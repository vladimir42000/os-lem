"""GDN13 cone-excursion output surface for OPT consumption.

This module exposes one narrow os-lem-owned output surface for the accepted
GDN13 offset-driver TQWT baseline. It intentionally reuses the accepted
normalized model packet, the accepted observations-list mechanism, and the
accepted solver callable. It does not implement optimizer logic, fallback
normalization, score behavior, or resonator semantics.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

import numpy as np

from os_lem.api import run_simulation
from os_lem.gdn13_offset_tqwt_opt_model_packet import (
    get_gdn13_offset_tqwt_normalized_model_packet_for_opt,
)

CASE_ID = "gdn13_offset_tqwt"
ACCEPTED_DRIVER_ID = "drv_gdn13"
MODEL_PACKET_CALLABLE = (
    "os_lem.gdn13_offset_tqwt_opt_model_packet."
    "get_gdn13_offset_tqwt_normalized_model_packet_for_opt"
)
SOLVER_CALLABLE = "os_lem.api.run_simulation"
CONE_EXCURSION_CONVENTION = "abs(cone_displacement_m) * 1e3"
CONE_EXCURSION_SOURCE = "os_lem observations list cone_displacement"

OBSERVATION_RECORDS: tuple[dict[str, str], ...] = (
    {
        "id": "gdn13_cone_displacement",
        "type": "cone_displacement",
        "target": ACCEPTED_DRIVER_ID,
    },
    {
        "id": "gdn13_cone_velocity",
        "type": "cone_velocity",
        "target": ACCEPTED_DRIVER_ID,
    },
)


def _as_mapping(packet: Any) -> Mapping[str, Any]:
    if isinstance(packet, Mapping):
        return packet
    if hasattr(packet, "__dict__"):
        return vars(packet)
    raise TypeError("GDN13 model packet must be a mapping-like object")


def _packet_get(packet: Mapping[str, Any], key: str, default: Any = None) -> Any:
    if key in packet:
        return packet[key]
    return default


def _array_or_none(value: Any) -> np.ndarray | None:
    if value is None:
        return None
    return np.asarray(value)


def _is_1d_finite_real(values: np.ndarray) -> bool:
    return (
        values.ndim == 1
        and not np.iscomplexobj(values)
        and np.all(np.isfinite(values.astype(float, copy=False)))
    )


def _find_driver_id(model_dict: Mapping[str, Any]) -> str | None:
    """Find the accepted GDN13 driver id without assuming a fixed schema.

    The current accepted packet is expected to contain ``drv_gdn13``. This helper
    verifies that the id is present in one of the common model structures or, as
    a last defensive check, in the serialized model representation.
    """

    for key in ("drivers", "driver", "elements"):
        value = model_dict.get(key)
        if isinstance(value, Mapping):
            if value.get("id") == ACCEPTED_DRIVER_ID:
                return ACCEPTED_DRIVER_ID
        if isinstance(value, list):
            for item in value:
                if isinstance(item, Mapping) and item.get("id") == ACCEPTED_DRIVER_ID:
                    return ACCEPTED_DRIVER_ID

    if ACCEPTED_DRIVER_ID in repr(model_dict):
        return ACCEPTED_DRIVER_ID

    return None


def _append_required_observations(model_dict: dict[str, Any]) -> list[dict[str, str]]:
    existing = model_dict.get("observations")
    if existing is None:
        observations: list[dict[str, Any]] = []
    elif isinstance(existing, list):
        observations = list(existing)
    else:
        raise TypeError("model_dict['observations'] must be a list when present")

    existing_keys = {
        (obs.get("id"), obs.get("type"), obs.get("target"))
        for obs in observations
        if isinstance(obs, Mapping)
    }
    for record in OBSERVATION_RECORDS:
        key = (record["id"], record["type"], record["target"])
        if key not in existing_keys:
            observations.append(dict(record))
    model_dict["observations"] = observations
    return [dict(record) for record in OBSERVATION_RECORDS]


def _blocked_surface(reason: str, packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = packet or {}
    return {
        "output_contract_status": "blocked",
        "block_reason": reason,
        "case_id": CASE_ID,
        "driver_id": ACCEPTED_DRIVER_ID,
        "frequency_hz": None,
        "cone_excursion_mm": None,
        "cone_excursion_convention": CONE_EXCURSION_CONVENTION,
        "cone_excursion_unit": "mm",
        "cone_excursion_source": CONE_EXCURSION_SOURCE,
        "model_packet_callable": MODEL_PACKET_CALLABLE,
        "solver_callable": SOLVER_CALLABLE,
        "observation_records": [dict(record) for record in OBSERVATION_RECORDS],
        "normalized_model_packet_status": _packet_get(packet, "packet_status", None),
        "baseline_parity_gate_status": _packet_get(packet, "baseline_parity_gate_status", None),
        "full_band_spl_claim": False,
        "mouth_only_spl_claim": False,
        "normalization_owner": "os-lem",
        "model_construction_owner": "os-lem",
        "motion_observable_owner": "os-lem",
    }


def get_gdn13_cone_excursion_output_surface_for_opt(
    *,
    model_packet: Mapping[str, Any] | None = None,
    frequencies_hz: Any | None = None,
) -> dict[str, Any]:
    """Return the accepted GDN13 cone-excursion output surface for OPT.

    The callable is deliberately narrow:
    - it obtains the accepted GDN13 model packet from os-lem unless a packet is
      explicitly supplied for testing;
    - it makes a defensive copy of the packet model_dict;
    - it adds the accepted observations-list records for ``drv_gdn13``;
    - it calls ``os_lem.api.run_simulation``;
    - it validates that ``cone_excursion_mm`` is a finite real-valued 1D array
      aligned with ``frequency_hz`` and consistent with
      ``abs(cone_displacement_m) * 1e3`` when displacement is returned.
    """

    packet_obj = (
        model_packet
        if model_packet is not None
        else get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    )
    packet = _as_mapping(packet_obj)

    packet_status = _packet_get(packet, "packet_status")
    if packet_status not in (None, "passed"):
        return _blocked_surface(
            f"normalized model packet status is not passed: {packet_status!r}", packet
        )

    model_dict = _packet_get(packet, "model_dict")
    if not isinstance(model_dict, Mapping):
        return _blocked_surface("normalized model packet did not expose model_dict", packet)

    driver_id = _find_driver_id(model_dict)
    if driver_id != ACCEPTED_DRIVER_ID:
        return _blocked_surface(
            f"accepted GDN13 driver id {ACCEPTED_DRIVER_ID!r} not found in model_dict",
            packet,
        )

    packet_frequencies = _packet_get(packet, "frequencies_hz")
    selected_frequencies = frequencies_hz if frequencies_hz is not None else packet_frequencies
    if selected_frequencies is None:
        return _blocked_surface("normalized model packet did not expose frequencies_hz", packet)

    frequency_hz = np.asarray(selected_frequencies, dtype=float)
    if frequency_hz.ndim != 1 or frequency_hz.size == 0 or not np.all(np.isfinite(frequency_hz)):
        return _blocked_surface("frequencies_hz is not a finite non-empty 1D array", packet)

    model_with_observations = deepcopy(dict(model_dict))
    observation_records = _append_required_observations(model_with_observations)

    try:
        result = run_simulation(model_with_observations, frequency_hz)
    except Exception as exc:  # pragma: no cover - exercised only on repo/runtime failure
        return _blocked_surface(f"run_simulation failed with cone-motion observations: {exc}", packet)

    result_frequency = _array_or_none(getattr(result, "frequency_hz", None))
    if result_frequency is None:
        result_frequency = frequency_hz
    else:
        result_frequency = np.asarray(result_frequency, dtype=float)

    cone_displacement_m = _array_or_none(getattr(result, "cone_displacement_m", None))
    cone_velocity_m_per_s = _array_or_none(getattr(result, "cone_velocity_m_per_s", None))
    cone_excursion_mm = _array_or_none(getattr(result, "cone_excursion_mm", None))

    if cone_excursion_mm is None:
        return _blocked_surface("SimulationResult did not expose cone_excursion_mm", packet)

    cone_excursion_mm = np.asarray(cone_excursion_mm)
    if not _is_1d_finite_real(cone_excursion_mm):
        return _blocked_surface("cone_excursion_mm is not a finite real-valued 1D array", packet)

    if result_frequency.ndim != 1 or result_frequency.shape != cone_excursion_mm.shape:
        return _blocked_surface(
            "cone_excursion_mm is not aligned with returned frequency_hz", packet
        )

    displacement_relation_passed: bool | None = None
    if cone_displacement_m is not None:
        expected = np.abs(np.asarray(cone_displacement_m)) * 1e3
        displacement_relation_passed = bool(
            expected.shape == cone_excursion_mm.shape
            and np.allclose(cone_excursion_mm, expected, rtol=1e-10, atol=1e-12)
        )
        if not displacement_relation_passed:
            return _blocked_surface(
                "cone_excursion_mm did not match abs(cone_displacement_m) * 1e3",
                packet,
            )

    return {
        "output_contract_status": "passed",
        "block_reason": None,
        "case_id": CASE_ID,
        "driver_id": ACCEPTED_DRIVER_ID,
        "frequency_hz": result_frequency,
        "cone_excursion_mm": cone_excursion_mm,
        "cone_excursion_convention": CONE_EXCURSION_CONVENTION,
        "cone_excursion_unit": "mm",
        "cone_excursion_source": CONE_EXCURSION_SOURCE,
        "model_packet_callable": MODEL_PACKET_CALLABLE,
        "solver_callable": SOLVER_CALLABLE,
        "observation_records": observation_records,
        "normalized_model_packet_status": packet_status,
        "baseline_parity_gate_status": _packet_get(packet, "baseline_parity_gate_status"),
        "full_band_spl_claim": False,
        "mouth_only_spl_claim": False,
        "normalization_owner": "os-lem",
        "model_construction_owner": "os-lem",
        "motion_observable_owner": "os-lem",
        "cone_displacement_m": cone_displacement_m,
        "cone_velocity_m_per_s": cone_velocity_m_per_s,
        "cone_displacement_unit": "m",
        "cone_velocity_unit": "m/s",
        "cone_displacement_relation_passed": displacement_relation_passed,
    }


def export_gdn13_cone_excursion_output_surface_for_opt(
    **kwargs: Any,
) -> dict[str, Any]:
    """Alias for callers that prefer export_* naming."""

    return get_gdn13_cone_excursion_output_surface_for_opt(**kwargs)
