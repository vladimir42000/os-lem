from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional

import numpy as np

from os_lem.api import run_simulation
from os_lem.reference_tqwt_side_resonator_local_refinement_definition import (
    get_local_refinement_definition,
    render_definition_summary,
)
from os_lem.reference_tqwt_side_resonator_local_refinement_pass1 import (
    DEFAULT_REFINEMENT_RUNTIME,
    coordinate_search_local_refinement,
    extract_refinement_seeds_from_result_surface,
    parameter_identity,
    probe_parameters_from_mapping,
)
from os_lem.reference_tqwt_side_resonator_optimization_probe import (
    DEFAULT_OBJECTIVE,
    CandidateEvaluation,
    ProbeParameters,
    baseline_offset_tap_model_dict,
    build_candidate_model_dict,
    evaluate_candidate_from_series,
    fixed_phase1_frequencies_hz,
    phase1_runtime_defaults,
    rank_phase1_results,
    sample_phase1_candidates,
)

ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_bounded_local_refinement_pass1_report.json"
REPORT_MD = ROOT / "proof" / "tqwt_side_resonator_optimization_probe_bounded_local_refinement_pass1_report.md"


def _band_mean(frequencies_hz: np.ndarray, spl_db: np.ndarray) -> float:
    mask = (frequencies_hz >= DEFAULT_OBJECTIVE.band_hz_low) & (
        frequencies_hz <= DEFAULT_OBJECTIVE.band_hz_high
    )
    if not np.any(mask):
        raise ValueError("objective band is empty")
    return float(np.mean(spl_db[mask]))


def _label_for_params(params: ProbeParameters) -> str:
    return (
        f"resonator_type={params.resonator_type.value};x_attach_norm={params.x_attach_norm:.4f};"
        f"l_res_m={params.l_res_m:.4f};s_res_m2={params.s_res_m2:.6f};"
        f"v_res_m3={params.v_res_m3 if params.v_res_m3 is not None else 'null'}"
    )


def _evaluate_candidate(params: ProbeParameters, frequencies_hz: np.ndarray, baseline_mean_spl_band_db: float) -> CandidateEvaluation:
    label = _label_for_params(params)
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


def _evaluate_baseline(frequencies_hz: np.ndarray) -> tuple[CandidateEvaluation, float]:
    model_dict = baseline_offset_tap_model_dict()
    result = run_simulation(model_dict, frequencies_hz)
    spl_total = np.asarray(result.series["spl_total"], dtype=float)
    excursion_mm = np.asarray(result.cone_excursion_mm, dtype=float)
    baseline_mean = _band_mean(frequencies_hz, spl_total)
    baseline = evaluate_candidate_from_series(
        label="baseline_no_resonator",
        params=None,
        frequencies_hz=frequencies_hz,
        spl_total_db=spl_total,
        excursion_mm=excursion_mm,
        baseline_mean_spl_band_db=baseline_mean,
        geometry_valid=True,
    )
    return baseline, baseline_mean


def _classify_overall(results: list[dict[str, Any]]) -> str:
    classes = [entry["refinement_classification"] for entry in results]
    if "meaningful_gain" in classes:
        return "meaningful_gain"
    if "marginal_gain" in classes:
        return "marginal_gain"
    return "not_demonstrated"


