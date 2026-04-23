from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.elements.waveguide_1d import area_at_position
from os_lem.parser import normalize_model
from os_lem.solve import (
    solve_frequency_point,
    waveguide_line_profile_particle_velocity,
    waveguide_line_profile_pressure,
    waveguide_line_profile_volume_velocity,
)


@dataclass(frozen=True)
class ExponentialSmokeObservation:
    segments: int
    x_m: np.ndarray
    pressure_values: np.ndarray
    flow_values: np.ndarray
    particle_values: np.ndarray
    node_a_pressure: complex
    node_b_pressure: complex
    endpoint_flow_a: complex
    endpoint_flow_b: complex
    endpoint_velocity_a: complex
    endpoint_velocity_b: complex
    boundary_areas_m2: np.ndarray

    @property
    def mouth_pressure_abs(self) -> float:
        return float(abs(self.node_b_pressure))

    @property
    def endpoint_flow_abs(self) -> float:
        return float(abs(self.endpoint_flow_a))

    @property
    def all_finite(self) -> bool:
        arrays = [self.pressure_values, self.flow_values, self.particle_values]
        return all(np.all(np.isfinite(arr.real)) and np.all(np.isfinite(arr.imag)) for arr in arrays)


@dataclass(frozen=True)
class ExponentialSmokeReport:
    observations: tuple[ExponentialSmokeObservation, ...]
    frequency_hz: float


def exponential_model_dict() -> dict:
    return {
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
            "node_front": "front",
            "node_rear": "rear",
        },
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "infinite_baffle_piston",
                "area": "132 cm2",
            },
            {
                "id": "rear_vol",
                "type": "volume",
                "node": "rear",
                "value": "18 l",
            },
            {
                "id": "wg1",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "mouth",
                "length": "40 cm",
                "area_start": "10 cm2",
                "area_end": "50 cm2",
                "profile": "exponential",
                "segments": 12,
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "unflanged_piston",
                "area": "50 cm2",
            },
        ],
        "observations": [
            {"id": "line_q_a", "type": "element_volume_velocity", "target": "wg1", "location": "a"},
            {"id": "line_q_b", "type": "element_volume_velocity", "target": "wg1", "location": "b"},
            {"id": "line_v_a", "type": "element_particle_velocity", "target": "wg1", "location": "a"},
            {"id": "line_v_b", "type": "element_particle_velocity", "target": "wg1", "location": "b"},
            {"id": "line_p_120", "type": "line_profile", "target": "wg1", "quantity": "pressure", "frequency": "120 Hz", "points": 13},
            {"id": "line_q_120", "type": "line_profile", "target": "wg1", "quantity": "volume_velocity", "frequency": "120 Hz", "points": 13},
            {"id": "line_v_120", "type": "line_profile", "target": "wg1", "quantity": "particle_velocity", "frequency": "120 Hz", "points": 13},
        ],
    }


def build_exponential_model_with_segments(segments: int) -> dict:
    model_dict = copy.deepcopy(exponential_model_dict())
    for element in model_dict["elements"]:
        if element.get("id") == "wg1":
            element["segments"] = int(segments)
            return model_dict
    raise AssertionError("expected wg1 element in exponential smoke model")


def _waveguide_by_id(model, waveguide_id: str):
    for waveguide in model.waveguides:
        if waveguide.id == waveguide_id:
            return waveguide
    raise KeyError(f"unknown waveguide id: {waveguide_id}")


def _relative_l2_change(a: np.ndarray, b: np.ndarray) -> float:
    denom = max(float(np.linalg.norm(b)), 1e-12)
    return float(np.linalg.norm(a - b) / denom)


def _relative_scalar_change(a: float, b: float) -> float:
    denom = max(abs(b), 1e-12)
    return float(abs(a - b) / denom)


def downsample_boundary_profile(values: np.ndarray, coarse_segments: int, fine_segments: int) -> np.ndarray:
    if fine_segments % coarse_segments != 0:
        raise ValueError("fine_segments must be an integer multiple of coarse_segments")
    ratio = fine_segments // coarse_segments
    return np.asarray(values[::ratio], dtype=np.complex128)


def evaluate_exponential_reference_smoke(
    build_model: Callable[[int], dict],
    *,
    refinement_levels: Sequence[int] = (6, 12, 24),
    frequency_hz: float = 120.0,
    waveguide_id: str = "wg1",
    node_a: str = "rear",
    node_b: str = "mouth",
) -> ExponentialSmokeReport:
    observations: list[ExponentialSmokeObservation] = []
    for segments in refinement_levels:
        model, _ = normalize_model(build_model(int(segments)))
        system = assemble_system(model)
        point = solve_frequency_point(model, system, float(frequency_hz))
        waveguide = _waveguide_by_id(model, waveguide_id)
        points = waveguide.segments + 1

        pressure = waveguide_line_profile_pressure(point, system, waveguide_id, points=points)
        flow = waveguide_line_profile_volume_velocity(point, system, waveguide_id, points=points)
        particle = waveguide_line_profile_particle_velocity(point, system, waveguide_id, points=points)

        idx = {name: i for i, name in enumerate(system.node_order)}
        boundary_areas = np.array(
            [
                area_at_position(
                    waveguide.length_m,
                    waveguide.area_start_m2,
                    waveguide.area_end_m2,
                    float(x_m),
                    profile=waveguide.profile,
                )
                for x_m in flow.x_m
            ],
            dtype=float,
        )

        observations.append(
            ExponentialSmokeObservation(
                segments=waveguide.segments,
                x_m=np.asarray(flow.x_m, dtype=float),
                pressure_values=np.asarray(pressure.values, dtype=np.complex128),
                flow_values=np.asarray(flow.values, dtype=np.complex128),
                particle_values=np.asarray(particle.values, dtype=np.complex128),
                node_a_pressure=point.pressures[idx[node_a]],
                node_b_pressure=point.pressures[idx[node_b]],
                endpoint_flow_a=point.waveguide_endpoint_flow[waveguide_id].node_a,
                endpoint_flow_b=point.waveguide_endpoint_flow[waveguide_id].node_b,
                endpoint_velocity_a=point.waveguide_endpoint_velocity[waveguide_id].node_a,
                endpoint_velocity_b=point.waveguide_endpoint_velocity[waveguide_id].node_b,
                boundary_areas_m2=boundary_areas,
            )
        )

    return ExponentialSmokeReport(observations=tuple(observations), frequency_hz=float(frequency_hz))
