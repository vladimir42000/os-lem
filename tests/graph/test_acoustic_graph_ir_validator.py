from __future__ import annotations

from copy import deepcopy

from os_lem.acoustic_graph_ir import (
    AcousticGraphValidationResult,
    SUPPORTED_ELEMENT_TYPES,
    validate_acoustic_graph_ir,
)


def _gdn13_offset_tqwt_graph() -> dict:
    return {
        "metadata": {
            "case_id": "gdn13_offset_tqwt",
            "purpose": "structural validator anchor only",
        },
        "nodes": [
            {"id": "driver_front"},
            {"id": "tap_s2"},
            {"id": "closed_s1"},
            {"id": "mouth_s3"},
        ],
        "elements": [
            {
                "id": "gdn13_driver",
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
                "id": "rear_closed_stub_s2_to_s1",
                "type": "horn_or_duct_segment",
                "node_a": "tap_s2",
                "node_b": "closed_s1",
                "length_cm": 55.80,
                "area_a_cm2": 98.06,
                "area_b_cm2": 96.00,
                "profile": "parabolic",
            },
            {
                "id": "closed_end_s1",
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
                "id": "mouth_radiation_s3",
                "type": "radiation_load",
                "node": "mouth_s3",
                "area_cm2": 102.00,
                "radiation_space": "2pi",
            },
        ],
    }


def _validate(graph: dict) -> AcousticGraphValidationResult:
    return validate_acoustic_graph_ir(graph)


def test_valid_minimal_gdn13_shaped_graph_passes_structural_validation():
    result = _validate(_gdn13_offset_tqwt_graph())

    assert result.is_valid is True
    assert result.errors == []
    assert result.node_count == 4
    assert result.element_count == 5
    assert result.supported_element_types_seen == [
        "electrodynamic_driver",
        "horn_or_duct_segment",
        "closed_termination",
        "radiation_load",
    ]


def test_validation_result_exposes_expected_fields_and_supported_element_tokens():
    result = _validate(_gdn13_offset_tqwt_graph())

    assert hasattr(result, "is_valid")
    assert hasattr(result, "errors")
    assert hasattr(result, "warnings")
    assert hasattr(result, "node_count")
    assert hasattr(result, "element_count")
    assert hasattr(result, "supported_element_types_seen")
    assert set(SUPPORTED_ELEMENT_TYPES) == {
        "electrodynamic_driver",
        "horn_or_duct_segment",
        "closed_termination",
        "acoustic_chamber",
        "radiation_load",
    }


def test_duplicate_node_id_fails_with_clear_error():
    graph = _gdn13_offset_tqwt_graph()
    graph["nodes"].append({"id": "tap_s2"})

    result = _validate(graph)

    assert result.is_valid is False
    assert any("duplicate node id: tap_s2" in error for error in result.errors)


def test_duplicate_element_id_fails_with_clear_error():
    graph = _gdn13_offset_tqwt_graph()
    graph["elements"].append(deepcopy(graph["elements"][0]))

    result = _validate(graph)

    assert result.is_valid is False
    assert any("duplicate element id: gdn13_driver" in error for error in result.errors)


def test_unknown_element_type_fails_explicitly():
    graph = _gdn13_offset_tqwt_graph()
    graph["elements"][0]["type"] = "unbounded_magic_horn"

    result = _validate(graph)

    assert result.is_valid is False
    assert any("unknown element type" in error and "unbounded_magic_horn" in error for error in result.errors)


def test_unknown_referenced_node_fails_explicitly():
    graph = _gdn13_offset_tqwt_graph()
    graph["elements"][0]["front_node"] = "missing_front_node"

    result = _validate(graph)

    assert result.is_valid is False
    assert any("references unknown node: missing_front_node" in error for error in result.errors)


def test_missing_required_driver_field_fails_explicitly():
    graph = _gdn13_offset_tqwt_graph()
    del graph["elements"][0]["parameters"]["Re_ohm"]

    result = _validate(graph)

    assert result.is_valid is False
    assert any("Re_ohm is required" in error for error in result.errors)


def test_invalid_horn_profile_fails_explicitly():
    graph = _gdn13_offset_tqwt_graph()
    graph["elements"][1]["profile"] = "unsupported_freeform_profile"

    result = _validate(graph)

    assert result.is_valid is False
    assert any("unsupported horn_or_duct_segment profile" in error for error in result.errors)


def test_non_positive_length_or_area_fails_explicitly():
    graph = _gdn13_offset_tqwt_graph()
    graph["elements"][1]["length_cm"] = 0.0
    graph["elements"][1]["area_b_cm2"] = -1.0

    result = _validate(graph)

    assert result.is_valid is False
    assert any("length.length_cm must be a positive number" in error for error in result.errors)
    assert any("area_b.area_b_cm2 must be a positive number" in error for error in result.errors)


def test_unsupported_radiation_space_fails_explicitly():
    graph = _gdn13_offset_tqwt_graph()
    graph["elements"][-1]["radiation_space"] = "4pi"

    result = _validate(graph)

    assert result.is_valid is False
    assert any("unsupported radiation_space" in error and "4pi" in error for error in result.errors)


def test_empty_node_and_element_lists_fail():
    result = _validate({"nodes": [], "elements": []})

    assert result.is_valid is False
    assert any("nodes must not be empty" in error for error in result.errors)
    assert any("elements must not be empty" in error for error in result.errors)


def test_chamber_volume_must_be_positive_when_chamber_is_used():
    graph = {
        "nodes": [{"id": "chamber_node"}],
        "elements": [
            {
                "id": "front_chamber",
                "type": "acoustic_chamber",
                "node": "chamber_node",
                "volume_l": 0.0,
            }
        ],
    }

    result = _validate(graph)

    assert result.is_valid is False
    assert any("volume.volume_l must be a positive number" in error for error in result.errors)


def test_validator_does_not_call_solver(monkeypatch):
    from os_lem import api

    def _raise_if_called(*args, **kwargs):
        raise AssertionError("graph IR validator must not call run_simulation")

    monkeypatch.setattr(api, "run_simulation", _raise_if_called)

    result = _validate(_gdn13_offset_tqwt_graph())

    assert result.is_valid is True