def build_report() -> dict[str, Any]:
    phase1_runtime = phase1_runtime_defaults()
    refinement_runtime = DEFAULT_REFINEMENT_RUNTIME
    refinement_definition = get_local_refinement_definition()
    frequencies_hz = fixed_phase1_frequencies_hz()

    baseline_eval, baseline_mean_spl_band_db = _evaluate_baseline(frequencies_hz)

    coarse_candidates = [
        _evaluate_candidate(params, frequencies_hz, baseline_mean_spl_band_db)
        for params in sample_phase1_candidates(
            sample_count=refinement_runtime.coarse_sample_count,
            seed=refinement_runtime.coarse_seed,
        )
    ]
    coarse_surface = rank_phase1_results(
        baseline=baseline_eval,
        candidates=coarse_candidates,
        best_n=refinement_runtime.coarse_best_n,
    )
    coarse_map = {
        parameter_identity(candidate.params): candidate
        for candidate in coarse_candidates
        if candidate.params is not None and candidate.failure is None
    }

    seed_params = extract_refinement_seeds_from_result_surface(coarse_surface)
    global_budget_remaining = refinement_definition.budget.max_total_evals
    per_seed_results = []
    for params in seed_params:
        seed_eval = coarse_map[parameter_identity(params)]
        result, global_budget_remaining = coordinate_search_local_refinement(
            seed_eval=seed_eval,
            evaluate_fn=lambda trial_params: _evaluate_candidate(
                trial_params,
                frequencies_hz,
                baseline_mean_spl_band_db,
            ),
            global_budget_remaining=global_budget_remaining,
        )
        per_seed_results.append(result.as_dict())

    best_refined: Optional[dict[str, Any]] = None
    if per_seed_results:
        best_refined = min(per_seed_results, key=lambda item: (float(item["refined_score"]), item["refined_label"]))

    report = {
        "fixed_probe_boundary": {
            "family": "tqwt_offset_tl_conical_no_fill_fixed_driver",
            "fill": "none",
            "driver_fixed": True,
            "max_side_resonators": 1,
            "coarse_surface_seed": refinement_runtime.coarse_seed,
            "coarse_surface_sample_count": refinement_runtime.coarse_sample_count,
            "coarse_surface_best_n": refinement_runtime.coarse_best_n,
            "local_method": refinement_definition.method_name,
            "discrete_variable_policy": refinement_definition.discrete_variable_policy,
        },
        "baseline": baseline_eval.as_dict(),
        "coarse_surface": {
            "baseline": coarse_surface["baseline"],
            "best_n": coarse_surface["best_n"],
            "candidate_count": coarse_surface["candidate_count"],
            "successful_candidate_count": coarse_surface["successful_candidate_count"],
            "failed_candidate_count": coarse_surface["failed_candidate_count"],
        },
        "refinement_contract": render_definition_summary(),
        "selected_seed_count": len(seed_params),
        "selected_seed_labels": [_label_for_params(params) for params in seed_params],
        "per_seed_results": per_seed_results,
        "overall_assessment": {
            "classification": _classify_overall(per_seed_results),
            "best_refined_label": None if best_refined is None else best_refined["refined_label"],
            "best_refined_score": None if best_refined is None else best_refined["refined_score"],
            "best_seed_label": None if best_refined is None else best_refined["seed_label"],
            "best_score_delta_db": None if best_refined is None else best_refined["score_delta_db"],
            "refinement_budget_used": refinement_definition.budget.max_total_evals - global_budget_remaining,
            "refinement_budget_remaining": global_budget_remaining,
            "question_answered": (
                "bounded local refinement on top of the robust coarse-search seeds yields "
                + _classify_overall(per_seed_results)
                + " additional gain under the frozen contract"
            ),
        },
        "reading_discipline": [
            "This pass reuses the landed phase-1 coarse-search surface as the seed source; it does not reopen the global search problem.",
            "resonator_type stays fixed per seed during refinement.",
            "Generated JSON/Markdown outputs remain local-only proof byproducts unless later curated explicitly.",
        ],
    }
    return report


def _render_markdown(report: Mapping[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# TQWT side-resonator bounded local refinement pass 1")
    lines.append("")
    lines.append("## fixed probe boundary")
    for k, v in report["fixed_probe_boundary"].items():
        lines.append(f"- {k} = {v}")
    lines.append("")
    lines.append("## selected seeds")
    for label in report["selected_seed_labels"]:
        lines.append(f"- {label}")
    lines.append("")
    lines.append("## per-seed refinement results")
    for entry in report["per_seed_results"]:
        lines.append(
            "- "
            + f"seed={entry['seed_label']}: refined={entry['refined_label']}, "
            + f"classification={entry['refinement_classification']}, "
            + f"score_delta_db={entry['score_delta_db']:.6f}, "
            + f"evaluations_used={entry['evaluations_used']}, "
            + f"terminated_because={entry['terminated_because']}"
        )
    lines.append("")
    lines.append("## overall assessment")
    for k, v in report["overall_assessment"].items():
        lines.append(f"- {k} = {v}")
    lines.append("")
    lines.append("## reading discipline")
    for line in report["reading_discipline"]:
        lines.append(f"- {line}")
    return "\n".join(lines) + "\n"


def main() -> None:
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True))
    REPORT_MD.write_text(_render_markdown(report))
    print(f"Wrote {REPORT_JSON}")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
