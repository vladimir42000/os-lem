"""Focused tests for the v0.9.0 acoustic graph IR compiler skeleton.

These tests verify only graph IR validation/compilation boundaries.  They do
not run the solver and do not claim graph-defined GDN13 parity.
"""

from __future__ import annotations

from copy import deepcopy

from os_lem.acoustic_graph_ir import (
    AcousticGraphCompileResult,
    compile_acoustic_graph_ir_to_model_dict,
)


def _gdn13_shaped_graph() -> dict:
    return {
        "metadata": {
            "name": "gdn13_offset_tqwt_graph_ir_structural_anchor",
            "case_id": "gdn13_offset_tqwt",
            "validation_anchor_only": True,
        },
        "nodes": [
            {"id": "driver_front"},
            {"id": "tap_s2"},
            {"id": "closed_s1"},
            {"id": "mouth_s3"},
        ],
        "elements": [
            {
                "id": "drv_gdn13",
                "type": "electrodynamic_driver",
                "front_node": "driver_front",
                "rear_node": "tap_s2",
                "parameters": {
                    "Sd_cm2": 82.00,
                    "Bl_Tm": 6.16,
                    "Cms_m_per_N": 1.01e-03,
                    "Rms": 0.49,
                    "Mmd_g": 8.50,
                    "Le_mH": 1.00,
                    "Re_ohm": 6.50,
                },
            },
            {
                "id": "rear_closed_stub_s1_to_s2",
                "type": "horn_or_duct_segment",
                "node_a": "tap_s2",
                "node_b": "closed_s1",
                "length_cm": 55.80,
                "area_a_cm2": 98.06,
                "area_b_cm2": 96.00,
                "profile": "parabolic",
            },
            {
                "id": "closed_s1_termination",
                "type": "closed_termination",
                "node": "closed_s1",
            },
            {
                "id": "forward_open_line_s2_to_s3",
                "type": "horn_or_duct_segment",
                "node_a": "tap_s2",
                "node_b": "mouth_s3",
                "length_cm": 106.46,
                "area_a_cm2": 98.06,
                "area_b_cm2": 102.00,
                "profile": "parabolic",
            },
            {
                "id": "mouth_s3_radiation",
                "type": "radiation_load",
                "node": "mouth_s3",
                "area_cm2": 102.00,
                "radiation_space": "2pi",
            },
        ],
    }


def test_valid_gdn13_shaped_graph_compiles_successfully() -> None:
    result = compile_acoustic_graph_ir_to_model_dict(_gdn13_shaped_graph())

    assert isinstance(result, AcousticGraphCompileResult)
    assert result.is_success is True
    assert result.errors == []
    assert result.model_dict is not None
    assert result.compiled_node_count == 4
    assert result.compiled_element_count == 5
    assert result.unsupported_element_ids == []
    assert result.compiled_element_ids == [
        "drv_gdn13",
        "rear_closed_stub_s1_to_s2",
        "closed_s1_termination",
        "forward_open_line_s2_to_s3",
        "mouth_s3_radiation",
    ]


def test_compiler_result_exposes_required_fields() -> None:
    result = compile_acoustic_graph_ir_to_model_dict(_gdn13_shaped_graph())

    assert hasattr(result, "is_success")
    assert hasattr(result, "errors")
    assert hasattr(result, "warnings")
    assert hasattr(result, "model_dict")
    assert hasattr(result, "compiled_node_count")
    assert hasattr(result, "compiled_element_count")
    assert hasattr(result, "compiled_element_ids")
    assert hasattr(result, "unsupported_element_ids")


def test_compiled_gdn13_graph_contains_expected_existing_model_skeleton() -> None:
    result = compile_acoustic_graph_ir_to_model_dict(_gdn13_shaped_graph())

    assert result.is_success is True
    model_dict = result.model_dict
    assert model_dict is not None
    assert model_dict["meta"]["compiler_skeleton"] is True
    assert model_dict["meta"]["acoustic_graph_ir_version"] == "v0.9.0"

    driver = model_dict["driver"]
    assert driver["id"] == "drv_gdn13"
    assert driver["node_front"] == "driver_front"
    assert driver["node_rear"] == "tap_s2"
    assert driver["parameters"]["Sd_m2"] == 82.00e-4
    assert driver["parameters"]["Mmd_kg"] == 8.50e-3
    assert driver["parameters"]["Le_H"] == 1.00e-3

    elements_by_id = {element["id"]: element for element in model_dict["elements"]}
    assert elements_by_id["rear_closed_stub_s1_to_s2"] == {
        "id": "rear_closed_stub_s1_to_s2",
        "type": "waveguide_1d",
        "node_a": "tap_s2",
        "node_b": "closed_s1",
        "length": "0.558 m",
        "area_start": "0.009806 m2",
        "area_end": "0.0096 m2",
        "profile": "parabolic",
        "source_graph_element_id": "rear_closed_stub_s1_to_s2",
    }
    assert elements_by_id["forward_open_line_s2_to_s3"]["length"] == "1.0646 m"
    assert elements_by_id["forward_open_line_s2_to_s3"]["area_end"] == "0.0102 m2"
    assert elements_by_id["mouth_s3_radiation"]["type"] == "radiator"
    assert elements_by_id["mouth_s3_radiation"]["radiation_space"] == "2pi"

    assert model_dict["closed_terminations"] == [
        {
            "id": "closed_s1_termination",
            "type": "closed_termination",
            "node": "closed_s1",
            "structural_only": True,
            "source_graph_element_id": "closed_s1_termination",
        }
    ]


