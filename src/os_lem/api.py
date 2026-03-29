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

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from .assemble import AssembledElement, AssembledSystem, assemble_system
from .elements.duct import duct_admittance
from .elements.radiator import radiator_impedance
from .model import DuctElement, NormalizedModel, Observation, RadiatorElement, Waveguide1DElement
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


_FRONTEND_CONTRACT_V1: dict[str, Any] = {
    "contract_name": "os_lem_frontend_contract_v1",
    "contract_version": 1,
    "api_function": "run_simulation",
    "machine_readable_function": "get_frontend_contract_v1",
    "stability_rule": (
        "Any patch that changes supported element types, observation types, result surface, "
        "example-worthy workflows, or parser fields used by the facade must either update "
        "the frontend contract manifest, frontend docs, and frontend tests, or explicitly "
        "declare: No frontend contract change."
    ),
    "stable": {
        "driver_models": ["ts_classic", "em_explicit"],
        "element_types": {
            "volume": {"required_fields": ["id", "type", "node", "value"]},
            "duct": {"required_fields": ["id", "type", "node_a", "node_b", "length", "area"]},
            "waveguide_1d": {
                "required_fields": [
                    "id",
                    "type",
                    "node_a",
                    "node_b",
                    "length",
                    "area_start",
                    "area_end",
                    "profile",
                ],
                "profile": "conical",
                "optional_fields": ["segments", "loss"],
            },
            "radiator": {"required_fields": ["id", "type", "node", "model", "area"]},
        },
        "radiator_models": ["infinite_baffle_piston", "unflanged_piston", "flanged_piston"],
        "observation_types": {
            "input_impedance": {"result_kind": "complex_series", "unit": "ohm"},
            "cone_velocity": {"result_kind": "complex_series", "unit": "m/s"},
            "cone_displacement": {"result_kind": "complex_series", "unit": "m"},
            "node_pressure": {"result_kind": "complex_series", "unit": "Pa"},
            "spl": {"result_kind": "real_series", "unit": "dB"},
            "spl_sum": {"result_kind": "real_series", "unit": "dB"},
            "element_volume_velocity": {"result_kind": "complex_series", "unit": "m^3/s"},
            "element_particle_velocity": {"result_kind": "complex_series", "unit": "m/s"},
            "line_profile": {
                "result_kind": "line_profile",
                "quantities": ["pressure", "volume_velocity", "particle_velocity"],
            },
            "group_delay": {"result_kind": "real_series", "unit": "s"},
        },
        "result_surface": {
            "simulation_result_fields": [
                "model",
                "system",
                "sweep",
                "warnings",
                "series",
                "units",
                "observation_types",
            ],
            "simulation_result_properties": [
                "frequencies_hz",
                "zin_complex_ohm",
                "zin_mag_ohm",
                "cone_velocity_m_per_s",
                "cone_displacement_m",
                "cone_excursion_mm",
            ],
            "line_profile_fields": ["frequency_hz", "quantity", "x_m", "values"],
        },
        "stable_workflows": [
            "closed_box_with_front_radiator",
            "single_rear_conical_line_with_one_mouth_radiator",
        ],
        "canonical_examples": [
            {
                "id": "closed_box_minimal",
                "path": "examples/frontend_contract_v1/closed_box_minimal.yaml",
                "workflow": "closed_box_with_front_radiator",
            },
            {
                "id": "conical_line_minimal",
                "path": "examples/frontend_contract_v1/conical_line_minimal.yaml",
                "workflow": "single_rear_conical_line_with_one_mouth_radiator",
            },
        ],
    },
    "experimental": {
        "topology_openings": [
            "parallel_split_recombine_bundles_between_same_two_nodes",
            "true_interior_acoustic_junctions_with_more_than_two_incident_branches",
            "branched_horn_skeletons_with_multiple_leaf_mouth_radiators",
            "shared_exit_recombination_after_multiple_upstream_branch_legs",
            "dual_junction_split_merge_horn_skeletons",
        ],
        "note": (
            "These openings exist in the current kernel, but they are not part of the frozen "
            "frontend contract v1 and may evolve without preserving frontend-level semantics."
        ),
    },
}


