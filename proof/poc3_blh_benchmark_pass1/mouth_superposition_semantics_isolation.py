from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

from os_lem.reference_poc3_mouth_superposition_semantics import (
    CandidateScore,
    ResidualClassification,
    build_partition_semantic_candidates,
    classify_mouth_residual,
    mean_absolute_error_db,
    score_candidates,
)


BANDS_HZ = (
    ("low", 0.0, 200.0),
    ("mid", 200.0, 2000.0),
    ("high", 2000.0, 20000.000001),
)


@dataclass(frozen=True)
class Curve:
    label: str
    frequencies_hz: np.ndarray
    values: np.ndarray
    origin: str
    y_column: str


@dataclass(frozen=True)
class BandScore:
    label: str
    lo_hz: float
    hi_hz: float
    mae_db: float
    finite_points: int
    max_abs_delta_db: float


@dataclass(frozen=True)
class IsolationReport:
    root: str
    baseline_summary: Dict[str, object]
    discovered_tables: List[Dict[str, object]]
    hornresp_total_vs_oslem_total_mae_db: float
    hornresp_total_vs_akabak_total_mae_db: Optional[float]
    hornresp_mouth_candidate_scores: List[Dict[str, object]]
    hornresp_self_consistency_scores: List[Dict[str, object]]
    oslem_total_reconstruction_scores: List[Dict[str, object]]
    direct_mouth_band_scores: List[Dict[str, object]]
    classification: Dict[str, str]


def _read_key_value_file(path: Path) -> Dict[str, object]:
    out: Dict[str, object] = {}
    if not path.exists():
        return out
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        lowered = value.lower()
        if lowered in {"true", "false"}:
            out[key] = lowered == "true"
            continue
        try:
            out[key] = float(value)
            continue
        except ValueError:
            out[key] = value
    return out


def _read_tab_curve(path: Path, y_column: str) -> Curve:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
    if not rows:
        raise RuntimeError(f"No rows found in {path}")
    if "frequency_hz" not in reader.fieldnames:
        raise RuntimeError(f"frequency_hz column missing in {path}")
    if y_column not in reader.fieldnames:
        raise RuntimeError(f"{y_column} column missing in {path}")
    frequencies_hz = np.asarray([float(row["frequency_hz"]) for row in rows], dtype=float)
    values = np.asarray([float(row[y_column]) for row in rows], dtype=float)
    return Curve(
        label=path.stem,
        frequencies_hz=frequencies_hz,
        values=values,
        origin=str(path),
        y_column=y_column,
    )


def _curve_on_reference_grid(reference_freq_hz: np.ndarray, curve: Curve) -> np.ndarray:
    finite = np.isfinite(curve.frequencies_hz) & np.isfinite(curve.values)
    if np.count_nonzero(finite) < 2:
        return np.full_like(reference_freq_hz, np.nan, dtype=float)
    return np.interp(
        reference_freq_hz,
        curve.frequencies_hz[finite],
        curve.values[finite],
        left=np.nan,
        right=np.nan,
    )


def _table_info(curve: Curve) -> Dict[str, object]:
    return {
        "label": curve.label,
        "origin": curve.origin,
        "points": int(len(curve.frequencies_hz)),
        "y_column": curve.y_column,
        "f_min_hz": float(np.nanmin(curve.frequencies_hz)),
        "f_max_hz": float(np.nanmax(curve.frequencies_hz)),
    }


def _band_mae_scores(
    frequencies_hz: np.ndarray,
    reference_db: Iterable[float],
    candidate_db: Iterable[float],
    label: str,
) -> List[BandScore]:
    reference = np.asarray(list(reference_db), dtype=float)
    candidate = np.asarray(list(candidate_db), dtype=float)
    scores: List[BandScore] = []
    for band_label, lo_hz, hi_hz in BANDS_HZ:
        mask = (
            (frequencies_hz >= lo_hz)
            & (frequencies_hz < hi_hz)
            & np.isfinite(reference)
            & np.isfinite(candidate)
        )
        finite_points = int(np.count_nonzero(mask))
        if finite_points == 0:
            mae_db = float("inf")
            max_abs_delta_db = float("inf")
        else:
            delta = candidate[mask] - reference[mask]
            mae_db = float(np.mean(np.abs(delta)))
            max_abs_delta_db = float(np.max(np.abs(delta)))
        scores.append(
            BandScore(
                label=f"{label}:{band_label}",
                lo_hz=lo_hz,
                hi_hz=hi_hz,
                mae_db=mae_db,
                finite_points=finite_points,
                max_abs_delta_db=max_abs_delta_db,
            )
        )
    return scores


