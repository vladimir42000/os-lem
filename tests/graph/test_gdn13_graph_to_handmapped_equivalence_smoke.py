"""GDN13 graph-to-handmapped construction equivalence smoke.

This test is intentionally construction-level only.  It verifies that the
v0.9.0 acoustic graph IR validator/compiler path can express the accepted
GDN13 offset-driver TQWT construction and match the already accepted
hand-mapped model construction on a bounded semantic projection.

It does not run the solver, does not claim SPL parity, and does not replace
the accepted hand-mapped GDN13 reference path.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

import pytest

from os_lem.acoustic_graph_ir import (
    compile_acoustic_graph_ir_to_model_dict,
    validate_acoustic_graph_ir,
)
from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    build_gdn13_offset_tqwt_model_dict,
    gdn13_hornresp_driver_derived_parameters,
)


_NODE_ALIASES = {
    "driver_front": "driver_front",
    "tap_s2": "tap_s2",
    "closed_s1": "closed_end_s1",
    "closed_end_s1": "closed_end_s1",
    "mouth_s3": "mouth_s3",
}


def _accepted_gdn13_graph_ir() -> dict[str, Any]:
    return {
        "metadata": {
            "name": "gdn13_offset_tqwt_graph_to_handmapped_equivalence_smoke",
            "case_id": "gdn13_offset_tqwt",
            "construction_equivalence_only": True,
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


def _compile_graph_model() -> dict[str, Any]:
    result = compile_acoustic_graph_ir_to_model_dict(_accepted_gdn13_graph_ir())
    assert result.is_success is True
    assert result.model_dict is not None
    return result.model_dict


def _handmapped_model() -> dict[str, Any]:
    return build_gdn13_offset_tqwt_model_dict(profile="parabolic")


def _by_id(items: list[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {str(item["id"]): item for item in items}


def _float_quantity(value: Any) -> float:
    """Parse the numeric prefix of existing os-lem quantity strings."""

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        return float(value.split()[0])
    raise TypeError(f"unsupported quantity value: {value!r}")


def _canonical_node(node_id: str) -> str:
    return _NODE_ALIASES.get(node_id, node_id)


def _segment_projection(segment: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": segment["id"],
        "profile": segment["profile"],
        "length_m": _float_quantity(segment["length"]),
        "area_by_node_m2": {
            _canonical_node(str(segment["node_a"])): _float_quantity(segment["area_start"]),
            _canonical_node(str(segment["node_b"])): _float_quantity(segment["area_end"]),
        },
        "nodes": {_canonical_node(str(segment["node_a"])), _canonical_node(str(segment["node_b"]))},
    }


def _driver_projection_from_graph(model: Mapping[str, Any]) -> dict[str, Any]:
    driver = model["driver"]
    parameters = driver["parameters"]
    return {
        "node_front": _canonical_node(driver["node_front"]),
        "node_rear": _canonical_node(driver["node_rear"]),
        "Sd_m2": parameters["Sd_m2"],
        "Bl_Tm": parameters["Bl_Tm"],
        "Cms_m_per_N": parameters["Cms_m_per_N"],
        "Rms_Ns_per_m": parameters["Rms_Ns_per_m"],
        "Mmd_kg": parameters["Mmd_kg"],
        "Le_H": parameters["Le_H"],
        "Re_ohm": parameters["Re_ohm"],
    }


def _driver_projection_from_handmapped(model: Mapping[str, Any]) -> dict[str, Any]:
    driver = model["driver"]
    authority = gdn13_hornresp_driver_derived_parameters()
    return {
        "node_front": _canonical_node(driver["node_front"]),
        "node_rear": _canonical_node(driver["node_rear"]),
        "Sd_m2": authority.sd_cm2 * 1.0e-4,
        "Bl_Tm": authority.bl_tm,
        "Cms_m_per_N": authority.cms_m_per_n,
        "Rms_Ns_per_m": authority.rms_mechanical,
        "Mmd_kg": authority.mmd_g * 1.0e-3,
        "Le_H": authority.le_mh * 1.0e-3,
        "Re_ohm": authority.re_ohm,
    }


def _assert_close(actual: float, expected: float, *, rel: float = 1.0e-12, abs_: float = 1.0e-12) -> None:
    assert math.isclose(actual, expected, rel_tol=rel, abs_tol=abs_), (actual, expected)


def test_gdn13_graph_validates_and_compiles_structurally() -> None:
    graph = _accepted_gdn13_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    compile_result = compile_acoustic_graph_ir_to_model_dict(graph)

    assert validation.is_valid is True
    assert validation.node_count == 4
    assert validation.element_count == 5
    assert set(validation.supported_element_types_seen) == {
        "electrodynamic_driver",
        "horn_or_duct_segment",
        "closed_termination",
        "radiation_load",
    }
    assert compile_result.is_success is True
    assert compile_result.model_dict is not None
    assert compile_result.compiled_element_ids == [
        "drv_gdn13",
        "rear_closed_stub_s1_to_s2",
        "closed_s1_termination",
        "forward_open_line_s2_to_s3",
        "mouth_s3_radiation",
    ]


def test_handmapped_gdn13_model_construction_loads_without_solver_execution(monkeypatch) -> None:
    import os_lem.api as api
    import os_lem.reference_gdn13_offset_tqwt_mapping_trial as gdn13_reference

    def fail_if_called(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - must not execute
        raise AssertionError("construction equivalence smoke must not call run_simulation")

    monkeypatch.setattr(api, "run_simulation", fail_if_called)
    monkeypatch.setattr(gdn13_reference, "run_simulation", fail_if_called)

    graph_model = _compile_graph_model()
    handmapped = _handmapped_model()

    assert graph_model["meta"]["compiler_skeleton"] is True
    assert handmapped["meta"]["name"] == "gdn13_offset_tqwt_hornresp_mapping_trial"


def test_graph_compiled_driver_parameters_match_handmapped_authority() -> None:
    graph_driver = _driver_projection_from_graph(_compile_graph_model())
    hand_driver = _driver_projection_from_handmapped(_handmapped_model())

    assert graph_driver["node_front"] == hand_driver["node_front"] == "driver_front"
    assert graph_driver["node_rear"] == hand_driver["node_rear"] == "tap_s2"
    for key in ("Sd_m2", "Bl_Tm", "Cms_m_per_N", "Rms_Ns_per_m", "Mmd_kg", "Le_H", "Re_ohm"):
        _assert_close(float(graph_driver[key]), float(hand_driver[key]))


def test_graph_compiled_rear_and_forward_sections_match_handmapped_projection() -> None:
    graph_elements = _by_id(_compile_graph_model()["elements"])
    hand_elements = _by_id(_handmapped_model()["elements"])

    graph_rear = _segment_projection(graph_elements["rear_closed_stub_s1_to_s2"])
    hand_rear = _segment_projection(hand_elements["rear_closed_stub_s1_to_s2"])
    assert graph_rear["profile"] == hand_rear["profile"] == "parabolic"
    assert graph_rear["nodes"] == hand_rear["nodes"] == {"tap_s2", "closed_end_s1"}
    _assert_close(graph_rear["length_m"], hand_rear["length_m"])
    _assert_close(graph_rear["area_by_node_m2"]["tap_s2"], hand_rear["area_by_node_m2"]["tap_s2"])
    _assert_close(graph_rear["area_by_node_m2"]["closed_end_s1"], hand_rear["area_by_node_m2"]["closed_end_s1"])

    graph_forward = _segment_projection(graph_elements["forward_open_line_s2_to_s3"])
    hand_forward = _segment_projection(hand_elements["forward_open_line_s2_to_s3"])
    assert graph_forward["profile"] == hand_forward["profile"] == "parabolic"
    assert graph_forward["nodes"] == hand_forward["nodes"] == {"tap_s2", "mouth_s3"}
    _assert_close(graph_forward["length_m"], hand_forward["length_m"])
    _assert_close(graph_forward["area_by_node_m2"]["tap_s2"], hand_forward["area_by_node_m2"]["tap_s2"])
    _assert_close(graph_forward["area_by_node_m2"]["mouth_s3"], hand_forward["area_by_node_m2"]["mouth_s3"])


def test_graph_compiled_closed_termination_and_mouth_radiation_match_handmapped_projection() -> None:
    graph_model = _compile_graph_model()
    handmapped = _handmapped_model()
    graph_elements = _by_id(graph_model["elements"])
    hand_elements = _by_id(handmapped["elements"])

    assert graph_model["closed_terminations"] == [
        {
            "id": "closed_s1_termination",
            "type": "closed_termination",
            "node": "closed_s1",
            "structural_only": True,
            "source_graph_element_id": "closed_s1_termination",
        }
    ]
    hand_rear = _segment_projection(hand_elements["rear_closed_stub_s1_to_s2"])
    assert _canonical_node(graph_model["closed_terminations"][0]["node"]) == "closed_end_s1"
    assert "closed_end_s1" in hand_rear["nodes"]

    graph_radiation = graph_elements["mouth_s3_radiation"]
    hand_radiation = hand_elements["mouth_s3_radiation"]
    assert _canonical_node(graph_radiation["node"]) == _canonical_node(hand_radiation["node"]) == "mouth_s3"
    _assert_close(_float_quantity(graph_radiation["area"]), _float_quantity(hand_radiation["area"]))
    assert graph_radiation["radiation_space"] == "2pi"

    observations_by_id = _by_id(handmapped["observations"])
    assert observations_by_id["spl_mouth"]["target"] == "mouth_s3_radiation"
    assert observations_by_id["spl_mouth"]["radiation_space"] == "2pi"


def test_bounded_projection_is_used_instead_of_raw_dictionary_equality() -> None:
    graph_model = _compile_graph_model()
    handmapped = _handmapped_model()

    assert graph_model != handmapped
    assert graph_model["meta"]["non_claims"] == [
        "compiler skeleton only",
        "no solver execution from graph IR",
        "no graph-defined parity claim",
    ]
    assert "observations" in handmapped
    assert graph_model["observations"] == []


def test_no_solver_called_by_graph_to_handmapped_equivalence_path(monkeypatch) -> None:
    import os_lem.api as api
    import os_lem.reference_gdn13_offset_tqwt_mapping_trial as gdn13_reference

    def fail_if_called(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - must not execute
        raise AssertionError("graph-to-handmapped construction equivalence must not call solver")

    monkeypatch.setattr(api, "run_simulation", fail_if_called)
    monkeypatch.setattr(gdn13_reference, "run_simulation", fail_if_called)

    graph_model = _compile_graph_model()
    handmapped = _handmapped_model()

    assert graph_model["driver"]["id"] == "drv_gdn13"
    assert handmapped["driver"]["id"] == "drv_gdn13"
