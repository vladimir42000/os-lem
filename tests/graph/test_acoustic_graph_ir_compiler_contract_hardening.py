"""Contract-hardening tests for the v0.9.0 acoustic graph IR compiler.

These tests deliberately exercise compiler-boundary behavior only. They do not
run the solver, do not add a second topology anchor, and do not claim external
HornResp parity.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from os_lem.acoustic_graph_ir import (
    AcousticGraphCompileResult,
    compile_acoustic_graph_ir_to_model_dict,
    validate_acoustic_graph_ir,
)


def _generic_non_gdn_graph() -> dict[str, Any]:
    """Return a small compiler-contract fixture that is not the GDN13 anchor."""

    return {
        "metadata": {
            "name": "generic_compiler_contract_fixture",
            "purpose": "compiler-contract-hardening-only",
        },
        "nodes": [
            {"id": "driver_front"},
            {"id": "driver_rear"},
            {"id": "closed_end"},
            {"id": "mouth"},
        ],
        "elements": [
            {
                "id": "generic_driver",
                "type": "electrodynamic_driver",
                "front_node": "driver_front",
                "rear_node": "driver_rear",
                "parameters": {
                    "Sd_cm2": 80.0,
                    "Bl_Tm": 5.5,
                    "Cms_m_per_N": 8.0e-4,
                    "Rms": 0.65,
                    "Mmd_g": 7.25,
                    "Re_ohm": 6.2,
                    "Le_mH": 0.75,
                },
            },
            {
                "id": "rear_stub",
                "type": "horn_or_duct_segment",
                "node_a": "driver_rear",
                "node_b": "closed_end",
                "length_cm": 42.0,
                "area_a_cm2": 80.0,
                "area_b_cm2": 76.0,
                "profile": "conical",
                "segments": 8,
            },
            {"id": "closed_rear", "type": "closed_termination", "node": "closed_end"},
            {
                "id": "forward_line",
                "type": "horn_or_duct_segment",
                "node_a": "driver_rear",
                "node_b": "mouth",
                "length_cm": 85.0,
                "area_a_cm2": 80.0,
                "area_b_cm2": 95.0,
                "profile": "exponential",
                "segments": 12,
            },
            {
                "id": "mouth_radiation",
                "type": "radiation_load",
                "node": "mouth",
                "area_cm2": 95.0,
                "radiation_space": "2pi",
            },
        ],
    }


def _gdn13_graph() -> dict[str, Any]:
    """Return the accepted GDN13-shaped graph used only as a compatibility guard."""

    return {
        "metadata": {
            "name": "gdn13_offset_tqwt_graph_contract_guard",
            "purpose": "accepted-gdn13-graph-compiler-guard-only",
            "compiler_target": "existing_solver_model_dict",
            "emit_default_diagnostic_observations": True,
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
                    "Cms_m_per_N": 1.01e-3,
                    "Rms": 0.49,
                    "Mmd_g": 8.50,
                    "Le_mH": 1.00,
                    "Re_ohm": 6.50,
                },
            },
            {
                "id": "rear_closed_stub_s1_s2",
                "type": "horn_or_duct_segment",
                "node_a": "tap_s2",
                "node_b": "closed_s1",
                "length_cm": 55.80,
                "area_a_cm2": 98.06,
                "area_b_cm2": 96.00,
                "profile": "parabolic",
                "segments": 18,
            },
            {"id": "closed_s1_termination", "type": "closed_termination", "node": "closed_s1"},
            {
                "id": "forward_open_line_s2_s3",
                "type": "horn_or_duct_segment",
                "node_a": "tap_s2",
                "node_b": "mouth_s3",
                "length_cm": 106.46,
                "area_a_cm2": 98.06,
                "area_b_cm2": 102.00,
                "profile": "parabolic",
                "segments": 34,
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


def _normalize_projection(model_dict: dict[str, Any]) -> dict[str, Any]:
    """Return a stable bounded projection for deterministic compiler comparison."""

    return {
        "meta": model_dict.get("meta"),
        "nodes": model_dict.get("nodes"),
        "driver": model_dict.get("driver"),
        "elements": model_dict.get("elements"),
        "closed_terminations": model_dict.get("closed_terminations"),
        "observations": model_dict.get("observations"),
    }


def _compile(graph: dict[str, Any]) -> AcousticGraphCompileResult:
    result = compile_acoustic_graph_ir_to_model_dict(graph)
    assert hasattr(result, "is_success")
    assert hasattr(result, "errors")
    assert hasattr(result, "warnings")
    assert hasattr(result, "model_dict")
    assert hasattr(result, "compiled_node_count")
    assert hasattr(result, "compiled_element_count")
    assert hasattr(result, "compiled_element_ids")
    assert hasattr(result, "unsupported_element_ids")
    return result


def test_generic_non_gdn_graph_compiles_without_gdn13_specific_defaults() -> None:
    graph = _generic_non_gdn_graph()

    result = _compile(graph)

    assert result.is_success, result.errors
    assert result.model_dict is not None
    assert result.compiled_node_count == 4
    assert result.compiled_element_count == 5
    assert result.compiled_element_ids == [
        "generic_driver",
        "rear_stub",
        "closed_rear",
        "forward_line",
        "mouth_radiation",
    ]
    assert result.unsupported_element_ids == []
    assert result.model_dict["driver"]["id"] == "generic_driver"
    assert result.model_dict["driver"]["node_rear"] == "driver_rear"
    assert "gdn13" not in repr(result.model_dict).lower()
    assert "tap_s2" not in repr(result.model_dict)


def test_compiler_output_is_deterministic_for_repeated_equivalent_input() -> None:
    graph_a = _generic_non_gdn_graph()
    graph_b = deepcopy(graph_a)

    first = _compile(graph_a)
    second = _compile(graph_b)

    assert first.is_success and second.is_success
    assert first.compiled_node_count == second.compiled_node_count
    assert first.compiled_element_count == second.compiled_element_count
    assert first.compiled_element_ids == second.compiled_element_ids
    assert first.unsupported_element_ids == second.unsupported_element_ids
    assert _normalize_projection(first.model_dict or {}) == _normalize_projection(second.model_dict or {})


@pytest.mark.parametrize(
    "mutator, expected_substring",
    [
        (
            lambda graph: graph["nodes"].append({"id": "driver_rear"}),
            "duplicate node id",
        ),
        (
            lambda graph: graph["elements"][1].update({"type": "unknown_primitive"}),
            "unknown element type",
        ),
        (
            lambda graph: graph["elements"][1].pop("length_cm"),
            "length requires exactly one",
        ),
        (
            lambda graph: graph["elements"][1].update({"length_m": 0.42}),
            "length is ambiguous",
        ),
        (
            lambda graph: graph["elements"][-1].update({"radiation_space": "4pi"}),
            "unsupported radiation_space",
        ),
        (
            lambda graph: graph["elements"][1].update({"profile": "made_up_profile"}),
            "unsupported horn_or_duct_segment profile",
        ),
        (
            lambda graph: graph["elements"][1].update({"node_b": "missing_node"}),
            "references unknown node",
        ),
    ],
)
def test_structured_failure_cases_return_errors_without_model_dict(mutator, expected_substring: str) -> None:
    graph = _generic_non_gdn_graph()
    mutator(graph)

    result = _compile(graph)

    assert not result.is_success
    assert result.model_dict is None
    assert result.errors
    assert any(expected_substring in error for error in result.errors), result.errors


def test_acoustic_chamber_is_structurally_valid_but_compile_blocked() -> None:
    graph = _generic_non_gdn_graph()
    graph["elements"].append(
        {
            "id": "structural_chamber_without_compiler_target",
            "type": "acoustic_chamber",
            "node": "driver_front",
            "volume_l": 1.25,
        }
    )

    validation = validate_acoustic_graph_ir(graph)
    result = _compile(graph)

    assert validation.is_valid, validation.errors
    assert not result.is_success
    assert result.model_dict is None
    assert result.unsupported_element_ids == ["structural_chamber_without_compiler_target"]
    assert any("acoustic_chamber has no accepted compiler target yet" in error for error in result.errors)


def test_unsupported_element_combination_two_drivers_fails_explicitly() -> None:
    graph = _generic_non_gdn_graph()
    second_driver = deepcopy(graph["elements"][0])
    second_driver["id"] = "second_driver_not_supported_by_skeleton"
    graph["elements"].insert(1, second_driver)

    validation = validate_acoustic_graph_ir(graph)
    result = _compile(graph)

    assert validation.is_valid, validation.errors
    assert not result.is_success
    assert result.model_dict is None
    assert any("supports exactly one electrodynamic_driver" in error for error in result.errors)


def test_missing_required_driver_field_fails_without_gdn13_fallback() -> None:
    graph = _generic_non_gdn_graph()
    graph["elements"][0]["parameters"].pop("Sd_cm2")

    result = _compile(graph)

    assert not result.is_success
    assert result.model_dict is None
    assert any("parameters.Sd requires exactly one" in error for error in result.errors)
    assert "82" not in repr(result.errors)


def test_compiler_only_paths_do_not_call_solver(monkeypatch: pytest.MonkeyPatch) -> None:
    import os_lem.api as api

    def fail_if_called(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - only called on defect
        raise AssertionError("compiler contract hardening must not call run_simulation")

    monkeypatch.setattr(api, "run_simulation", fail_if_called)

    result = _compile(_generic_non_gdn_graph())

    assert result.is_success, result.errors
    assert result.model_dict is not None


def test_accepted_gdn13_graph_compiler_behavior_is_not_weakened() -> None:
    graph = _gdn13_graph()

    validation = validate_acoustic_graph_ir(graph)
    result = _compile(graph)

    assert validation.is_valid, validation.errors
    assert result.is_success, result.errors
    assert result.model_dict is not None
    assert result.compiled_node_count == 4
    assert result.compiled_element_count == 5
    assert result.compiled_element_ids == [
        "gdn13_driver",
        "rear_closed_stub_s1_s2",
        "closed_s1_termination",
        "forward_open_line_s2_s3",
        "mouth_s3_radiation",
    ]
    assert result.unsupported_element_ids == []
    assert result.model_dict["driver"]["id"] == "gdn13_driver"
    assert {element["id"] for element in result.model_dict["elements"]} >= {
        "rear_closed_stub_s1_s2",
        "forward_open_line_s2_s3",
        "mouth_s3_radiation",
    }
    assert result.model_dict["meta"]["compiler_target"] == "existing_solver_model_dict"