def build_report(root: Path) -> IsolationReport:
    comparison_dir = root / "comparison_outputs"

    hornresp_total = _read_tab_curve(
        comparison_dir / "hornresp_vs_oslem_total_spl_db.txt",
        "hornresp_total_spl_db",
    )
    hornresp_front = _read_tab_curve(
        comparison_dir / "hornresp_vs_oslem_front_spl_db.txt",
        "hornresp_front_spl_db",
    )
    hornresp_mouth = _read_tab_curve(
        comparison_dir / "hornresp_vs_oslem_mouth_spl_db.txt",
        "hornresp_mouth_spl_db",
    )
    oslem_total = _read_tab_curve(root / "oslem_spl_magnitude_db.txt", "oslem_total_spl_db")
    oslem_front = _read_tab_curve(root / "oslem_spl_front_db.txt", "oslem_front_spl_db")
    oslem_mouth = _read_tab_curve(root / "oslem_spl_mouth_db.txt", "oslem_mouth_spl_db")

    akabak_total_curve: Optional[Curve] = None
    akabak_total_path = comparison_dir / "akabak_vs_oslem_total_spl_db.txt"
    if akabak_total_path.exists():
        akabak_total_curve = _read_tab_curve(akabak_total_path, "akabak_total_spl_db")

    reference_freq_hz = hornresp_mouth.frequencies_hz
    hornresp_total_on_ref = _curve_on_reference_grid(reference_freq_hz, hornresp_total)
    hornresp_front_on_ref = _curve_on_reference_grid(reference_freq_hz, hornresp_front)
    hornresp_mouth_on_ref = hornresp_mouth.values
    oslem_total_on_ref = _curve_on_reference_grid(reference_freq_hz, oslem_total)
    oslem_front_on_ref = _curve_on_reference_grid(reference_freq_hz, oslem_front)
    oslem_mouth_on_ref = _curve_on_reference_grid(reference_freq_hz, oslem_mouth)

    hornresp_total_vs_oslem_total = mean_absolute_error_db(
        _curve_on_reference_grid(hornresp_total.frequencies_hz, hornresp_total),
        _curve_on_reference_grid(hornresp_total.frequencies_hz, oslem_total),
    )
    hornresp_total_vs_akabak_total_mae = None
    if akabak_total_curve is not None:
        hornresp_total_vs_akabak_total_mae = mean_absolute_error_db(
            _curve_on_reference_grid(hornresp_total.frequencies_hz, hornresp_total),
            _curve_on_reference_grid(hornresp_total.frequencies_hz, akabak_total_curve),
        ).mae_db

    oslem_candidates = build_partition_semantic_candidates(
        total_db=oslem_total_on_ref,
        front_db=oslem_front_on_ref,
        mouth_db=oslem_mouth_on_ref,
    )
    mouth_scores = score_candidates(
        reference_db=hornresp_mouth_on_ref,
        candidates={
            "oslem_direct_mouth": oslem_candidates["direct_mouth"],
            "oslem_implied_mouth_power": oslem_candidates["implied_mouth_power_from_total_minus_front"],
            "oslem_implied_mouth_amplitude": oslem_candidates["implied_mouth_amplitude_from_total_minus_front"],
        },
    )

    hornresp_self_candidates = build_partition_semantic_candidates(
        total_db=hornresp_total_on_ref,
        front_db=hornresp_front_on_ref,
        mouth_db=hornresp_mouth_on_ref,
    )
    hornresp_self_scores = score_candidates(
        reference_db=hornresp_mouth_on_ref,
        candidates={
            "hornresp_direct_mouth": hornresp_self_candidates["direct_mouth"],
            "hornresp_implied_mouth_power": hornresp_self_candidates["implied_mouth_power_from_total_minus_front"],
            "hornresp_implied_mouth_amplitude": hornresp_self_candidates["implied_mouth_amplitude_from_total_minus_front"],
        },
    )

    oslem_total_reconstruction_scores = score_candidates(
        reference_db=oslem_total.values,
        candidates={
            "oslem_reconstructed_total_power_from_front_plus_mouth": build_partition_semantic_candidates(
                total_db=oslem_total.values,
                front_db=oslem_front.values,
                mouth_db=oslem_mouth.values,
            )["reconstructed_total_power_from_front_plus_mouth"],
            "oslem_reconstructed_total_amplitude_from_front_plus_mouth": build_partition_semantic_candidates(
                total_db=oslem_total.values,
                front_db=oslem_front.values,
                mouth_db=oslem_mouth.values,
            )["reconstructed_total_amplitude_from_front_plus_mouth"],
        },
    )

    direct_mouth_band_scores = [
        asdict(score)
        for score in _band_mae_scores(
            frequencies_hz=reference_freq_hz,
            reference_db=hornresp_mouth_on_ref,
            candidate_db=oslem_mouth_on_ref,
            label="oslem_direct_mouth_vs_hornresp",
        )
    ]

    baseline_direct = next(score for score in mouth_scores if score.label == "oslem_direct_mouth")
    best_alternative = min(
        (score for score in mouth_scores if score.label != "oslem_direct_mouth"),
        key=lambda item: (item.mae_db, -item.finite_points, item.label),
        default=baseline_direct,
    )
    classification = classify_mouth_residual(
        baseline_mouth_mae_db=baseline_direct.mae_db,
        best_alternative_mae_db=best_alternative.mae_db,
        total_mae_db=hornresp_total_vs_oslem_total.mae_db,
        best_alternative_label=best_alternative.label,
    )

    baseline_summary = _read_key_value_file(root / "run_summary.txt")
    comparison_summary = _read_key_value_file(comparison_dir / "comparison_summary.txt")
    baseline_summary.update(comparison_summary)

    discovered_tables = [
        _table_info(curve)
        for curve in [
            hornresp_total,
            hornresp_front,
            hornresp_mouth,
            oslem_total,
            oslem_front,
            oslem_mouth,
        ]
    ]
    if akabak_total_curve is not None:
        discovered_tables.append(_table_info(akabak_total_curve))

    return IsolationReport(
        root=str(root),
        baseline_summary=baseline_summary,
        discovered_tables=discovered_tables,
        hornresp_total_vs_oslem_total_mae_db=hornresp_total_vs_oslem_total.mae_db,
        hornresp_total_vs_akabak_total_mae_db=hornresp_total_vs_akabak_total_mae,
        hornresp_mouth_candidate_scores=[asdict(score) for score in mouth_scores],
        hornresp_self_consistency_scores=[asdict(score) for score in hornresp_self_scores],
        oslem_total_reconstruction_scores=[asdict(score) for score in oslem_total_reconstruction_scores],
        direct_mouth_band_scores=direct_mouth_band_scores,
        classification=asdict(classification),
    )


