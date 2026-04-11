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
    rank_phase1_results,
    render_template_text,
    robustness_runtime_defaults,
    sample_phase1_candidates,
    summarize_ranked_run,
    summarize_repeatability_and_budget,
    validate_probe_parameters,
)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_template.yaml"
REPORT_JSON = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_repeatability_and_budget_sensitivity_report.json"
REPORT_MD = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_repeatability_and_budget_sensitivity_report.md"


def _parse_int_list(text: str) -> list[int]:
    items = [part.strip() for part in text.split(",") if part.strip()]
    if not items:
        raise argparse.ArgumentTypeError("list must not be empty")
    try:
        return [int(item) for item in items]
    except ValueError as exc:  # pragma: no cover - argparse path
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_args() -> argparse.Namespace:
    defaults = robustness_runtime_defaults()
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=_parse_int_list, default=list(defaults.seeds))
    parser.add_argument("--budgets", type=_parse_int_list, default=list(defaults.sample_budgets))
    parser.add_argument("--best-n", type=int, default=defaults.best_n)
    return parser.parse_args()


def _band_mean(frequencies_hz: np.ndarray, spl_db: np.ndarray) -> float:
    mask = (frequencies_hz >= DEFAULT_OBJECTIVE.band_hz_low) & (
        frequencies_hz <= DEFAULT_OBJECTIVE.band_hz_high
    )
    if not np.any(mask):
        raise ValueError("objective band is empty")
    return float(np.mean(spl_db[mask]))


