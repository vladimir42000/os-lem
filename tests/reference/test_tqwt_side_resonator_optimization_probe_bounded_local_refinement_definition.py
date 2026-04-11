from __future__ import annotations

from os_lem.reference_tqwt_side_resonator_local_refinement_definition import (
    classify_gain,
    get_local_refinement_definition,
    render_definition_summary,
    select_refinement_seeds,
)


def test_definition_is_bounded_and_interpretable() -> None:
    definition = get_local_refinement_definition()
    assert definition.method_name == "bounded_coordinate_search"
    assert definition.discrete_variable_policy == "resonator_type_fixed_per_seed"
    assert definition.seed_selection.max_seed_count == 3
    assert definition.budget.max_evals_per_seed == 48
    assert definition.budget.max_total_evals == 144
    assert definition.budget.initial_step_fraction == 0.10
    assert definition.budget.min_step_fraction == 0.01
    assert definition.budget.step_shrink_factor == 0.5


def test_seed_selection_is_best_score_only_with_exact_deduplication() -> None:
    candidates = [
        {"score": 4.0, "parameters": {"x_attach": 0.2, "resonator_type": "chamber_neck"}},
        {"score": 3.0, "parameters": {"x_attach": 0.3, "resonator_type": "chamber_neck"}},
        {"score": 2.0, "parameters": {"x_attach": 0.1, "resonator_type": "side_pipe"}},
        {"score": 1.5, "parameters": {"x_attach": 0.1, "resonator_type": "side_pipe"}},
        {"score": 2.5, "parameters": {"x_attach": 0.4, "resonator_type": "chamber_neck"}},
    ]
    seeds = select_refinement_seeds(candidates)
    assert len(seeds) == 3
    assert float(seeds[0]["score"]) == 1.5
    assert float(seeds[1]["score"]) == 2.5
    assert float(seeds[2]["score"]) == 3.0


def test_gain_classification_is_disciplined() -> None:
    assert classify_gain(seed_score=10.0, refined_score=9.3, hard_geometry_failure=False, dominant_penalty_added=False) == "meaningful"
    assert classify_gain(seed_score=10.0, refined_score=9.8, hard_geometry_failure=False, dominant_penalty_added=False) == "marginal"
    assert classify_gain(seed_score=10.0, refined_score=10.1, hard_geometry_failure=False, dominant_penalty_added=False) == "not_demonstrated"
    assert classify_gain(seed_score=10.0, refined_score=8.0, hard_geometry_failure=True, dominant_penalty_added=False) == "failure"
    assert classify_gain(seed_score=10.0, refined_score=8.0, hard_geometry_failure=False, dominant_penalty_added=True) == "failure"


def test_summary_is_stable() -> None:
    summary = render_definition_summary()
    assert summary["method_name"] == "bounded_coordinate_search"
    assert summary["max_seed_count"] == 3
    assert summary["max_evals_per_seed"] == 48
    assert summary["max_total_evals"] == 144
    assert summary["meaningful_gain_threshold_db"] == 0.50
