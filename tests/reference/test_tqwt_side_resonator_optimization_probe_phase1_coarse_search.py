from __future__ import annotations

from os_lem.reference_tqwt_side_resonator_optimization_probe import (
    CandidateEvaluation,
    Phase1RuntimeConfig,
    ProbeParameters,
    ResonatorType,
    ScoreBreakdown,
    baseline_offset_tap_model_dict,
    fixed_phase1_frequencies_hz,
    nearest_main_line_boundary_node,
    phase1_runtime_defaults,
    rank_phase1_results,
    sample_phase1_candidates,
)


def test_phase1_runtime_defaults_are_bounded_and_repeatable() -> None:
    runtime = phase1_runtime_defaults()
    assert runtime == Phase1RuntimeConfig(
        search_mode="random_uniform",
        random_seed=2026,
        sample_count=96,
        best_n=5,
        frequency_start_hz=20.0,
        frequency_stop_hz=500.0,
        frequency_count=96,
    )


def test_sample_phase1_candidates_is_repeatable_under_fixed_seed() -> None:
    first = sample_phase1_candidates(sample_count=4, seed=2026)
    second = sample_phase1_candidates(sample_count=4, seed=2026)
    assert first == second
    assert first[0].resonator_type == ResonatorType.SIDE_PIPE
    assert first[1].resonator_type == ResonatorType.CHAMBER_NECK


def test_nearest_main_line_boundary_node_uses_frozen_boundary_policy() -> None:
    assert nearest_main_line_boundary_node(0.20) == "split"
    assert nearest_main_line_boundary_node(0.52) == "merge"
    assert nearest_main_line_boundary_node(0.92) == "mouth"


def test_rank_phase1_results_keeps_baseline_and_orders_candidates() -> None:
    baseline = CandidateEvaluation(
        label="baseline_no_resonator",
        params=None,
        score=8.0,
        components=ScoreBreakdown(8.0, 0.0, 0.0, 0.0),
        mean_spl_band_db=84.0,
        max_excursion_band_mm=2.0,
        geometry_valid=True,
    )
    candidates = [
        CandidateEvaluation(
            label="c2",
            params=ProbeParameters(0.4, ResonatorType.SIDE_PIPE, 0.2, 1.0e-3),
            score=9.0,
            components=ScoreBreakdown(9.0, 0.0, 0.0, 0.0),
            mean_spl_band_db=83.5,
            max_excursion_band_mm=2.1,
            geometry_valid=True,
        ),
        CandidateEvaluation(
            label="c1",
            params=ProbeParameters(0.5, ResonatorType.CHAMBER_NECK, 0.3, 1.2e-3, 2.5e-3),
            score=7.0,
            components=ScoreBreakdown(7.0, 0.0, 0.0, 0.0),
            mean_spl_band_db=84.2,
            max_excursion_band_mm=2.2,
            geometry_valid=True,
        ),
    ]
    ranked = rank_phase1_results(baseline, candidates, best_n=1)
    assert ranked["baseline"]["label"] == "baseline_no_resonator"
    assert ranked["best_n"][0]["label"] == "c1"
    assert ranked["candidate_count"] == 2
    assert ranked["successful_candidate_count"] == 2
    assert ranked["failed_candidate_count"] == 0


def test_baseline_offset_tap_model_dict_exposes_required_outputs() -> None:
    model = baseline_offset_tap_model_dict()
    observation_ids = {obs["id"] for obs in model["observations"]}
    assert {"zin", "xcone", "spl_total"}.issubset(observation_ids)


def test_fixed_phase1_frequencies_are_monotone_and_bounded() -> None:
    frequencies = fixed_phase1_frequencies_hz()
    assert len(frequencies) == 96
    assert frequencies[0] == 20.0
    assert frequencies[-1] == 500.0
    assert all(b > a for a, b in zip(frequencies[:-1], frequencies[1:]))
