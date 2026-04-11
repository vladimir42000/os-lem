"""Bounded reference scaffolding for the v0.6 TQWT side-resonator optimization probe.

This module now supports a truthful, bounded phase-1 coarse search above the
already-frozen probe definition. It intentionally remains small:
- no optimizer framework
- no local refinement
- no API expansion
- no topology-family growth
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Iterable, List, Mapping, Optional, Sequence

import numpy as np


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


@dataclass(frozen=True)
class Phase1RuntimeConfig:
    search_mode: str = "random_uniform"
    random_seed: int = 2026
    sample_count: int = 96
    best_n: int = 5
    frequency_start_hz: float = 20.0
    frequency_stop_hz: float = 500.0
    frequency_count: int = 96


@dataclass(frozen=True)
class CandidateEvaluation:
    label: str
    params: Optional[ProbeParameters]
    score: float
    components: ScoreBreakdown
    mean_spl_band_db: float
    max_excursion_band_mm: float
    geometry_valid: bool
    failure: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "params": None if self.params is None else probe_parameters_to_dict(self.params),
            "score": self.score,
            "components": {
                "ripple_db": self.components.ripple_db,
                "excursion_penalty": self.components.excursion_penalty,
                "output_penalty": self.components.output_penalty,
                "geometry_penalty": self.components.geometry_penalty,
            },
            "mean_spl_band_db": self.mean_spl_band_db,
            "max_excursion_band_mm": self.max_excursion_band_mm,
            "geometry_valid": self.geometry_valid,
            "failure": self.failure,
        }


DEFAULT_BOUNDS = ProbeBounds()
DEFAULT_OBJECTIVE = ObjectiveConfig()
DEFAULT_PHASE1_RUNTIME = Phase1RuntimeConfig()


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


def band_mask(
    frequencies_hz: Sequence[float],
    low_hz: float,
    high_hz: float,
) -> np.ndarray:
    freq = np.asarray(frequencies_hz, dtype=float)
    return (freq >= low_hz) & (freq <= high_hz)


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
  execution_mode: phase1_coarse_search

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


def phase1_runtime_defaults() -> Phase1RuntimeConfig:
    return DEFAULT_PHASE1_RUNTIME


def phase1_runtime_defaults_dict() -> dict[str, Any]:
    return asdict(DEFAULT_PHASE1_RUNTIME)


def probe_parameters_to_dict(params: ProbeParameters) -> dict[str, Any]:
    data = asdict(params)
    data["resonator_type"] = params.resonator_type.value
    return data


def render_template_text(template_text: str, params: ProbeParameters) -> str:
    replacements = {
        "${x_attach_norm}": f"{params.x_attach_norm:.9g}",
        "${resonator_type}": params.resonator_type.value,
        "${L_res_m}": f"{params.l_res_m:.9g}",
        "${S_res_m2}": f"{params.s_res_m2:.9g}",
        "${V_res_m3}": "null" if params.v_res_m3 is None else f"{params.v_res_m3:.9g}",
    }
    rendered = template_text
    for needle, replacement in replacements.items():
        rendered = rendered.replace(needle, replacement)
    return rendered


def main_line_boundary_positions() -> dict[str, float]:
    total_length_m = 0.23 + 0.46 + 0.32
    return {
        "rear": 0.0,
        "split": 0.23 / total_length_m,
        "merge": (0.23 + 0.46) / total_length_m,
        "mouth": 1.0,
    }


def nearest_main_line_boundary_node(x_attach_norm: float) -> str:
    positions = main_line_boundary_positions()
    return min(positions, key=lambda node: abs(positions[node] - x_attach_norm))


def fixed_phase1_frequencies_hz(
    runtime: Phase1RuntimeConfig = DEFAULT_PHASE1_RUNTIME,
) -> np.ndarray:
    return np.geomspace(
        runtime.frequency_start_hz,
        runtime.frequency_stop_hz,
        runtime.frequency_count,
    )


def sample_phase1_candidates(
    sample_count: int,
    seed: int,
    bounds: ProbeBounds = DEFAULT_BOUNDS,
) -> List[ProbeParameters]:
    if sample_count <= 0:
        raise ValueError("sample_count must be positive")

    rng = np.random.default_rng(seed)
    out: List[ProbeParameters] = []
    for idx in range(sample_count):
        resonator_type = (
            ResonatorType.SIDE_PIPE if idx % 2 == 0 else ResonatorType.CHAMBER_NECK
        )
        x_attach_norm = float(rng.uniform(bounds.x_attach_norm_min, bounds.x_attach_norm_max))
        l_res_m = float(rng.uniform(bounds.l_res_m_min, bounds.l_res_m_max))
        s_res_m2 = float(rng.uniform(bounds.s_res_m2_min, bounds.s_res_m2_max))
        v_res_m3: Optional[float]
        if resonator_type == ResonatorType.CHAMBER_NECK:
            v_res_m3 = float(rng.uniform(bounds.v_res_m3_min, bounds.v_res_m3_max))
        else:
            v_res_m3 = None
        out.append(
            ProbeParameters(
                x_attach_norm=x_attach_norm,
                resonator_type=resonator_type,
                l_res_m=l_res_m,
                s_res_m2=s_res_m2,
                v_res_m3=v_res_m3,
            )
        )
    return out


def baseline_offset_tap_model_dict() -> dict[str, Any]:
    return {
        "meta": {"name": "tqwt_side_resonator_probe_baseline", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "tap",
            "node_rear": "rear",
        },
        "elements": [
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "split",
                "length": "23 cm",
                "area_start": "80 cm2",
                "area_end": "88 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "main_leg",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "46 cm",
                "area_start": "88 cm2",
                "area_end": "102 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "tap_upstream",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "tap",
                "length": "18 cm",
                "area_start": "52 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "tap_downstream",
                "type": "waveguide_1d",
                "node_a": "tap",
                "node_b": "merge",
                "length": "16 cm",
                "area_start": "55 cm2",
                "area_end": "62 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "mouth",
                "length": "32 cm",
                "area_start": "102 cm2",
                "area_end": "105 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "flanged_piston",
                "area": "105 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
            {
                "id": "spl_total",
                "type": "spl",
                "target": "mouth_rad",
                "distance": "1 m",
                "radiation_space": "2pi",
            },
        ],
    }


def build_candidate_model_dict(params: ProbeParameters) -> dict[str, Any]:
    model = baseline_offset_tap_model_dict()
    attach_node = nearest_main_line_boundary_node(params.x_attach_norm)

    if params.resonator_type == ResonatorType.SIDE_PIPE:
        model["elements"].extend(
            [
                {
                    "id": "res_pipe",
                    "type": "waveguide_1d",
                    "node_a": attach_node,
                    "node_b": "res_pipe_end",
                    "length": f"{params.l_res_m:.9g} m",
                    "area_start": f"{params.s_res_m2:.9g} m2",
                    "area_end": f"{params.s_res_m2:.9g} m2",
                    "profile": "conical",
                    "segments": 3,
                },
                {
                    "id": "res_pipe_terminal",
                    "type": "volume",
                    "node": "res_pipe_end",
                    "value": "1e-6 m3",
                },
            ]
        )
    else:
        if params.v_res_m3 is None:
            raise ValueError("chamber_neck candidate requires v_res_m3")
        model["elements"].extend(
            [
                {
                    "id": "res_neck",
                    "type": "duct",
                    "node_a": attach_node,
                    "node_b": "res_chamber",
                    "length": f"{params.l_res_m:.9g} m",
                    "area": f"{params.s_res_m2:.9g} m2",
                },
                {
                    "id": "res_chamber_volume",
                    "type": "volume",
                    "node": "res_chamber",
                    "value": f"{params.v_res_m3:.9g} m3",
                },
            ]
        )

    return model


def evaluate_candidate_from_series(
    label: str,
    params: Optional[ProbeParameters],
    frequencies_hz: Sequence[float],
    spl_total_db: Sequence[float],
    excursion_mm: Sequence[float],
    baseline_mean_spl_band_db: float,
    geometry_valid: bool,
    objective: ObjectiveConfig = DEFAULT_OBJECTIVE,
    failure: Optional[str] = None,
) -> CandidateEvaluation:
    mask = band_mask(frequencies_hz, objective.band_hz_low, objective.band_hz_high)
    if not np.any(mask):
        raise ValueError("band mask is empty")

    spl_band = np.asarray(spl_total_db, dtype=float)[mask]
    excursion_band = np.asarray(excursion_mm, dtype=float)[mask]
    components = compute_probe_score(
        spl_band_db=spl_band.tolist(),
        excursion_band_mm=excursion_band.tolist(),
        baseline_mean_spl_band_db=baseline_mean_spl_band_db,
        geometry_is_valid=geometry_valid,
        objective=objective,
    )
    mean_spl_band_db = float(np.mean(centered_moving_average(spl_band.tolist(), objective.smoothing_window_bins)))
    max_excursion_band_mm = float(np.max(excursion_band))
    return CandidateEvaluation(
        label=label,
        params=params,
        score=components.total_score,
        components=components,
        mean_spl_band_db=mean_spl_band_db,
        max_excursion_band_mm=max_excursion_band_mm,
        geometry_valid=geometry_valid,
        failure=failure,
    )


def rank_phase1_results(
    baseline: CandidateEvaluation,
    candidates: Sequence[CandidateEvaluation],
    best_n: int,
) -> dict[str, Any]:
    successful = [candidate for candidate in candidates if candidate.failure is None]
    ranked = sorted(successful, key=lambda candidate: (candidate.score, candidate.label))
    return {
        "baseline": baseline.as_dict(),
        "best_n": [candidate.as_dict() for candidate in ranked[:best_n]],
        "candidate_count": len(candidates),
        "successful_candidate_count": len(successful),
        "failed_candidate_count": len(candidates) - len(successful),
    }
