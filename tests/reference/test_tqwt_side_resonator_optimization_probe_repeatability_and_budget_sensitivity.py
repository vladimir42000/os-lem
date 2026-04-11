from __future__ import annotations

from os_lem.reference_tqwt_side_resonator_optimization_probe import (
    CandidateEvaluation,
    ProbeParameters,
    ResonatorType,
    RobustnessRunSummary,
    ScoreBreakdown,
    candidate_region_family,
    candidate_region_label,
    robustness_runtime_defaults,
    summarize_ranked_run,
    summarize_repeatability_and_budget,
)


def test_candidate_region_helpers_are_deterministic_and_bounded() -> None:
    params = ProbeParameters(
        x_attach_norm=0.70,
        resonator_type=ResonatorType.CHAMBER_NECK,
        l_res_m=0.42,
        s_res_m2=2.2e-3,
        v_res_m3=4.5e-3,
    )
    assert candidate_region_family(params) == "type=chamber_neck;attach=merge"
    assert candidate_region_label(params) == (
        "type=chamber_neck;attach=merge;length=medium;area=mid;volume=medium"
    )


def test_summarize_ranked_run_extracts_best_region_and_penalty_state() -> None:
    result_surface = {
        "baseline": {"label": "baseline_no_resonator", "score": 9.0},
        "best_n": [
            {
                "label": "best",
                "score": 6.0,
                "params": {
                    "x_attach_norm": 0.70,
                    "resonator_type": "chamber_neck",
                    "l_res_m": 0.42,
                    "s_res_m2": 2.2e-3,
                    "v_res_m3": 4.5e-3,
                    "driver_offset_norm": 0.0,
                },
                "components": {
                    "ripple_db": 6.0,
                    "excursion_penalty": 0.0,
                    "output_penalty": 0.0,
                    "geometry_penalty": 0.0,
                },
            }
        ],
        "candidate_count": 8,
        "successful_candidate_count": 8,
        "failed_candidate_count": 0,
    }
    summary = summarize_ranked_run(result_surface, budget=96, seed=2026)
    assert summary.best_resonator_type == "chamber_neck"
    assert summary.best_attach_node == "merge"
    assert summary.best_penalty_free is True
    assert summary.best_score_improvement == 3.0


def test_summarize_repeatability_and_budget_reports_stable_region_with_material_gain() -> None:
    runs = [
        RobustnessRunSummary(96, 2026, 9.0, 6.8, 2.2, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=small", True, 96, 96, 0),
        RobustnessRunSummary(96, 2027, 9.0, 6.6, 2.4, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=medium", True, 96, 96, 0),
        RobustnessRunSummary(96, 2028, 9.0, 6.7, 2.3, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=medium", True, 96, 96, 0),
        RobustnessRunSummary(144, 2026, 9.0, 5.5, 3.5, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=small", True, 144, 144, 0),
        RobustnessRunSummary(144, 2027, 9.0, 5.3, 3.7, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=medium", True, 144, 144, 0),
        RobustnessRunSummary(144, 2028, 9.0, 5.4, 3.6, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=medium", True, 144, 144, 0),
    ]
    summary = summarize_repeatability_and_budget(runs)
    assert summary["assessment"]["category"] == "broadly_stable_with_material_budget_improvement"
    assert summary["assessment"]["region_broadly_stable"] is True
    assert summary["per_budget"]["96"]["dominant_best_resonator_type"] == "chamber_neck"
    assert summary["per_budget"]["144"]["all_candidates_successful"] is True


def test_summarize_repeatability_and_budget_reports_mixed_when_best_region_shifts() -> None:
    runs = [
        RobustnessRunSummary(96, 2026, 9.0, 6.8, 2.2, "side_pipe", "split", "type=side_pipe;attach=split;length=short;area=narrow;volume=na", True, 96, 96, 0),
        RobustnessRunSummary(96, 2027, 9.0, 6.6, 2.4, "side_pipe", "split", "type=side_pipe;attach=split;length=medium;area=mid;volume=na", True, 96, 96, 0),
        RobustnessRunSummary(96, 2028, 9.0, 6.7, 2.3, "side_pipe", "split", "type=side_pipe;attach=split;length=medium;area=mid;volume=na", True, 96, 96, 0),
        RobustnessRunSummary(144, 2026, 9.0, 5.5, 3.5, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=small", True, 144, 144, 0),
        RobustnessRunSummary(144, 2027, 9.0, 5.3, 3.7, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=medium", True, 144, 144, 0),
        RobustnessRunSummary(144, 2028, 9.0, 5.4, 3.6, "chamber_neck", "merge", "type=chamber_neck;attach=merge;length=medium;area=mid;volume=medium", True, 144, 144, 0),
    ]
    summary = summarize_repeatability_and_budget(runs)
    assert summary["assessment"]["category"] == "mixed_or_budget_sensitive"
    assert summary["assessment"]["region_broadly_stable"] is False


def test_robustness_runtime_defaults_stay_small_and_explicit() -> None:
    runtime = robustness_runtime_defaults()
    assert runtime.seeds == (2026, 2027, 2028)
    assert runtime.sample_budgets == (96, 144)
    assert runtime.best_n == 3
