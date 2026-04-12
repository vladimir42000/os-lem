"""Bounded local-refinement pass-1 support for the TQWT side-resonator probe.

This module implements only the small, auditable pieces needed by the bounded
local-refinement pass:
- seed extraction from the deterministic coarse-search surface
- bounded coordinate-search mechanics
- deterministic refinement classification

It intentionally does **not** introduce:
- a general optimizer framework
- mixed discrete/global search
- solver/API expansion
- topology-family growth
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Sequence

from os_lem.reference_tqwt_side_resonator_local_refinement_definition import (
    classify_gain,
    get_local_refinement_definition,
    select_refinement_seeds,
)
from os_lem.reference_tqwt_side_resonator_optimization_probe import (
    CandidateEvaluation,
    DEFAULT_BOUNDS,
    ProbeBounds,
    ProbeParameters,
    ResonatorType,
    ScoreBreakdown,
)


@dataclass(frozen=True)
class RefinementRuntimeConfig:
    coarse_seed: int = 2026
    coarse_sample_count: int = 96
    coarse_best_n: int = 5


@dataclass(frozen=True)
class RefinementPassResult:
    seed_label: str
    seed_params: ProbeParameters
    seed_score: float
    refined_label: str
    refined_params: ProbeParameters
    refined_score: float
    score_delta_db: float
    refinement_classification: str
    raw_gain_classification: str
    evaluations_used: int
    accepted_improvement_count: int
    remaining_global_budget_after_seed: int
    terminated_because: str
    geometry_valid: bool
    dominant_penalty_added: bool
    component_deltas: Mapping[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "seed_label": self.seed_label,
            "seed_params": probe_parameters_to_mapping(self.seed_params),
            "seed_score": self.seed_score,
            "refined_label": self.refined_label,
            "refined_params": probe_parameters_to_mapping(self.refined_params),
            "refined_score": self.refined_score,
            "score_delta_db": self.score_delta_db,
            "refinement_classification": self.refinement_classification,
            "raw_gain_classification": self.raw_gain_classification,
            "evaluations_used": self.evaluations_used,
            "accepted_improvement_count": self.accepted_improvement_count,
            "remaining_global_budget_after_seed": self.remaining_global_budget_after_seed,
            "terminated_because": self.terminated_because,
            "geometry_valid": self.geometry_valid,
            "dominant_penalty_added": self.dominant_penalty_added,
            "component_deltas": dict(self.component_deltas),
        }


DEFAULT_REFINEMENT_RUNTIME = RefinementRuntimeConfig()


def probe_parameters_from_mapping(mapping: Mapping[str, Any]) -> ProbeParameters:
    resonator_type = mapping["resonator_type"]
    if not isinstance(resonator_type, ResonatorType):
        resonator_type = ResonatorType(str(resonator_type))
    v_res = mapping.get("v_res_m3")
    return ProbeParameters(
        x_attach_norm=float(mapping["x_attach_norm"]),
        resonator_type=resonator_type,
        l_res_m=float(mapping["l_res_m"]),
        s_res_m2=float(mapping["s_res_m2"]),
        v_res_m3=None if v_res is None else float(v_res),
        driver_offset_norm=float(mapping.get("driver_offset_norm", 0.0)),
    )


def probe_parameters_to_mapping(params: ProbeParameters) -> dict[str, Any]:
    return {
        "x_attach_norm": params.x_attach_norm,
        "resonator_type": params.resonator_type.value,
        "l_res_m": params.l_res_m,
        "s_res_m2": params.s_res_m2,
        "v_res_m3": params.v_res_m3,
        "driver_offset_norm": params.driver_offset_norm,
    }


def parameter_identity(params: ProbeParameters) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), repr(v)) for k, v in probe_parameters_to_mapping(params).items()))


def extract_refinement_seeds_from_result_surface(result_surface: Mapping[str, Any]) -> list[ProbeParameters]:
    candidates = []
    for entry in result_surface.get("best_n", []):
        params = entry.get("params")
        if not isinstance(params, Mapping):
            continue
        candidates.append({
            "score": float(entry["score"]),
            "parameters": dict(params),
        })
    chosen = select_refinement_seeds(candidates)
    return [probe_parameters_from_mapping(candidate["parameters"]) for candidate in chosen]


def active_variable_names(params: ProbeParameters) -> tuple[str, ...]:
    if params.resonator_type == ResonatorType.SIDE_PIPE:
        return ("x_attach_norm", "l_res_m", "s_res_m2")
    return ("x_attach_norm", "l_res_m", "s_res_m2", "v_res_m3")


def _value_bounds(name: str, bounds: ProbeBounds = DEFAULT_BOUNDS) -> tuple[float, float]:
    mapping = {
        "x_attach_norm": (bounds.x_attach_norm_min, bounds.x_attach_norm_max),
        "l_res_m": (bounds.l_res_m_min, bounds.l_res_m_max),
        "s_res_m2": (bounds.s_res_m2_min, bounds.s_res_m2_max),
        "v_res_m3": (bounds.v_res_m3_min, bounds.v_res_m3_max),
    }
    return mapping[name]


def initial_step_sizes(params: ProbeParameters, bounds: ProbeBounds = DEFAULT_BOUNDS) -> dict[str, float]:
    definition = get_local_refinement_definition()
    out: dict[str, float] = {}
    for name in active_variable_names(params):
        lo, hi = _value_bounds(name, bounds)
        out[name] = (hi - lo) * definition.budget.initial_step_fraction
    return out


def minimum_step_sizes(params: ProbeParameters, bounds: ProbeBounds = DEFAULT_BOUNDS) -> dict[str, float]:
    definition = get_local_refinement_definition()
    out: dict[str, float] = {}
    for name in active_variable_names(params):
        lo, hi = _value_bounds(name, bounds)
        out[name] = (hi - lo) * definition.budget.min_step_fraction
    return out


def _clamp(name: str, value: float, bounds: ProbeBounds = DEFAULT_BOUNDS) -> float:
    lo, hi = _value_bounds(name, bounds)
    return max(lo, min(hi, value))


def replace_variable(params: ProbeParameters, name: str, value: float, bounds: ProbeBounds = DEFAULT_BOUNDS) -> ProbeParameters:
    value = _clamp(name, value, bounds)
    if name == "x_attach_norm":
        return ProbeParameters(
            x_attach_norm=value,
            resonator_type=params.resonator_type,
            l_res_m=params.l_res_m,
            s_res_m2=params.s_res_m2,
            v_res_m3=params.v_res_m3,
            driver_offset_norm=params.driver_offset_norm,
        )
    if name == "l_res_m":
        return ProbeParameters(
            x_attach_norm=params.x_attach_norm,
            resonator_type=params.resonator_type,
            l_res_m=value,
            s_res_m2=params.s_res_m2,
            v_res_m3=params.v_res_m3,
            driver_offset_norm=params.driver_offset_norm,
        )
    if name == "s_res_m2":
        return ProbeParameters(
            x_attach_norm=params.x_attach_norm,
            resonator_type=params.resonator_type,
            l_res_m=params.l_res_m,
            s_res_m2=value,
            v_res_m3=params.v_res_m3,
            driver_offset_norm=params.driver_offset_norm,
        )
    if name == "v_res_m3":
        if params.resonator_type != ResonatorType.CHAMBER_NECK:
            raise ValueError("v_res_m3 is not active for side_pipe")
        return ProbeParameters(
            x_attach_norm=params.x_attach_norm,
            resonator_type=params.resonator_type,
            l_res_m=params.l_res_m,
            s_res_m2=params.s_res_m2,
            v_res_m3=value,
            driver_offset_norm=params.driver_offset_norm,
        )
    raise KeyError(f"unsupported active variable: {name}")


def dominant_penalty_present(candidate: CandidateEvaluation) -> bool:
    penalties = [
        candidate.components.excursion_penalty,
        candidate.components.output_penalty,
        candidate.components.geometry_penalty,
    ]
    max_penalty = max(penalties)
    return max_penalty > 0.0 and max_penalty >= candidate.components.ripple_db


def refinement_component_deltas(seed: CandidateEvaluation, refined: CandidateEvaluation) -> dict[str, float]:
    return {
        "score_delta_db": refined.score - seed.score,
        "ripple_db_delta": refined.components.ripple_db - seed.components.ripple_db,
        "excursion_penalty_delta": refined.components.excursion_penalty - seed.components.excursion_penalty,
        "output_penalty_delta": refined.components.output_penalty - seed.components.output_penalty,
        "geometry_penalty_delta": refined.components.geometry_penalty - seed.components.geometry_penalty,
        "mean_spl_band_db_delta": refined.mean_spl_band_db - seed.mean_spl_band_db,
        "max_excursion_band_mm_delta": refined.max_excursion_band_mm - seed.max_excursion_band_mm,
    }


def classify_refinement_pass(seed: CandidateEvaluation, refined: CandidateEvaluation) -> tuple[str, str, bool]:
    dominant_added = dominant_penalty_present(refined) and not dominant_penalty_present(seed)
    raw = classify_gain(
        seed_score=seed.score,
        refined_score=refined.score,
        hard_geometry_failure=not refined.geometry_valid,
        dominant_penalty_added=dominant_added,
    )
    mapping = {
        "meaningful": "meaningful_gain",
        "marginal": "marginal_gain",
        "failure": "not_demonstrated",
        "not_demonstrated": "not_demonstrated",
    }
    return mapping[raw], raw, dominant_added



def coordinate_search_local_refinement(
    *,
    seed_eval: CandidateEvaluation,
    evaluate_fn: Callable[[ProbeParameters], CandidateEvaluation],
    global_budget_remaining: int,
    bounds: ProbeBounds = DEFAULT_BOUNDS,
) -> tuple[RefinementPassResult, int]:
    definition = get_local_refinement_definition()
    if seed_eval.params is None:
        raise ValueError("seed candidate must carry parameters")

    current = seed_eval
    steps = initial_step_sizes(seed_eval.params, bounds)
    min_steps = minimum_step_sizes(seed_eval.params, bounds)
    visited = {parameter_identity(seed_eval.params)}
    evaluations_used = 0
    accepted_improvement_count = 0
    per_seed_budget = definition.budget.max_evals_per_seed
    shrink_factor = definition.budget.step_shrink_factor
    terminated_because = "step_floor_reached"

    while True:
        if global_budget_remaining <= 0:
            terminated_because = "global_budget_exhausted"
            break
        if evaluations_used >= per_seed_budget:
            terminated_because = "per_seed_budget_exhausted"
            break
        if all(steps[name] < min_steps[name] for name in steps):
            terminated_because = "step_floor_reached"
            break

        improved = False
        for name in active_variable_names(current.params):
            base_value = getattr(current.params, name)
            assert base_value is not None
            for direction in (-1.0, 1.0):
                trial_value = _clamp(name, float(base_value) + direction * steps[name], bounds)
                if abs(trial_value - float(base_value)) < 1e-15:
                    continue
                trial_params = replace_variable(current.params, name, trial_value, bounds)
                ident = parameter_identity(trial_params)
                if ident in visited:
                    continue
                visited.add(ident)
                trial = evaluate_fn(trial_params)
                evaluations_used += 1
                global_budget_remaining -= 1
                if trial.score + 1e-12 < current.score:
                    current = trial
                    accepted_improvement_count += 1
                    improved = True
                    break
                if global_budget_remaining <= 0 or evaluations_used >= per_seed_budget:
                    break
            if improved or global_budget_remaining <= 0 or evaluations_used >= per_seed_budget:
                break
        if not improved:
            steps = {name: steps[name] * shrink_factor for name in steps}

    classification, raw_classification, dominant_added = classify_refinement_pass(seed_eval, current)
    result = RefinementPassResult(
        seed_label=seed_eval.label,
        seed_params=seed_eval.params,
        seed_score=seed_eval.score,
        refined_label=current.label,
        refined_params=current.params if current.params is not None else seed_eval.params,
        refined_score=current.score,
        score_delta_db=current.score - seed_eval.score,
        refinement_classification=classification,
        raw_gain_classification=raw_classification,
        evaluations_used=evaluations_used,
        accepted_improvement_count=accepted_improvement_count,
        remaining_global_budget_after_seed=global_budget_remaining,
        terminated_because=terminated_because,
        geometry_valid=current.geometry_valid,
        dominant_penalty_added=dominant_added,
        component_deltas=refinement_component_deltas(seed_eval, current),
    )
    return result, global_budget_remaining
