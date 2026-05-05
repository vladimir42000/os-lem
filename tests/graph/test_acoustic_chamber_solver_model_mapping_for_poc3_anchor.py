"""Acoustic chamber solver-model mapping tests for the POC3 anchor path."""
from __future__ import annotations
from typing import Any, Mapping
import pytest
from os_lem.acoustic_graph_ir import compile_acoustic_graph_ir_to_model_dict, validate_acoustic_graph_ir

def _base_nodes() -> list[dict[str, str]]:
    return [{"id": "driver_front"}, {"id": "driver_rear"}, {"id": "rear_chamber_node"}, {"id": "throat_chamber_node"}, {"id": "mouth"}, {"id": "closed_end"}]

def _driver() -> dict[str, Any]:
    return {"id": "poc3_driver", "type": "electrodynamic_driver", "front_node": "driver_front", "rear_node": "driver_rear", "parameters": {"Sd_cm2": 82.0, "Bl_Tm": 6.16, "Cms_m_per_N": 1.01e-3, "Rms": 0.49, "Mmd_g": 8.50, "Re_ohm": 6.50, "Le_mH": 1.00}}

def _minimal_existing_solver_graph(chambers: list[dict[str, Any]]) -> dict[str, Any]:
    elements: list[dict[str, Any]] = [_driver()]
    elements.extend(chambers)
    elements.extend([
        {"id": "rear_stub", "type": "horn_or_duct_segment", "node_a": "driver_rear", "node_b": "closed_end", "length_cm": 20.0, "area_a_cm2": 80.0, "area_b_cm2": 80.0, "profile": "conical"},
        {"id": "closed_end_marker", "type": "closed_termination", "node": "closed_end"},
        {"id": "forward_horn", "type": "horn_or_duct_segment", "node_a": "driver_front", "node_b": "mouth", "length_cm": 40.0, "area_a_cm2": 80.0, "area_b_cm2": 120.0, "profile": "conical"},
        {"id": "mouth_radiation", "type": "radiation_load", "node": "mouth", "area_cm2": 120.0, "radiation_space": "2pi"},
    ])
    return {"metadata": {"name": "poc3_style_chamber_solver_model_mapping_contract", "compiler_target": "existing_solver_model_dict", "emit_default_diagnostic_observations": False}, "nodes": _base_nodes(), "elements": elements}

def _compile(graph: Mapping[str, Any]):
    return validate_acoustic_graph_ir(graph), compile_acoustic_graph_ir_to_model_dict(graph)

def _solver_chambers(model_dict: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(item) for item in model_dict.get("elements", []) if isinstance(item, Mapping) and item.get("type") == "acoustic_chamber"]

def _meta_chamber_records(model_dict: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(item) for item in model_dict.get("meta", {}).get("graph_compiled_acoustic_chambers", []) if isinstance(item, Mapping)]

def test_minimal_acoustic_chamber_maps_into_solver_facing_chamber_representation() -> None:
    graph = _minimal_existing_solver_graph([{"id": "rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_l": 7.5}])
    validation, compiled = _compile(graph)
    assert validation.is_valid is True, validation.errors
    assert compiled.is_success is True, compiled.errors
    assert _solver_chambers(compiled.model_dict) == [{"id": "rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume": "0.0075 m3"}]

def test_volume_l_maps_deterministically_to_canonical_solver_volume() -> None:
    graph = _minimal_existing_solver_graph([{"id": "rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_l": 12.25}])
    _, compiled = _compile(graph)
    assert compiled.is_success is True, compiled.errors
    assert _solver_chambers(compiled.model_dict)[0]["volume"] == "0.01225 m3"
    assert _meta_chamber_records(compiled.model_dict)[0]["volume_m3"] == pytest.approx(0.01225)

def test_volume_m3_maps_deterministically_to_canonical_solver_volume() -> None:
    graph = _minimal_existing_solver_graph([{"id": "rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_m3": 0.0034}])
    _, compiled = _compile(graph)
    assert compiled.is_success is True, compiled.errors
    assert _solver_chambers(compiled.model_dict)[0]["volume"] == "0.0034 m3"

@pytest.mark.parametrize("chamber, expected_fragment", [
    ({"id": "bad_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_l": 7.5, "volume_m3": 0.0075}, "ambiguous"),
    ({"id": "bad_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node"}, "requires exactly one"),
    ({"id": "bad_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_l": 0.0}, "positive"),
    ({"id": "bad_chamber", "type": "acoustic_chamber", "node": "unknown_node", "volume_l": 7.5}, "unknown node"),
])
def test_invalid_chamber_mapping_cases_fail_explicitly(chamber: dict[str, Any], expected_fragment: str) -> None:
    graph = _minimal_existing_solver_graph([chamber])
    validation, compiled = _compile(graph)
    assert validation.is_valid is False
    assert compiled.is_success is False
    assert expected_fragment in "\n".join([*validation.errors, *compiled.errors])

def test_poc3_style_rear_and_throat_chambers_map_to_solver_facing_records() -> None:
    graph = _minimal_existing_solver_graph([
        {"id": "poc3_rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_l": 7.5},
        {"id": "poc3_throat_chamber", "type": "acoustic_chamber", "node": "throat_chamber_node", "volume_m3": 0.00125},
    ])
    validation, compiled = _compile(graph)
    assert validation.is_valid is True, validation.errors
    assert compiled.is_success is True, compiled.errors
    chambers = sorted(_solver_chambers(compiled.model_dict), key=lambda item: item["id"])
    assert chambers == [
        {"id": "poc3_rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume": "0.0075 m3"},
        {"id": "poc3_throat_chamber", "type": "acoustic_chamber", "node": "throat_chamber_node", "volume": "0.00125 m3"},
    ]

def test_graph_compiled_chamber_mapping_matches_bounded_poc3_chamber_projection() -> None:
    graph = _minimal_existing_solver_graph([
        {"id": "poc3_rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_l": 7.5},
        {"id": "poc3_throat_chamber", "type": "acoustic_chamber", "node": "throat_chamber_node", "volume_m3": 0.00125},
    ])
    _, compiled = _compile(graph)
    records = sorted(_meta_chamber_records(compiled.model_dict), key=lambda item: item["id"])
    assert records[0]["volume_m3"] == pytest.approx(0.0075)
    assert records[1]["volume_m3"] == pytest.approx(0.00125)

def test_no_solver_call_occurs_from_chamber_solver_model_mapping(monkeypatch) -> None:
    import os_lem.api as api
    def fail_if_called(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("acoustic_chamber solver-model mapping must not call run_simulation")
    monkeypatch.setattr(api, "run_simulation", fail_if_called)
    graph = _minimal_existing_solver_graph([{"id": "rear_chamber", "type": "acoustic_chamber", "node": "rear_chamber_node", "volume_l": 7.5}])
    validation, compiled = _compile(graph)
    assert validation.is_valid is True, validation.errors
    assert compiled.is_success is True, compiled.errors
    assert _solver_chambers(compiled.model_dict)
