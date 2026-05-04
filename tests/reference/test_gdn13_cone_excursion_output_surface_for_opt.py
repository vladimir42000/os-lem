from __future__ import annotations

from copy import deepcopy

import numpy as np

from os_lem.api import run_simulation
from os_lem.gdn13_cone_excursion_output_surface_for_opt import (
    export_gdn13_cone_excursion_output_surface_for_opt,
    get_gdn13_cone_excursion_output_surface_for_opt,
)
from os_lem.gdn13_offset_tqwt_opt_model_packet import (
    get_gdn13_offset_tqwt_normalized_model_packet_for_opt,
)
from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    build_gdn13_offset_tqwt_model_dict,
)


def _bounded_frequency_subset(packet: dict) -> np.ndarray:
    frequency_hz = np.asarray(packet["frequencies_hz"], dtype=float)
    if frequency_hz.size <= 16:
        return frequency_hz
    idx = np.unique(
        np.rint(np.linspace(0, frequency_hz.size - 1, 16)).astype(int)
    )
    return frequency_hz[idx]


def test_gdn13_cone_excursion_export_callable_imports_and_passes() -> None:
    surface = get_gdn13_cone_excursion_output_surface_for_opt()

    assert surface["output_contract_status"] == "passed"
    assert surface["case_id"] == "gdn13_offset_tqwt"
    assert surface["driver_id"] == "drv_gdn13"
    assert surface["model_packet_callable"] == (
        "os_lem.gdn13_offset_tqwt_opt_model_packet."
        "get_gdn13_offset_tqwt_normalized_model_packet_for_opt"
    )
    assert surface["solver_callable"] == "os_lem.api.run_simulation"
    assert surface["normalization_owner"] == "os-lem"
    assert surface["model_construction_owner"] == "os-lem"
    assert surface["motion_observable_owner"] == "os-lem"


def test_gdn13_cone_excursion_surface_contract_shape_and_convention() -> None:
    surface = get_gdn13_cone_excursion_output_surface_for_opt()

    frequency_hz = np.asarray(surface["frequency_hz"])
    cone_excursion_mm = np.asarray(surface["cone_excursion_mm"])

    assert frequency_hz.ndim == 1
    assert np.all(np.isfinite(frequency_hz))
    assert cone_excursion_mm.ndim == 1
    assert not np.iscomplexobj(cone_excursion_mm)
    assert np.all(np.isfinite(cone_excursion_mm))
    assert cone_excursion_mm.shape == frequency_hz.shape
    assert surface["cone_excursion_convention"] == "abs(cone_displacement_m) * 1e3"
    assert surface["cone_excursion_unit"] == "mm"
    assert surface["cone_excursion_source"] == "os_lem observations list cone_displacement"


def test_gdn13_cone_excursion_surface_uses_accepted_observation_records() -> None:
    surface = get_gdn13_cone_excursion_output_surface_for_opt()
    records = surface["observation_records"]

    assert {
        "id": "gdn13_cone_displacement",
        "type": "cone_displacement",
        "target": "drv_gdn13",
    } in records
    assert {
        "id": "gdn13_cone_velocity",
        "type": "cone_velocity",
        "target": "drv_gdn13",
    } in records


def test_gdn13_cone_excursion_surface_returns_motion_diagnostics_if_available() -> None:
    surface = get_gdn13_cone_excursion_output_surface_for_opt()

    displacement = surface["cone_displacement_m"]
    excursion = np.asarray(surface["cone_excursion_mm"])

    assert displacement is not None
    displacement = np.asarray(displacement)
    assert displacement.ndim == 1
    assert displacement.shape == excursion.shape
    assert np.allclose(excursion, np.abs(displacement) * 1e3, rtol=1e-10, atol=1e-12)
    assert surface["cone_displacement_relation_passed"] is True

    velocity = surface["cone_velocity_m_per_s"]
    assert velocity is not None
    velocity = np.asarray(velocity)
    assert velocity.ndim == 1
    assert velocity.shape == excursion.shape


def test_gdn13_cone_excursion_surface_preserves_non_claims() -> None:
    surface = get_gdn13_cone_excursion_output_surface_for_opt()

    assert surface["full_band_spl_claim"] is False
    assert surface["mouth_only_spl_claim"] is False


