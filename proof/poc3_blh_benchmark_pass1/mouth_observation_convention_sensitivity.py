from __future__ import annotations

import argparse
import copy
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from os_lem.api import run_simulation  # noqa: E402
from os_lem.reference_poc3_mouth_observation_convention import (  # noqa: E402
    BandScore,
    ConventionSensitivityAssessment,
    ConventionVariantScore,
    assess_convention_sensitivity,
    band_scores,
    mean_absolute_error_db,
    rank_variant_scores,
)


BENCH_DIR = Path(__file__).resolve().parent
COMPARE_DIR = BENCH_DIR / "comparison_outputs"
MODEL_PATH = BENCH_DIR / "model.yaml"
SUMMARY_PATH = COMPARE_DIR / "comparison_summary.txt"

REPORT_JSON = BENCH_DIR / "mouth_observation_convention_sensitivity_report.json"
REPORT_MD = BENCH_DIR / "mouth_observation_convention_sensitivity_report.md"

SUPPORTED_MOUTH_MODELS: tuple[str, ...] = (
    "infinite_baffle_piston",
    "flanged_piston",
    "unflanged_piston",
)
SUPPORTED_MOUTH_CONTRACTS: tuple[str, ...] = (
    "raw",
    "mouth_directivity_only",
)


@dataclass(frozen=True)
class ReferenceCurve:
    frequencies_hz: np.ndarray
    values_db: np.ndarray
    value_column: str
    origin: str


@dataclass(frozen=True)
class VariantResult:
    score: ConventionVariantScore
    mouth_bands: list[BandScore]


@dataclass(frozen=True)
class ConventionSensitivityReport:
    root: str
    baseline_summary: dict[str, Any]
    supported_mouth_models: list[str]
    supported_mouth_contracts: list[str]
    fixed_radiation_space: str
    fixed_front_radiator_model: str
    reference_tables: dict[str, dict[str, Any]]
    ranked_variants: list[dict[str, Any]]
    best_variant_band_breakdown: list[dict[str, Any]]
    assessment: dict[str, Any]
    reading_discipline: list[str]


def _load_model(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"expected YAML mapping in {path}")
    return data


