from __future__ import annotations

from os_lem.reference_tqwt_side_resonator_local_refinement_pass1 import (
    active_variable_names,
    classify_refinement_pass,
    coordinate_search_local_refinement,
    extract_refinement_seeds_from_result_surface,
)
from os_lem.reference_tqwt_side_resonator_optimization_probe import (
    CandidateEvaluation,
    ProbeParameters,
    ResonatorType,
    ScoreBreakdown,
)


def _candidate(label: str, score: float, params: ProbeParameters, *, ripple: float | None = None, geometry_valid: bool = True) -> CandidateEvaluation:
    ripple = score if ripple is None else ripple
    return CandidateEvaluation(
        label=label,
        params=params,
        score=score,
        components=ScoreBreakdown(
            ripple_db=ripple,
            excursion_penalty=0.0,
            output_penalty=0.0,
            geometry_penalty=0.0 if geometry_valid else 1_000_000.0,
        ),
        mean_spl_band_db=90.0,
        max_excursion_band_mm=2.0,
        geometry_valid=geometry_valid,
        failure=None if geometry_valid else "invalid geometry",
    )


def test_extract_refinement_seeds_obeys_best_score_and_exact_dedup() -> None:
    result_surface = {
        "best_n": [
            {"score": 6.0, "params": {"x_attach_norm": 0.7, "resonator_type": "chamber_neck", "l_res_m": 0.4, "s_res_m2": 0.002, "v_res_m3": 0.004, "driver_offset_norm": 0.0}},
            {"score": 6.1, "params": {"x_attach_norm": 0.7, "resonator_type": "chamber_neck", "l_res_m": 0.4, "s_res_m2": 0.002, "v_res_m3": 0.004, "driver_offset_norm": 0.0}},
            {"score": 6.2, "params": {"x_attach_norm": 0.3, "resonator_type": "side_pipe", "l_res_m": 0.2, "s_res_m2": 0.0015, "v_res_m3": None, "driver_offset_norm": 0.0}},
            {"score": 6.3, "params": {"x_attach_norm": 0.5, "resonator_type": "chamber_neck", "l_res_m": 0.7, "s_res_m2": 0.0025, "v_res_m3": 0.006, "driver_offset_norm": 0.0}},
            {"score": 6.4, "params": {"x_attach_norm": 0.2, "resonator_type": "side_pipe", "l_res_m": 0.8, "s_res_m2": 0.0035, "v_res_m3": None, "driver_offset_norm": 0.0}},
        ]
    }
    seeds = extract_refinement_seeds_from_result_surface(result_surface)
    assert len(seeds) == 3
    assert seeds[0].resonator_type == ResonatorType.CHAMBER_NECK
    assert seeds[1].resonator_type == ResonatorType.SIDE_PIPE
    assert seeds[2].x_attach_norm == 0.5


def test_active_variable_names_keep_resonator_type_fixed() -> None:
    side = ProbeParameters(0.3, ResonatorType.SIDE_PIPE, 0.2, 0.0015, None)
    chamber = ProbeParameters(0.7, ResonatorType.CHAMBER_NECK, 0.4, 0.002, 0.004)
    assert active_variable_names(side) == ("x_attach_norm", "l_res_m", "s_res_m2")
    assert active_variable_names(chamber) == ("x_attach_norm", "l_res_m", "s_res_m2", "v_res_m3")


def test_coordinate_search_honors_budget_and_keeps_resonator_type_fixed() -> None:
    seed = ProbeParameters(0.30, ResonatorType.SIDE_PIPE, 0.20, 0.0015, None)
    seed_eval = _candidate("seed", 10.0, seed)

    def evaluate_fn(params: ProbeParameters) -> CandidateEvaluation:
        # deterministic convex bowl with optimum near x=0.55, l=0.45, s=0.0025
        score = (
            5.0
            + (params.x_attach_norm - 0.55) ** 2 * 10.0
            + (params.l_res_m - 0.45) ** 2 * 4.0
            + (params.s_res_m2 - 0.0025) ** 2 * 50000.0
        )
        assert params.resonator_type == ResonatorType.SIDE_PIPE
        return _candidate("trial", score, params)

    result, remaining = coordinate_search_local_refinement(
        seed_eval=seed_eval,
        evaluate_fn=evaluate_fn,
        global_budget_remaining=20,
    )
    assert result.refined_params.resonator_type == ResonatorType.SIDE_PIPE
    assert result.evaluations_used <= 20
    assert remaining >= 0
    assert result.refined_score < result.seed_score


def test_classify_refinement_pass_is_deterministic() -> None:
    params = ProbeParameters(0.7, ResonatorType.CHAMBER_NECK, 0.4, 0.002, 0.004)
    seed = _candidate("seed", 8.0, params)
    refined_meaningful = _candidate("refined", 7.2, params)
    refined_marginal = _candidate("refined2", 7.7, params)
    refined_none = _candidate("refined3", 8.1, params)

    assert classify_refinement_pass(seed, refined_meaningful)[0] == "meaningful_gain"
    assert classify_refinement_pass(seed, refined_marginal)[0] == "marginal_gain"
    assert classify_refinement_pass(seed, refined_none)[0] == "not_demonstrated"