def test_gdn13_cone_excursion_surface_does_not_mutate_original_packet_model_dict() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    original_model_dict = packet["model_dict"]
    before = deepcopy(original_model_dict)

    surface = get_gdn13_cone_excursion_output_surface_for_opt(model_packet=packet)

    assert surface["output_contract_status"] == "passed"
    assert original_model_dict == before
    assert "observations" not in original_model_dict or original_model_dict["observations"] == before.get("observations")


def test_gdn13_cone_excursion_surface_model_packet_remains_solver_facing() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    frequency_hz = _bounded_frequency_subset(packet)

    surface = get_gdn13_cone_excursion_output_surface_for_opt(
        model_packet=packet,
        frequencies_hz=frequency_hz,
    )

    assert surface["output_contract_status"] == "passed"
    result = run_simulation(packet["model_dict"], frequency_hz)
    assert hasattr(result, "zin_complex_ohm")
    assert "spl_total_diagnostic" in result.series
    spl_total = np.asarray(result.series["spl_total_diagnostic"])
    assert spl_total.shape == frequency_hz.shape
    assert np.all(np.isfinite(spl_total))


def _stable_collection_projection(items):
    if not isinstance(items, list):
        return []
    semantic_keys = (
        "id",
        "type",
        "kind",
        "target",
        "node",
        "node_a",
        "node_b",
        "front_node",
        "rear_node",
        "from",
        "to",
        "source",
        "length",
        "length_cm",
        "length_m",
        "area",
        "area_cm2",
        "area_m2",
        "area_a_cm2",
        "area_b_cm2",
        "area_a_m2",
        "area_b_m2",
        "profile",
        "radiation_space",
    )
    projected = []
    for item in items:
        if isinstance(item, dict):
            projected.append({k: deepcopy(item[k]) for k in semantic_keys if k in item})
    return sorted(projected, key=lambda record: repr((record.get("id"), record.get("type"), record)))


def _accepted_model_projection(model_dict):
    """Project actual repo model_dict keys without inventing a segments contract."""
    projection = {}
    for key in (
        "driver",
        "drivers",
        "elements",
        "nodes",
        "radiators",
        "radiation",
        "observations",
        "source",
        "sources",
    ):
        if key not in model_dict:
            continue
        value = model_dict[key]
        if isinstance(value, list):
            projection[key] = _stable_collection_projection(value)
        else:
            projection[key] = deepcopy(value)
    return projection


def test_gdn13_cone_excursion_surface_model_dict_matches_accepted_builder_projection() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    accepted = build_gdn13_offset_tqwt_model_dict(profile="parabolic")

    packet_projection = _accepted_model_projection(packet["model_dict"])
    accepted_projection = _accepted_model_projection(accepted)

    assert "driver" in packet_projection
    assert "driver" in accepted_projection
    assert packet_projection["driver"] == accepted_projection["driver"]

    shared_keys = sorted(set(packet_projection) & set(accepted_projection))
    assert shared_keys, "packet and accepted builder must share repo-truth model_dict keys"

    # Compare only actual repo keys. In particular, do not require an invented
    # 'segments' top-level key: the accepted GDN13 model_dict currently uses its
    # own solver-facing structure.
    for key in shared_keys:
        assert packet_projection[key] == accepted_projection[key]


def test_gdn13_cone_excursion_export_alias_matches_primary_callable_contract() -> None:
    primary = get_gdn13_cone_excursion_output_surface_for_opt()
    alias = export_gdn13_cone_excursion_output_surface_for_opt()

    assert alias["output_contract_status"] == primary["output_contract_status"] == "passed"
    assert alias["case_id"] == primary["case_id"] == "gdn13_offset_tqwt"
    assert alias["driver_id"] == primary["driver_id"] == "drv_gdn13"


def test_gdn13_cone_excursion_surface_contains_no_fallback_or_resonator_semantics() -> None:
    surface = get_gdn13_cone_excursion_output_surface_for_opt()

    serialized_keys = " ".join(sorted(surface.keys())).lower()
    assert "fallback" not in serialized_keys
    assert "resonator" not in serialized_keys