def _evaluate_candidate(
    params: ProbeParameters,
    frequencies_hz: np.ndarray,
    baseline_mean_spl_band_db: float,
) -> CandidateEvaluation:
    label = (
        f"resonator_type={params.resonator_type.value};x_attach_norm={params.x_attach_norm:.4f};"
        f"l_res_m={params.l_res_m:.4f};s_res_m2={params.s_res_m2:.6f};"
        f"v_res_m3={params.v_res_m3 if params.v_res_m3 is not None else 'null'}"
    )
    validation_errors = validate_probe_parameters(params)
    if validation_errors:
        fallback = evaluate_candidate_from_series(
            label=label,
            params=params,
            frequencies_hz=frequencies_hz,
            spl_total_db=np.full_like(frequencies_hz, 0.0),
            excursion_mm=np.full_like(frequencies_hz, 0.0),
            baseline_mean_spl_band_db=baseline_mean_spl_band_db,
            geometry_valid=False,
        )
        return CandidateEvaluation(
            label=label,
            params=params,
            score=fallback.components.total_score,
            components=fallback.components,
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
        fallback = evaluate_candidate_from_series(
            label=label,
            params=params,
            frequencies_hz=frequencies_hz,
            spl_total_db=np.full_like(frequencies_hz, 0.0),
            excursion_mm=np.full_like(frequencies_hz, 0.0),
            baseline_mean_spl_band_db=baseline_mean_spl_band_db,
            geometry_valid=False,
        )
        return CandidateEvaluation(
            label=label,
            params=params,
            score=fallback.components.total_score,
            components=fallback.components,
            mean_spl_band_db=0.0,
            max_excursion_band_mm=0.0,
            geometry_valid=False,
            failure=str(exc),
        )


def _render_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# TQWT side resonator optimization probe repeatability and budget sensitivity")
    lines.append("")
    lines.append(f"root: `{ROOT}`")
    lines.append("")
    lines.append("## frozen definition reference plan")
    for key, value in phase1_execution_plan().items():
        lines.append(f"- {key} = {value}")
    lines.append("")
    lines.append("## bounded robustness runtime")
    for key, value in report["runtime"].items():
        lines.append(f"- {key} = {value}")
    lines.append("")
    lines.append("## baseline")
    baseline = report["baseline"]
    lines.append(f"- label = {baseline['label']}")
    lines.append(f"- score = {baseline['score']:.6f}")
    lines.append(f"- mean_spl_band_db = {baseline['mean_spl_band_db']:.6f}")
    lines.append(f"- max_excursion_band_mm = {baseline['max_excursion_band_mm']:.6f}")
    lines.append("")
    lines.append("## per-run best summaries")
    for run in report["runs"]:
        lines.append(
            "- "
            + f"budget={run['budget']}; seed={run['seed']}; best_score={run['best_score']:.6f}; "
            + f"best_score_improvement={run['best_score_improvement']:.6f}; "
            + f"best_resonator_type={run['best_resonator_type']}; "
            + f"best_attach_node={run['best_attach_node']}; "
            + f"best_region_label={run['best_region_label']}; "
            + f"best_penalty_free={run['best_penalty_free']}; "
            + f"successful_candidate_count={run['successful_candidate_count']}; "
            + f"failed_candidate_count={run['failed_candidate_count']}"
        )
    lines.append("")
    lines.append("## per-budget summary")
    for budget, entry in report["summary"]["per_budget"].items():
        lines.append(
            "- "
            + f"budget={budget}; run_count={entry['run_count']}; "
            + f"median_best_score={entry['median_best_score']:.6f}; "
            + f"median_improvement_vs_baseline={entry['median_improvement_vs_baseline']:.6f}; "
            + f"dominant_best_resonator_type={entry['dominant_best_resonator_type']}; "
            + f"dominant_best_region_family={entry['dominant_best_region_family']}; "
            + f"dominant_best_region_family_fraction={entry['dominant_best_region_family_fraction']:.6f}; "
            + f"all_candidates_successful={entry['all_candidates_successful']}"
        )
    lines.append("")
    lines.append("## assessment")
    assessment = report["summary"]["assessment"]
    lines.append(f"- category = {assessment['category']}")
    lines.append(f"- region_broadly_stable = {assessment['region_broadly_stable']}")
    lines.append(f"- budget_improvement_delta = {assessment['budget_improvement_delta']:.6f}")
    lines.append(f"- interpretation = {assessment['interpretation']}")
    lines.append("")
    lines.append("## reading discipline")
    lines.append("- The frozen TQWT probe definition and landed phase-1 search method remain fixed; this script only classifies bounded rerun repeatability and modest budget sensitivity above that baseline.")
    lines.append("- Lower score is better: ripple_db + excursion_penalty + output_penalty + geometry_penalty.")
    lines.append("- The compared budgets stay proof-sized and fixed-seed; this is not a phase-2 refinement or a general optimizer study.")
    lines.append("- Generated JSON/Markdown outputs remain local proof byproducts unless later curated into repo truth.")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = _parse_args()
    runtime_defaults = phase1_runtime_defaults()
    frequencies_hz = fixed_phase1_frequencies_hz(runtime_defaults)

    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered_probe_yaml = render_template_text(
        template_text,
        ProbeParameters(
            x_attach_norm=0.50,
            resonator_type=ResonatorType.SIDE_PIPE,
            l_res_m=0.20,
            s_res_m2=1.0e-3,
        ),
    )
    yaml.safe_load(rendered_probe_yaml)

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

    run_summaries = []
    per_run_rankings = []
    for budget in args.budgets:
        for seed in args.seeds:
            sampled = sample_phase1_candidates(budget, seed)
            candidate_evaluations = [
                _evaluate_candidate(candidate, frequencies_hz, baseline_mean)
                for candidate in sampled
            ]
            result_surface = rank_phase1_results(baseline_eval, candidate_evaluations, args.best_n)
            run_summaries.append(summarize_ranked_run(result_surface, budget=budget, seed=seed))
            per_run_rankings.append(
                {
                    "budget": budget,
                    "seed": seed,
                    "result_surface": result_surface,
                }
            )

    summary = summarize_repeatability_and_budget(run_summaries)
    report = {
        "template_path": str(TEMPLATE_PATH.relative_to(ROOT)),
        "definition_reference_plan": phase1_execution_plan(),
        "runtime": {
            "search_mode": runtime_defaults.search_mode,
            "seeds": args.seeds,
            "sample_budgets": args.budgets,
            "best_n": args.best_n,
            "frequency_start_hz": runtime_defaults.frequency_start_hz,
            "frequency_stop_hz": runtime_defaults.frequency_stop_hz,
            "frequency_count": runtime_defaults.frequency_count,
        },
        "baseline": baseline_eval.as_dict(),
        "runs": [run.as_dict() for run in run_summaries],
        "run_rankings": per_run_rankings,
        "summary": summary,
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(_render_report(report), encoding="utf-8")
    print(_render_report(report))


if __name__ == "__main__":
    main()
