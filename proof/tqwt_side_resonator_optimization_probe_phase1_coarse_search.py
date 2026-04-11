from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from os_lem.api import run_simulation
from os_lem.reference_tqwt_side_resonator_optimization_probe import (
    DEFAULT_OBJECTIVE,
    CandidateEvaluation,
    ProbeParameters,
    ResonatorType,
    baseline_offset_tap_model_dict,
    build_candidate_model_dict,
    evaluate_candidate_from_series,
    fixed_phase1_frequencies_hz,
    phase1_execution_plan,
    phase1_runtime_defaults,
    probe_parameters_to_dict,
    rank_phase1_results,
    render_template_text,
    sample_phase1_candidates,
    validate_probe_parameters,
)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_template.yaml"
REPORT_JSON = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_phase1_coarse_search_report.json"
REPORT_MD = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_phase1_coarse_search_report.md"


def _parse_args() -> argparse.Namespace:
    defaults = phase1_runtime_defaults()
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-count", type=int, default=defaults.sample_count)
    parser.add_argument("--seed", type=int, default=defaults.random_seed)
    parser.add_argument("--best-n", type=int, default=defaults.best_n)
    return parser.parse_args()


def _band_mean(frequencies_hz: np.ndarray, spl_db: np.ndarray) -> float:
    mask = (frequencies_hz >= DEFAULT_OBJECTIVE.band_hz_low) & (
        frequencies_hz <= DEFAULT_OBJECTIVE.band_hz_high
    )
    if not np.any(mask):
        raise ValueError("objective band is empty")
    return float(np.mean(spl_db[mask]))


def _evaluate_model(label: str, model_dict: dict[str, Any], frequencies_hz: np.ndarray, baseline_mean_spl_band_db: float) -> CandidateEvaluation:
    result = run_simulation(model_dict, frequencies_hz)
    spl_total = np.asarray(result.series["spl_total"], dtype=float)
    excursion_mm = np.asarray(result.cone_excursion_mm, dtype=float)
    return evaluate_candidate_from_series(
        label=label,
        params=None,
        frequencies_hz=frequencies_hz,
        spl_total_db=spl_total,
        excursion_mm=excursion_mm,
        baseline_mean_spl_band_db=baseline_mean_spl_band_db,
        geometry_valid=True,
    )


def _evaluate_candidate(params: ProbeParameters, frequencies_hz: np.ndarray, baseline_mean_spl_band_db: float) -> CandidateEvaluation:
    label = (
        f"resonator_type={params.resonator_type.value};x_attach_norm={params.x_attach_norm:.4f};"
        f"l_res_m={params.l_res_m:.4f};s_res_m2={params.s_res_m2:.6f};"
        f"v_res_m3={params.v_res_m3 if params.v_res_m3 is not None else 'null'}"
    )
    validation_errors = validate_probe_parameters(params)
    if validation_errors:
        return CandidateEvaluation(
            label=label,
            params=params,
            score=DEFAULT_OBJECTIVE.invalid_geometry_penalty,
            components=evaluate_candidate_from_series(
                label=label,
                params=params,
                frequencies_hz=frequencies_hz,
                spl_total_db=np.full_like(frequencies_hz, 0.0),
                excursion_mm=np.full_like(frequencies_hz, 0.0),
                baseline_mean_spl_band_db=baseline_mean_spl_band_db,
                geometry_valid=False,
            ).components,
            mean_spl_band_db=0.0,
            max_excursion_band_mm=0.0,
            geometry_valid=False,
            failure="; ".join(validation_errors),
        )

    try:
        model_dict = build_candidate_model_dict(params)
        result = run_simulation(model_dict, frequencies_hz)
        spl_total = np.asarray(result.series["spl_total"], dtype=float)
        excursion_mm = np.asarray(result.cone_excursion_mm, dtype=float)
        return evaluate_candidate_from_series(
            label=label,
            params=params,
            frequencies_hz=frequencies_hz,
            spl_total_db=spl_total,
            excursion_mm=excursion_mm,
            baseline_mean_spl_band_db=baseline_mean_spl_band_db,
            geometry_valid=True,
        )
    except Exception as exc:  # pragma: no cover - exercised in live repo execution
        return CandidateEvaluation(
            label=label,
            params=params,
            score=DEFAULT_OBJECTIVE.invalid_geometry_penalty,
            components=evaluate_candidate_from_series(
                label=label,
                params=params,
                frequencies_hz=frequencies_hz,
                spl_total_db=np.full_like(frequencies_hz, 0.0),
                excursion_mm=np.full_like(frequencies_hz, 0.0),
                baseline_mean_spl_band_db=baseline_mean_spl_band_db,
                geometry_valid=False,
            ).components,
            mean_spl_band_db=0.0,
            max_excursion_band_mm=0.0,
            geometry_valid=False,
            failure=str(exc),
        )