def _format_scores(scores: List[Dict[str, object]]) -> str:
    return "\n".join(
        f"- {score['label']}: mae_db={float(score['mae_db']):.6f}, finite_points={int(score['finite_points'])}"
        for score in scores
    )


def _format_band_scores(scores: List[Dict[str, object]]) -> str:
    lines = []
    for score in scores:
        mae = float(score["mae_db"])
        max_abs = float(score["max_abs_delta_db"])
        finite_points = int(score["finite_points"])
        lines.append(
            f"- {score['label']}: range=[{float(score['lo_hz']):.0f}, {float(score['hi_hz']):.0f}) Hz, "
            f"mae_db={mae:.6f}, max_abs_delta_db={max_abs:.6f}, finite_points={finite_points}"
        )
    return "\n".join(lines)


def report_to_markdown(report: IsolationReport) -> str:
    lines = [
        "# POC3 mouth superposition semantics isolation",
        "",
        f"root: `{report.root}`",
        "",
        "## fixed benchmark baseline",
        "",
    ]

    for key in (
        "hornresp_total_spl_mae_db",
        "hornresp_front_spl_mae_db",
        "hornresp_mouth_spl_mae_db",
        "hornresp_impedance_mag_mae_ohm",
        "hornresp_impedance_phase_mae_deg",
        "hornresp_excursion_mae_mm",
        "akabak_total_spl_mae_db",
        "dominant_mismatch_classification",
        "classification_reason",
    ):
        if key in report.baseline_summary:
            lines.append(f"- {key} = {report.baseline_summary[key]}")

    lines.extend(["", "## loaded proof tables", ""])
    for table in report.discovered_tables:
        lines.append(
            f"- {table['label']}: points={table['points']}, y_column=`{table['y_column']}`, "
            f"range=[{table['f_min_hz']:.3f}, {table['f_max_hz']:.3f}] Hz, origin=`{table['origin']}`"
        )

    lines.extend(
        [
            "",
            "## hornresp mouth candidate ranking",
            "",
            _format_scores(report.hornresp_mouth_candidate_scores),
            "",
            "## hornresp self-consistency ranking",
            "",
            _format_scores(report.hornresp_self_consistency_scores),
            "",
            "## os-lem total reconstruction ranking",
            "",
            _format_scores(report.oslem_total_reconstruction_scores),
            "",
            "## direct mouth residual concentration",
            "",
            _format_band_scores(report.direct_mouth_band_scores),
            "",
            "## classification",
            "",
            f"- category = {report.classification['category']}",
            f"- interpretation = {report.classification['interpretation']}",
            "",
            "## reading discipline",
            "",
            "- The benchmark baseline stays fixed; this report only reinterprets already-exported total/front/mouth magnitude surfaces.",
            "- Direct mouth/front traces are compared against the committed Hornresp comparison tables, not guessed filenames or synthetic discovery rules.",
            "- Implied mouth candidates are phase-free magnitude reconstructions only; when total magnitude falls below front magnitude, the residual becomes non-finite and that is itself diagnostic.",
            "- A large reconstruction gap between front+mouth magnitudes and total magnitude indicates cancellation / superposition convention effects, not automatic proof of a solver failure.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default="proof/poc3_blh_benchmark_pass1",
        help="root directory containing the committed POC3 proof tables",
    )
    parser.add_argument("--output-json", default="", help="optional JSON report path")
    parser.add_argument("--output-markdown", default="", help="optional markdown report path")
    args = parser.parse_args()

    root = Path(args.root)
    report = build_report(root)
    rendered = report_to_markdown(report)
    print(rendered)

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    if args.output_markdown:
        Path(args.output_markdown).write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
