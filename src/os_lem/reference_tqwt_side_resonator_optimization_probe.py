"""Bounded reference scaffolding for the v0.6 TQWT side-resonator optimization probe.

This module is intentionally small and definition-oriented. It does not implement a
full optimizer. It freezes:
- the active parameter set
- explicit hard bounds
- YAML rendering contract
- score math for a future implementation
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional, Sequence


class ResonatorType(str, Enum):
    SIDE_PIPE = "side_pipe"
    CHAMBER_NECK = "chamber_neck"


@dataclass(frozen=True)
class ProbeBounds:
    x_attach_norm_min: float = 0.15
    x_attach_norm_max: float = 0.85
    l_res_m_min: float = 0.05
    l_res_m_max: float = 1.20
    s_res_m2_min: float = 1.0e-4
    s_res_m2_max: float = 6.0e-3
    v_res_m3_min: float = 2.0e-4
    v_res_m3_max: float = 2.0e-2


@dataclass(frozen=True)
class ObjectiveConfig:
    band_hz_low: float = 40.0
    band_hz_high: float = 250.0
    smoothing_window_bins: int = 5
    excursion_limit_mm: float = 4.0
    allowed_mean_drop_db: float = 1.5
    excursion_penalty_weight: float = 6.0
    output_penalty_weight: float = 3.0
    invalid_geometry_penalty: float = 1_000_000.0


@dataclass(frozen=True)
class ProbeParameters:
    x_attach_norm: float
    resonator_type: ResonatorType
    l_res_m: float
    s_res_m2: float
    v_res_m3: Optional[float] = None
    driver_offset_norm: float = 0.0


@dataclass(frozen=True)
class ScoreBreakdown:
    ripple_db: float
    excursion_penalty: float
    output_penalty: float
    geometry_penalty: float

    @property
    def total_score(self) -> float:
        return (
            self.ripple_db
            + self.excursion_penalty
            + self.output_penalty
            + self.geometry_penalty
        )


DEFAULT_BOUNDS = ProbeBounds()
DEFAULT_OBJECTIVE = ObjectiveConfig()


def validate_probe_parameters(
    params: ProbeParameters,
    bounds: ProbeBounds = DEFAULT_BOUNDS,
) -> List[str]:
    errors: List[str] = []

    if not (bounds.x_attach_norm_min <= params.x_attach_norm <= bounds.x_attach_norm_max):
        errors.append(
            f"x_attach_norm out of bounds: {params.x_attach_norm} not in "
            f"[{bounds.x_attach_norm_min}, {bounds.x_attach_norm_max}]"
        )

    if not (bounds.l_res_m_min <= params.l_res_m <= bounds.l_res_m_max):
        errors.append(
            f"l_res_m out of bounds: {params.l_res_m} not in "
            f"[{bounds.l_res_m_min}, {bounds.l_res_m_max}]"
        )

    if not (bounds.s_res_m2_min <= params.s_res_m2 <= bounds.s_res_m2_max):
        errors.append(
            f"s_res_m2 out of bounds: {params.s_res_m2} not in "
            f"[{bounds.s_res_m2_min}, {bounds.s_res_m2_max}]"
        )

    if params.driver_offset_norm != 0.0:
        errors.append("driver_offset_norm must remain 0.0 in phase-1 probe definition")

    if params.resonator_type == ResonatorType.CHAMBER_NECK:
        if params.v_res_m3 is None:
            errors.append("v_res_m3 is required for resonator_type='chamber_neck'")
        elif not (bounds.v_res_m3_min <= params.v_res_m3 <= bounds.v_res_m3_max):
            errors.append(
                f"v_res_m3 out of bounds: {params.v_res_m3} not in "
                f"[{bounds.v_res_m3_min}, {bounds.v_res_m3_max}]"
            )
    elif params.resonator_type == ResonatorType.SIDE_PIPE:
        if params.v_res_m3 not in (None, 0.0):
            errors.append("v_res_m3 must be None or 0.0 for resonator_type='side_pipe'")

    return errors


def centered_moving_average(values: Sequence[float], window: int) -> List[float]:
    if window <= 0:
        raise ValueError("window must be positive")
    if not values:
        return []
    if window == 1:
        return list(values)

    radius = window // 2
    out: List[float] = []
    n = len(values)
    for i in range(n):
        lo = max(0, i - radius)
        hi = min(n, i + radius + 1)
        segment = values[lo:hi]
        out.append(sum(segment) / len(segment))
    return out


def compute_probe_score(
    spl_band_db: Sequence[float],
    excursion_band_mm: Sequence[float],
    baseline_mean_spl_band_db: float,
    geometry_is_valid: bool,
    objective: ObjectiveConfig = DEFAULT_OBJECTIVE,
) -> ScoreBreakdown:
    if not spl_band_db:
        raise ValueError("spl_band_db must not be empty")
    if not excursion_band_mm:
        raise ValueError("excursion_band_mm must not be empty")

    smoothed = centered_moving_average(spl_band_db, objective.smoothing_window_bins)
    ripple_db = max(smoothed) - min(smoothed)

    x_peak_mm = max(excursion_band_mm)
    if x_peak_mm <= objective.excursion_limit_mm:
        excursion_penalty = 0.0
    else:
        excursion_penalty = objective.excursion_penalty_weight * (
            x_peak_mm - objective.excursion_limit_mm
        )

    mean_spl_band_db = sum(smoothed) / len(smoothed)
    mean_drop_db = baseline_mean_spl_band_db - mean_spl_band_db
    if mean_drop_db <= objective.allowed_mean_drop_db:
        output_penalty = 0.0
    else:
        output_penalty = objective.output_penalty_weight * (
            mean_drop_db - objective.allowed_mean_drop_db
        )

    geometry_penalty = 0.0 if geometry_is_valid else objective.invalid_geometry_penalty

    return ScoreBreakdown(
        ripple_db=ripple_db,
        excursion_penalty=excursion_penalty,
        output_penalty=output_penalty,
        geometry_penalty=geometry_penalty,
    )


def render_probe_yaml(params: ProbeParameters) -> str:
    v_res_text = "null" if params.v_res_m3 is None else f"{params.v_res_m3:.6g}"
    return f"""probe:
  name: tqwt_side_resonator_optimization_probe
  milestone: v0.6.0
  family: tqwt_offset_tl_conical_no_fill_fixed_driver
  purpose: bounded engineering probe definition
  execution_mode: definition_only

baseline:
  reference_model_id: tqwt_offset_tl_conical_no_fill_fixed_driver
  geometry_is_frozen: true
  fill: none
  driver_is_fixed: true
  driver_offset_norm: 0.0

parameters:
  x_attach_norm: {params.x_attach_norm:.6g}
  resonator_type: {params.resonator_type.value}
  L_res_m: {params.l_res_m:.6g}
  S_res_m2: {params.s_res_m2:.6g}
  V_res_m3: {v_res_text}
"""


def phase1_execution_plan() -> dict:
    return {
        "method": "random_uniform",
        "seed": 2026,
        "samples_per_resonator_type": 256,
        "total_samples": 512,
    }
