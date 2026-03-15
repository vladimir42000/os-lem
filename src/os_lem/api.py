"""Provisional high-level frontend integration facade.

This module provides a narrow wrapper around the current parser -> assemble ->
solve pipeline so UI and automation code can avoid importing low-level kernel
modules directly.

The contract is intentionally modest at this checkpoint:
- dict input is supported directly
- common observations are evaluated into ready-to-plot arrays
- unsupported observation kinds fail explicitly rather than leaking raw internals

This is a provisional integration layer, not yet a broad frozen public API for
all current and future kernel capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from .assemble import AssembledSystem, assemble_system
from .model import NormalizedModel, Observation, RadiatorElement
from .parser import normalize_model
from .units import parse_value
from .solve import (
    SolvedFrequencySweep,
    radiator_observation_pressure,
    radiator_spl,
    solve_frequency_point,
    solve_frequency_sweep,
    waveguide_line_profile_particle_velocity,
    waveguide_line_profile_pressure,
    waveguide_line_profile_volume_velocity,
)


@dataclass(slots=True, frozen=True)
class LineProfileResult:
    """Sampled one-frequency line-profile output exposed by the frontend facade."""

    frequency_hz: float
    quantity: str
    x_m: np.ndarray
    values: np.ndarray


@dataclass(slots=True, frozen=True)
class SimulationResult:
    """High-level simulation result intended for frontend consumption."""

    model: NormalizedModel
    system: AssembledSystem
    sweep: SolvedFrequencySweep
    warnings: tuple[str, ...]
    series: Mapping[str, np.ndarray | LineProfileResult]
    units: Mapping[str, str]
    observation_types: Mapping[str, str]

    @property
    def frequencies_hz(self) -> np.ndarray:
        return self.sweep.frequency_hz

    @property
    def zin_complex_ohm(self) -> np.ndarray | None:
        return self._first_series_for_type("input_impedance")

    @property
    def zin_mag_ohm(self) -> np.ndarray | None:
        series = self.zin_complex_ohm
        if series is None:
            return None
        return np.abs(series)

    @property
    def cone_velocity_m_per_s(self) -> np.ndarray | None:
        return self._first_series_for_type("cone_velocity")

    @property
    def cone_displacement_m(self) -> np.ndarray | None:
        return self._first_series_for_type("cone_displacement")

    @property
    def cone_excursion_mm(self) -> np.ndarray | None:
        series = self.cone_displacement_m
        if series is None:
            return None
        return np.abs(series) * 1.0e3

    def get_series(self, observation_id: str) -> np.ndarray | LineProfileResult:
        return self.series[observation_id]

    def _first_series_for_type(self, obs_type: str) -> np.ndarray | None:
        for obs_id, current_type in self.observation_types.items():
            if current_type == obs_type:
                value = self.series[obs_id]
                if isinstance(value, LineProfileResult):
                    return None
                return value
        return None


def run_simulation(model_dict: Mapping[str, Any], frequencies_hz: Sequence[float]) -> SimulationResult:
    """Run the current loudspeaker pipeline from a Python mapping.

    Parameters
    ----------
    model_dict:
        User-facing model dictionary matching the current YAML schema.
    frequencies_hz:
        1D frequency sweep in Hz.
    """

    if not isinstance(model_dict, Mapping):
        raise TypeError("model_dict must be a mapping")

    normalized_model, warnings = normalize_model(dict(model_dict))
    system = assemble_system(normalized_model)
    sweep = solve_frequency_sweep(normalized_model, system, frequencies_hz)
    series, units, observation_types = _evaluate_supported_observations(normalized_model, system, sweep)

    return SimulationResult(
        model=normalized_model,
        system=system,
        sweep=sweep,
        warnings=tuple(warnings),
        series=series,
        units=units,
        observation_types=observation_types,
    )


def _evaluate_supported_observations(
    model: NormalizedModel,
    system: AssembledSystem,
    sweep: SolvedFrequencySweep,
) -> tuple[dict[str, np.ndarray | LineProfileResult], dict[str, str], dict[str, str]]:
    series: dict[str, np.ndarray | LineProfileResult] = {}
    units: dict[str, str] = {}
    observation_types: dict[str, str] = {}

    for obs in model.observations:
        observation_types[obs.id] = obs.type
        value, unit = _evaluate_observation(model, system, sweep, obs, series)
        series[obs.id] = value
        units[obs.id] = unit

    return series, units, observation_types


def _evaluate_observation(
    model: NormalizedModel,
    system: AssembledSystem,
    sweep: SolvedFrequencySweep,
    obs: Observation,
    resolved_series: Mapping[str, np.ndarray | LineProfileResult],
) -> tuple[np.ndarray | LineProfileResult, str]:
    data = obs.data
    otype = obs.type

    if otype == "input_impedance":
        return sweep.input_impedance.copy(), "ohm"

    if otype == "cone_velocity":
        return sweep.cone_velocity.copy(), "m/s"

    if otype == "cone_displacement":
        return sweep.cone_displacement.copy(), "m"

    if otype == "node_pressure":
        node = str(data["target"])
        idx = system.node_index[node]
        return sweep.pressures[:, idx].copy(), "Pa"

    if otype == "spl":
        target = str(data["target"])
        distance_m = _parse_distance_m(data.get("distance", 1.0))
        radiation_space = _resolve_radiation_space(model, data.get("radiation_space"))
        return radiator_spl(sweep, system, target, distance_m, radiation_space=radiation_space), "dB"

    if otype == "spl_sum":
        total = np.zeros_like(sweep.frequency_hz, dtype=np.complex128)
        parent_space = _resolve_radiation_space(model, data.get("radiation_space"))
        for term in data["terms"]:
            target = str(term["target"])
            distance_m = _parse_distance_m(term.get("distance", 1.0))
            term_space = term.get("radiation_space", parent_space)
            total = total + radiator_observation_pressure(
                sweep,
                system,
                target,
                distance_m,
                radiation_space=term_space,
            )
        return 20.0 * np.log10(np.maximum(np.abs(total), 1.0e-30) / 2.0e-5), "dB"

    if otype == "line_profile":
        frequency_hz = _parse_frequency_hz(data["frequency"])
        point = solve_frequency_point(model, system, frequency_hz)
        quantity = str(data["quantity"])
        points = int(data["points"])
        target = str(data["target"])
        if quantity == "pressure":
            profile = waveguide_line_profile_pressure(point, system, target, points)
            unit = "Pa"
        elif quantity == "volume_velocity":
            profile = waveguide_line_profile_volume_velocity(point, system, target, points)
            unit = "m^3/s"
        elif quantity == "particle_velocity":
            profile = waveguide_line_profile_particle_velocity(point, system, target, points)
            unit = "m/s"
        else:  # pragma: no cover - parser should reject earlier
            raise ValueError(f"Unsupported line_profile quantity: {quantity!r}")
        return LineProfileResult(
            frequency_hz=frequency_hz,
            quantity=profile.quantity,
            x_m=profile.x_m.copy(),
            values=profile.values.copy(),
        ), unit

    if otype == "group_delay":
        target_id = str(data["target"])
        target_series = resolved_series.get(target_id)
        if target_series is None:
            raise ValueError(f"group_delay target {target_id!r} has not been evaluated")
        if isinstance(target_series, LineProfileResult):
            raise NotImplementedError("group_delay does not support line_profile targets in os_lem.api")
        phase = np.unwrap(np.angle(target_series))
        omega = 2.0 * np.pi * sweep.frequency_hz
        return -np.gradient(phase, omega), "s"

    raise NotImplementedError(
        f"Observation type {otype!r} is not yet exposed by the provisional os_lem.api facade"
    )



def _resolve_radiation_space(model: NormalizedModel, local_value: Any) -> str | None:
    if local_value is not None:
        return str(local_value)
    meta_value = model.metadata.get("radiation_space")
    if meta_value is not None:
        return str(meta_value)
    return None


def _parse_frequency_hz(value: Any) -> float:
    if isinstance(value, str):
        return float(parse_value(value))
    return float(value)

def _parse_distance_m(value: Any) -> float:
    if isinstance(value, str):
        text = value.strip()
        if text.endswith(" m"):
            return float(text[:-2].strip())
        return float(text)
    return float(value)