def test_compilation_is_deterministic() -> None:
    graph = _gdn13_shaped_graph()
    first = compile_acoustic_graph_ir_to_model_dict(graph)
    second = compile_acoustic_graph_ir_to_model_dict(graph)

    assert first == second


def test_compiler_uses_validator_duplicate_node_graph_does_not_compile() -> None:
    graph = _gdn13_shaped_graph()
    graph["nodes"].append({"id": "tap_s2"})

    result = compile_acoustic_graph_ir_to_model_dict(graph)

    assert result.is_success is False
    assert result.model_dict is None
    assert any("graph validation failed before compilation" in error for error in result.errors)
    assert any("duplicate node id: tap_s2" in error for error in result.errors)


def test_unknown_element_type_does_not_compile() -> None:
    graph = _gdn13_shaped_graph()
    graph["elements"][1]["type"] = "arbitrary_branch_network"

    result = compile_acoustic_graph_ir_to_model_dict(graph)

    assert result.is_success is False
    assert result.model_dict is None
    assert any("unknown element type" in error for error in result.errors)


def test_structurally_valid_but_unsupported_acoustic_chamber_fails_explicitly() -> None:
    graph = _gdn13_shaped_graph()
    graph["elements"].append(
        {
            "id": "side_chamber_not_yet_compiled",
            "type": "acoustic_chamber",
            "node": "tap_s2",
            "volume_l": 1.25,
        }
    )

    result = compile_acoustic_graph_ir_to_model_dict(graph)

    assert result.is_success is False
    assert result.model_dict is None
    assert result.unsupported_element_ids == ["side_chamber_not_yet_compiled"]
    assert any("acoustic_chamber has no accepted compiler target yet" in error for error in result.errors)


def test_missing_unit_field_fails_explicitly() -> None:
    graph = _gdn13_shaped_graph()
    del graph["elements"][1]["length_cm"]

    result = compile_acoustic_graph_ir_to_model_dict(graph)

    assert result.is_success is False
    assert result.model_dict is None
    assert any("length requires exactly one" in error for error in result.errors)


def test_unsupported_radiation_space_fails() -> None:
    graph = _gdn13_shaped_graph()
    graph["elements"][-1]["radiation_space"] = "4pi"

    result = compile_acoustic_graph_ir_to_model_dict(graph)

    assert result.is_success is False
    assert result.model_dict is None
    assert any("unsupported radiation_space" in error for error in result.errors)


def test_compiler_rejects_graph_without_driver() -> None:
    graph = _gdn13_shaped_graph()
    graph["elements"] = [element for element in graph["elements"] if element["type"] != "electrodynamic_driver"]

    result = compile_acoustic_graph_ir_to_model_dict(graph)

    assert result.is_success is False
    assert result.model_dict is None
    assert any("requires exactly one electrodynamic_driver" in error for error in result.errors)


def test_compiler_does_not_call_solver(monkeypatch) -> None:
    import os_lem.api as api

    def fail_if_called(*args, **kwargs):  # pragma: no cover - should never execute
        raise AssertionError("graph compiler skeleton must not call run_simulation")

    monkeypatch.setattr(api, "run_simulation", fail_if_called)

    result = compile_acoustic_graph_ir_to_model_dict(_gdn13_shaped_graph())

    assert result.is_success is True
    assert result.model_dict is not None


def test_compiler_result_non_claims_do_not_claim_graph_defined_parity() -> None:
    result = compile_acoustic_graph_ir_to_model_dict(_gdn13_shaped_graph())

    assert result.is_success is True
    assert result.model_dict is not None
    non_claims = result.model_dict["meta"]["non_claims"]
    assert "no solver execution from graph IR" in non_claims
    assert "no graph-defined parity claim" in non_claims
