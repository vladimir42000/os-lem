"""Bounded local-refinement definition for the TQWT side-resonator probe.

This module is definition-only. It does not implement refinement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence


@dataclass(frozen=True)
class RefinementBudget:
    max_evals_per_seed: int = 48
    max_total_evals: int = 144
    initial_step_fraction: float = 0.10
    min_step_fraction: float = 0.01
    step_shrink_factor: float = 0.5


@dataclass(frozen=True)
class SeedSelectionRule:
    max_seed_count: int = 3
    selection_mode: str = "best_score_only"
    deduplication_mode: str = "exact_parameter_identity"


@dataclass(frozen=True)
class MeaningfulGainRule:
    min_score_improvement_db: float = 0.50
    require_no_new_hard_geometry_failure: bool = True
    require_no_new_dominant_penalty: bool = True


@dataclass(frozen=True)
class LocalRefinementDefinition:
    method_name: str
    discrete_variable_policy: str
    allowed_global_variables: Sequence[str]
    side_pipe_active_variables: Sequence[str]
    chamber_neck_active_variables: Sequence[str]
    budget: RefinementBudget
    seed_selection: SeedSelectionRule
    meaningful_gain_rule: MeaningfulGainRule


def get_local_refinement_definition() -> LocalRefinementDefinition:
    return LocalRefinementDefinition(
        method_name="bounded_coordinate_search",
        discrete_variable_policy="resonator_type_fixed_per_seed",
        allowed_global_variables=(
            "x_attach",
            "resonator_type",
            "L_res_or_L_pipe",
            "S_res_or_S_neck",
            "V_res_if_chamber_neck",
            "driver_offset_optional_if_already_frozen",
        ),
        side_pipe_active_variables=(
            "x_attach",
            "L_pipe",
            "S_res",
            "driver_offset_optional_if_already_frozen",
        ),
        chamber_neck_active_variables=(
            "x_attach",
            "L_res",
            "S_res",
            "V_res",
            "driver_offset_optional_if_already_frozen",
        ),
        budget=RefinementBudget(),
        seed_selection=SeedSelectionRule(),
        meaningful_gain_rule=MeaningfulGainRule(),
    )


def select_refinement_seeds(candidates: Sequence[Mapping[str, object]]) -> List[Mapping[str, object]]:
    """Select up to 3 seeds by best score after exact parameter-identity deduplication.

    Expected candidate fields:
    - score: float
    - parameters: mapping
    """
    definition = get_local_refinement_definition()
    sorted_candidates = sorted(candidates, key=lambda item: float(item["score"]))
    seen = set()
    chosen: List[Mapping[str, object]] = []
    for candidate in sorted_candidates:
        params = candidate["parameters"]
        if not isinstance(params, Mapping):
            raise TypeError("candidate parameters must be a mapping")
        identity = tuple(sorted((str(k), repr(v)) for k, v in params.items()))
        if identity in seen:
            continue
        seen.add(identity)
        chosen.append(candidate)
        if len(chosen) >= definition.seed_selection.max_seed_count:
            break
    return chosen


def classify_gain(*, seed_score: float, refined_score: float, hard_geometry_failure: bool, dominant_penalty_added: bool) -> str:
    """Classify the usefulness of a later refinement result."""
    definition = get_local_refinement_definition()
    delta = refined_score - seed_score
    if hard_geometry_failure and definition.meaningful_gain_rule.require_no_new_hard_geometry_failure:
        return "failure"
    if dominant_penalty_added and definition.meaningful_gain_rule.require_no_new_dominant_penalty:
        return "failure"
    if delta <= -definition.meaningful_gain_rule.min_score_improvement_db:
        return "meaningful"
    if delta < 0.0:
        return "marginal"
    return "not_demonstrated"


def render_definition_summary() -> Dict[str, object]:
    definition = get_local_refinement_definition()
    return {
        "method_name": definition.method_name,
        "discrete_variable_policy": definition.discrete_variable_policy,
        "max_seed_count": definition.seed_selection.max_seed_count,
        "selection_mode": definition.seed_selection.selection_mode,
        "deduplication_mode": definition.seed_selection.deduplication_mode,
        "max_evals_per_seed": definition.budget.max_evals_per_seed,
        "max_total_evals": definition.budget.max_total_evals,
        "initial_step_fraction": definition.budget.initial_step_fraction,
        "min_step_fraction": definition.budget.min_step_fraction,
        "step_shrink_factor": definition.budget.step_shrink_factor,
        "meaningful_gain_threshold_db": definition.meaningful_gain_rule.min_score_improvement_db,
    }