def _render_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# TQWT side resonator optimization probe phase-1 coarse search")
    lines.append("")
    lines.append(f"root: `{ROOT}`")
    lines.append("")
    lines.append("## frozen definition reference plan")
    for key, value in phase1_execution_plan().items():
        lines.append(f"- {key} = {value}")
    lines.append("")
    lines.append("## actual runtime plan")
    for key, value in report["runtime"].items():
        lines.append(f"- {key} = {value}")
    lines.append("")
    lines.append("## baseline entry")
    baseline = report["result_surface"]["baseline"]
    lines.append(f"- label = {baseline['label']}")
    lines.append(f"- score = {baseline['score']:.6f}")
    for key, value in baseline["components"].items():
        lines.append(f"- baseline_{key} = {value:.6f}")
    lines.append(f"- baseline_mean_spl_band_db = {baseline['mean_spl_band_db']:.6f}")
    lines.append(f"- baseline_max_excursion_band_mm = {baseline['max_excursion_band_mm']:.6f}")
    lines.append("")
    lines.append("## ranked best_n")
    for entry in report["result_surface"]["best_n"]:
        lines.append(
            "- "
            + f"label={entry['label']}; score={entry['score']:.6f}; "
            + f"ripple_db={entry['components']['ripple_db']:.6f}; "
            + f"excursion_penalty={entry['components']['excursion_penalty']:.6f}; "
            + f"output_penalty={entry['components']['output_penalty']:.6f}; "
            + f"geometry_penalty={entry['components']['geometry_penalty']:.6f}; "
            + f"mean_spl_band_db={entry['mean_spl_band_db']:.6f}; "
            + f"max_excursion_band_mm={entry['max_excursion_band_mm']:.6f}"
        )
    lines.append("")
    lines.append("## result counts")
    for key in ["candidate_count", "successful_candidate_count", "failed_candidate_count"]:
        lines.append(f"- {key} = {report['result_surface'][key]}")
    lines.append("")
    lines.append("## reading discipline")
    lines.append("- The accepted TQWT probe definition remains fixed; this script only executes the frozen phase-1 coarse search boundary.")
    lines.append("- The runtime sample count is intentionally bounded for repeatable proof work and is reported explicitly above; the frozen definition reference plan remains recorded separately.")
    lines.append("- Lower score is better: ripple_db + excursion_penalty + output_penalty + geometry_penalty.")
    lines.append("- Generated JSON/Markdown outputs remain local proof byproducts unless later curated into repo truth.")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = _parse_args()
    runtime_defaults = phase1_runtime_defaults()
    frequencies_hz = fixed_phase1_frequencies_hz(runtime_defaults)

    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered_baseline_yaml = render_template_text(
        template_text,
        ProbeParameters(
            x_attach_norm=0.50,
            resonator_type=ResonatorType.SIDE_PIPE,
            l_res_m=0.20,
            s_res_m2=1.0e-3,
        ),
    )
    yaml.safe_load(rendered_baseline_yaml)

    baseline_model = baseline_offset_tap_model_dict()
    baseline_result = run_simulation(baseline_model, frequencies_hz)
    baseline_spl = np.asarray(baseline_result.series["spl_total"], dtype=float)
    baseline_excursion = np.asarray(baseline_result.cone_excursion_mm, dtype=float)
    baseline_mean = _band_mean(frequencies_hz, baseline_spl)
    baseline_eval = evaluate_candidate_from_series(
        label="baseline_no_resonator",
        params=None,
        frequencies_hz=frequencies_hz,
        spl_total_db=baseline_spl,
        excursion_mm=baseline_excursion,
        baseline_mean_spl_band_db=baseline_mean,
        geometry_valid=True,
    )

    sampled = sample_phase1_candidates(args.sample_count, args.seed)
    candidate_evaluations = [
        _evaluate_candidate(candidate, frequencies_hz, baseline_mean) for candidate in sampled
    ]
    result_surface = rank_phase1_results(baseline_eval, candidate_evaluations, args.best_n)

    best_yaml_snippets = []
    for entry in result_surface["best_n"]:
        params_dict = entry.get("params")
        if params_dict is None:
            continue
        params = ProbeParameters(
            x_attach_norm=float(params_dict["x_attach_norm"]),
            resonator_type=ResonatorType(params_dict["resonator_type"]),
            l_res_m=float(params_dict["l_res_m"]),
            s_res_m2=float(params_dict["s_res_m2"]),
            v_res_m3=None if params_dict["v_res_m3"] is None else float(params_dict["v_res_m3"]),
            driver_offset_norm=float(params_dict.get("driver_offset_norm", 0.0)),
        )
        best_yaml_snippets.append({
            "label": entry["label"],
            "rendered_yaml": render_template_text(template_text, params),
        })

    report = {
        "template_path": str(TEMPLATE_PATH.relative_to(ROOT)),
        "definition_reference_plan": phase1_execution_plan(),
        "runtime": {
            "search_mode": runtime_defaults.search_mode,
            "random_seed": args.seed,
            "sample_count": args.sample_count,
            "best_n": args.best_n,
            "frequency_start_hz": runtime_defaults.frequency_start_hz,
            "frequency_stop_hz": runtime_defaults.frequency_stop_hz,
            "frequency_count": runtime_defaults.frequency_count,
        },
        "result_surface": result_surface,
        "best_yaml_snippets": best_yaml_snippets,
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(_render_report(report), encoding="utf-8")
    print(_render_report(report))


if __name__ == "__main__":
    main()