def get_frontend_contract_v1() -> dict[str, Any]:
    """Return the frozen machine-readable frontend integration contract for v1.

    The returned mapping is JSON-serializable and separates the frontend surface
    that is intentionally stable from kernel openings that remain experimental.
    """

    return deepcopy(_FRONTEND_CONTRACT_V1)


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
        observable_contract = _resolve_observable_contract(data.get("observable_contract"))
        return radiator_spl(
            sweep,
            system,
            target,
            distance_m,
            radiation_space=radiation_space,
            observable_contract=observable_contract,
        ), "dB"

    if otype == "spl_sum":
        total = np.zeros_like(sweep.frequency_hz, dtype=np.complex128)
        parent_space = _resolve_radiation_space(model, data.get("radiation_space"))
        parent_contract = _resolve_observable_contract(data.get("observable_contract"))
        for term in data["terms"]:
            target = str(term["target"])
            distance_m = _parse_distance_m(term.get("distance", 1.0))
            term_space = term.get("radiation_space", parent_space)
            term_contract = _resolve_observable_contract(term.get("observable_contract", parent_contract))
            total = total + radiator_observation_pressure(
                sweep,
                system,
                target,
                distance_m,
                radiation_space=term_space,
                observable_contract=term_contract,
            )
        return 20.0 * np.log10(np.maximum(np.abs(total), 1.0e-30) / 2.0e-5), "dB"

    if otype in {"element_volume_velocity", "element_particle_velocity"}:
        return _evaluate_element_observation(system, sweep, data, quantity=otype)

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



def _evaluate_element_observation(
    system: AssembledSystem,
    sweep: SolvedFrequencySweep,
    data: Mapping[str, Any],
    *,
    quantity: str,
) -> tuple[np.ndarray, str]:
    target = str(data["target"])
    location = _resolve_waveguide_location(data.get("location"))
    element = _find_element(system, target)

    if element.kind == "duct":
        if location is not None:
            raise ValueError(f"{quantity} does not accept location for duct target {target!r}")
        payload = element.payload
        assert isinstance(payload, DuctElement)
        assert element.node_b is not None
        pa = sweep.pressures[:, element.node_a]
        pb = sweep.pressures[:, element.node_b]
        admittance = np.array(
            [duct_admittance(float(omega), payload.length_m, payload.area_m2) for omega in sweep.omega_rad_s],
            dtype=np.complex128,
        )
        values = admittance * (pa - pb)
        if quantity == "element_particle_velocity":
            values = values / payload.area_m2
            return values, "m/s"
        return values, "m^3/s"

    if element.kind == "radiator":
        if location is not None:
            raise ValueError(f"{quantity} does not accept location for radiator target {target!r}")
        payload = element.payload
        assert isinstance(payload, RadiatorElement)
        pressure = sweep.pressures[:, element.node_a]
        impedance = np.array(
            [radiator_impedance(payload.model, float(omega), payload.area_m2) for omega in sweep.omega_rad_s],
            dtype=np.complex128,
        )
        values = pressure / impedance
        if quantity == "element_particle_velocity":
            values = values / payload.area_m2
            return values, "m/s"
        return values, "m^3/s"

    if element.kind == "waveguide_1d":
        if location is None:
            raise ValueError(f"{quantity} requires location 'a' or 'b' for waveguide_1d target {target!r}")
        payload = element.payload
        assert isinstance(payload, Waveguide1DElement)
        if quantity == "element_volume_velocity":
            values = (
                sweep.waveguide_endpoint_flow[target].node_a
                if location == "a"
                else -sweep.waveguide_endpoint_flow[target].node_b
            )
            return values.copy(), "m^3/s"
        values = (
            sweep.waveguide_endpoint_velocity[target].node_a
            if location == "a"
            else -sweep.waveguide_endpoint_velocity[target].node_b
        )
        return values.copy(), "m/s"

    raise NotImplementedError(
        f"Observation type {quantity!r} does not support target element kind {element.kind!r} in os_lem.api"
    )


def _find_element(system: AssembledSystem, element_id: str) -> AssembledElement:
    for element in (*system.branch_elements, *system.shunt_elements):
        if element.id == element_id:
            return element
    raise ValueError(f"unknown element id {element_id!r}")


def _resolve_waveguide_location(local_value: Any) -> str | None:
    if local_value is None:
        return None
    token = str(local_value).strip()
    if token == "":
        return None
    if token not in {"a", "b"}:
        raise ValueError(f"Unsupported waveguide location {local_value!r}; expected one of ['a', 'b']")
    return token


def _resolve_observable_contract(local_value: Any) -> str | None:
    if local_value is None:
        return None
    token = str(local_value).strip()
    return None if token == "" else token


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