def _load_summary(path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key == "poc3_blh_benchmark_pass1_comparison_summary":
            continue
        try:
            summary[key] = float(value)
            continue
        except ValueError:
            pass
        summary[key] = value
    return summary


def _load_tab_curve(path: Path, value_column: str) -> ReferenceCurve:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
    if not rows:
        raise RuntimeError(f"no numeric rows found in {path}")
    freq = np.asarray([float(row["frequency_hz"]) for row in rows], dtype=float)
    values = np.asarray([float(row[value_column]) for row in rows], dtype=float)
    return ReferenceCurve(frequencies_hz=freq, values_db=values, value_column=value_column, origin=str(path))


def _curve_dict(curve: ReferenceCurve) -> dict[str, Any]:
    return {
        "points": int(curve.frequencies_hz.size),
        "value_column": curve.value_column,
        "origin": curve.origin,
        "range_hz": [float(np.min(curve.frequencies_hz)), float(np.max(curve.frequencies_hz))],
    }


def _interp(reference_freq_hz: np.ndarray, candidate_freq_hz: np.ndarray, candidate_values_db: np.ndarray) -> np.ndarray:
    finite = np.isfinite(candidate_freq_hz) & np.isfinite(candidate_values_db)
    if np.count_nonzero(finite) < 2:
        return np.full_like(reference_freq_hz, np.nan, dtype=float)
    return np.interp(reference_freq_hz, candidate_freq_hz[finite], candidate_values_db[finite], left=np.nan, right=np.nan)


def _variant_label(mouth_model: str, mouth_contract: str) -> str:
    return f"mouth_model={mouth_model}; mouth_contract={mouth_contract}"


def _build_variant_model(base_model: Mapping[str, Any], *, mouth_model: str, mouth_contract: str) -> dict[str, Any]:
    model = copy.deepcopy(base_model)
    elements = model.get("elements", [])
    if not isinstance(elements, list):
        raise TypeError("model elements must be a list")

    for element in elements:
        if not isinstance(element, dict):
            continue
        if element.get("id") == "mouth_rad":
            element["model"] = mouth_model

    observations: list[dict[str, Any]] = []
    observations.append(
        {
            "id": "spl_front_fixed",
            "type": "spl",
            "target": "front_rad",
            "distance": "1 m",
            "radiation_space": "2pi",
        }
    )
    mouth_obs: dict[str, Any] = {
        "id": "spl_mouth_variant",
        "type": "spl",
        "target": "mouth_rad",
        "distance": "1 m",
        "radiation_space": "2pi",
    }
    total_terms: list[dict[str, Any]] = [
        {
            "target": "front_rad",
            "distance": "1 m",
            "radiation_space": "2pi",
        },
        {
            "target": "mouth_rad",
            "distance": "1 m",
            "radiation_space": "2pi",
        },
    ]
    if mouth_contract != "raw":
        mouth_obs["observable_contract"] = mouth_contract
        total_terms[1]["observable_contract"] = mouth_contract
    observations.append(mouth_obs)
    observations.append(
        {
            "id": "spl_total_variant",
            "type": "spl_sum",
            "radiation_space": "2pi",
            "terms": total_terms,
        }
    )
    model["observations"] = observations
    if not isinstance(model.get("meta"), dict):
        model["meta"] = {}
    model["meta"]["radiation_space"] = "2pi"
    return model


def _evaluate_variants(base_model: dict[str, Any], compare_dir: Path) -> tuple[str, list[VariantResult]]:
    total_ref = _load_tab_curve(compare_dir / "hornresp_vs_oslem_total_spl_db.txt", "hornresp_total_spl_db")
    front_ref = _load_tab_curve(compare_dir / "hornresp_vs_oslem_front_spl_db.txt", "hornresp_front_spl_db")
    mouth_ref = _load_tab_curve(compare_dir / "hornresp_vs_oslem_mouth_spl_db.txt", "hornresp_mouth_spl_db")
    akabak_total_ref = _load_tab_curve(compare_dir / "akabak_vs_oslem_total_spl_db.txt", "akabak_total_spl_db")

    front_model = ""
    for element in base_model.get("elements", []):
        if isinstance(element, dict) and element.get("id") == "front_rad":
            front_model = str(element.get("model"))
            break

    variants: list[VariantResult] = []
    frequencies_hz = total_ref.frequencies_hz
    for mouth_model in SUPPORTED_MOUTH_MODELS:
        for mouth_contract in SUPPORTED_MOUTH_CONTRACTS:
            variant_model = _build_variant_model(base_model, mouth_model=mouth_model, mouth_contract=mouth_contract)
            result = run_simulation(variant_model, frequencies_hz)

            total_variant = np.asarray(result.series["spl_total_variant"], dtype=float)
            mouth_variant = np.asarray(result.series["spl_mouth_variant"], dtype=float)
            front_variant = np.asarray(result.series["spl_front_fixed"], dtype=float)

            mouth_on_ref = _interp(mouth_ref.frequencies_hz, frequencies_hz, mouth_variant)
            total_on_ref = _interp(total_ref.frequencies_hz, frequencies_hz, total_variant)
            front_on_ref = _interp(front_ref.frequencies_hz, frequencies_hz, front_variant)
            total_on_akabak = _interp(akabak_total_ref.frequencies_hz, frequencies_hz, total_variant)

            mouth_mae_db, _ = mean_absolute_error_db(mouth_ref.values_db, mouth_on_ref)
            total_mae_db, _ = mean_absolute_error_db(total_ref.values_db, total_on_ref)
            front_mae_db, _ = mean_absolute_error_db(front_ref.values_db, front_on_ref)
            akabak_total_mae_db, _ = mean_absolute_error_db(akabak_total_ref.values_db, total_on_akabak)

            mouth_band_scores = band_scores(
                mouth_ref.frequencies_hz,
                mouth_ref.values_db,
                mouth_on_ref,
                label_prefix=_variant_label(mouth_model, mouth_contract),
            )
            high_band = next(score for score in mouth_band_scores if score.label.endswith(":high"))
            variants.append(
                VariantResult(
                    score=ConventionVariantScore(
                        label=_variant_label(mouth_model, mouth_contract),
                        mouth_model=mouth_model,
                        mouth_contract=mouth_contract,
                        hornresp_mouth_mae_db=mouth_mae_db,
                        hornresp_total_mae_db=total_mae_db,
                        hornresp_front_mae_db=front_mae_db,
                        akabak_total_mae_db=akabak_total_mae_db,
                        high_band_mouth_mae_db=high_band.mae_db,
                    ),
                    mouth_bands=mouth_band_scores,
                )
            )

    return front_model, variants


def build_report(root: Path) -> ConventionSensitivityReport:
    compare_dir = root / "comparison_outputs"
    model = _load_model(root / "model.yaml")
    baseline_summary = _load_summary(compare_dir / "comparison_summary.txt")

    total_ref = _load_tab_curve(compare_dir / "hornresp_vs_oslem_total_spl_db.txt", "hornresp_total_spl_db")
    front_ref = _load_tab_curve(compare_dir / "hornresp_vs_oslem_front_spl_db.txt", "hornresp_front_spl_db")
    mouth_ref = _load_tab_curve(compare_dir / "hornresp_vs_oslem_mouth_spl_db.txt", "hornresp_mouth_spl_db")
    akabak_total_ref = _load_tab_curve(compare_dir / "akabak_vs_oslem_total_spl_db.txt", "akabak_total_spl_db")

    front_model, variant_results = _evaluate_variants(model, compare_dir)
    ranked_scores = rank_variant_scores([item.score for item in variant_results])
    ranked_lookup = {item.score.label: item for item in variant_results}
    best_variant = ranked_lookup[ranked_scores[0].label]

    assessment = assess_convention_sensitivity(
        baseline_mouth_mae_db=float(baseline_summary["hornresp_mouth_spl_mae_db"]),
        baseline_total_mae_db=float(baseline_summary["hornresp_total_spl_mae_db"]),
        ranked_scores=ranked_scores,
    )

    return ConventionSensitivityReport(
        root=str(root),
        baseline_summary=baseline_summary,
        supported_mouth_models=list(SUPPORTED_MOUTH_MODELS),
        supported_mouth_contracts=list(SUPPORTED_MOUTH_CONTRACTS),
        fixed_radiation_space="2pi",
        fixed_front_radiator_model=front_model,
        reference_tables={
            "hornresp_total_spl_db": _curve_dict(total_ref),
            "hornresp_front_spl_db": _curve_dict(front_ref),
            "hornresp_mouth_spl_db": _curve_dict(mouth_ref),
            "akabak_total_spl_db": _curve_dict(akabak_total_ref),
        },
        ranked_variants=[asdict(score) for score in ranked_scores],
        best_variant_band_breakdown=[asdict(score) for score in best_variant.mouth_bands],
        assessment=asdict(assessment),
        reading_discipline=[
            "The accepted POC3 baseline remains fixed; this harness does not redefine the default benchmark model or interpretation.",
            "The sweep stays inside current supported repo-resident mouth convention space: supported mouth radiator models plus the optional mouth_directivity_only observation contract.",
            "Radiation space stays fixed at 2pi to preserve the frozen benchmark protocol and avoid mixed-space total-sum comparisons becoming the dominant variable.",
            "Generated JSON/Markdown outputs are local proof byproducts; durable repo truth lives in the committed proof code and any later curated documentation note.",
        ],
    )


def _report_to_markdown(report: ConventionSensitivityReport) -> str:
    lines: list[str] = []
    lines.append("# POC3 mouth observation/convention sensitivity")
    lines.append("")
    lines.append(f"root: `{report.root}`")
    lines.append("")
    lines.append("## fixed baseline")
    lines.append("")
    for key in [
        "hornresp_total_spl_mae_db",
        "hornresp_front_spl_mae_db",
        "hornresp_mouth_spl_mae_db",
        "hornresp_impedance_mag_mae_ohm",
        "hornresp_impedance_phase_mae_deg",
        "hornresp_excursion_mae_mm",
        "akabak_total_spl_mae_db",
        "dominant_mismatch_classification",
    ]:
        if key in report.baseline_summary:
            lines.append(f"- {key} = {report.baseline_summary[key]}")
    lines.append("")
    lines.append("## sweep boundary")
    lines.append("")
    lines.append(f"- fixed_radiation_space = {report.fixed_radiation_space}")
    lines.append(f"- fixed_front_radiator_model = {report.fixed_front_radiator_model}")
    lines.append(f"- supported_mouth_models = {', '.join(report.supported_mouth_models)}")
    lines.append(f"- supported_mouth_contracts = {', '.join(report.supported_mouth_contracts)}")
    lines.append("")
    lines.append("## ranked variants")
    lines.append("")
    for score in report.ranked_variants:
        lines.append(
            "- "
            f"{score['label']}: "
            f"hornresp_mouth_mae_db={score['hornresp_mouth_mae_db']:.6f}, "
            f"hornresp_total_mae_db={score['hornresp_total_mae_db']:.6f}, "
            f"hornresp_front_mae_db={score['hornresp_front_mae_db']:.6f}, "
            f"high_band_mouth_mae_db={score['high_band_mouth_mae_db']:.6f}, "
            f"akabak_total_mae_db={score['akabak_total_mae_db']:.6f}"
        )
    lines.append("")
    lines.append("## best variant band breakdown")
    lines.append("")
    for band in report.best_variant_band_breakdown:
        lines.append(
            "- "
            f"{band['label']}: range=[{band['f_min_hz']:.0f}, {band['f_max_hz']:.0f}) Hz, "
            f"mae_db={band['mae_db']:.6f}, max_abs_delta_db={band['max_abs_delta_db']:.6f}, "
            f"finite_points={band['finite_points']}"
        )
    lines.append("")
    lines.append("## assessment")
    lines.append("")
    for key, value in report.assessment.items():
        lines.append(f"- {key} = {value}")
    lines.append("")
    lines.append("## reading discipline")
    lines.append("")
    for entry in report.reading_discipline:
        lines.append(f"- {entry}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate POC3 mouth observation/convention sensitivity")
    parser.add_argument("--root", type=Path, default=BENCH_DIR)
    args = parser.parse_args()

    report = build_report(args.root)
    report_json = args.root / "mouth_observation_convention_sensitivity_report.json"
    report_md = args.root / "mouth_observation_convention_sensitivity_report.md"
    report_json.write_text(json.dumps(asdict(report), indent=2) + "\n", encoding="utf-8")
    report_md.write_text(_report_to_markdown(report), encoding="utf-8")
    print(report_md.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
