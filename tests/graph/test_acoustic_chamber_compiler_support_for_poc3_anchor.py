"""Focused acoustic_chamber compiler-support tests for the POC3 anchor path.

These tests cover only volume-only compiler support for the already-approved
acoustic_chamber graph IR primitive. They do not run POC3, do not call the
solver, and do not claim POC3 construction equivalence or parity.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from os_lem.acoustic_graph_ir import (
    compile_acoustic_graph_ir_to_model_dict,
    validate_acoustic_graph_ir,
)


def _driver_element() -> dict[str, Any]:
    return {
        "id": "driver",
        "type": "electrodynamic_driver",
        "front_node": "driver_front",
        "rear_node": "driver_rear",
        "parameters": {
            "Sd_cm2": 82.0,
            "Bl_Tm": 6.16,
            "Cms_m_per_N": 1.01e-3,
            "Rms": 0.49,
            "Mmd_g": 8.50,
            "Re_ohm": 6.50,
            "Le_mH": 1.00,
        },
    }


def _minimal_chamber_graph(chamber: dict[str, Any]) -> dict[str, Any]:
    return {
        "metadata": {
            "name": "acoustic_chamber_compiler_support_fixture",
            "purpose": "compiler-support-for-approved-primitive-only",
        },
        "nodes": [
            {"id": "driver_front"},
            {"id": "driver_rear"},
            {"id": "rear_chamber_node"},
            {"id": "throat_chamber_node"},
        ],
        "elements": [
            _driver_element(),
            chamber,
        ],
    }


def _poc3_style_chamber_graph() -> dict[str, Any]:
    return {
        "metadata": {
            "name": "poc3_style_chamber_compiler_fixture",
            "purpose": "poc3-chamber-shape-compiler-support-only",
        },
        "nodes": [
            {"id": "driver_front"},
            {"id": "driver_rear"},
            {"id": "rear_chamber_node"},
            {"id": "throat_chamber_node"},
        ],
        "elements": [
            _driver_element(),
            {
                "id": "poc3_rear_chamber",
                "type": "acoustic_chamber",
                "node": "driver_rear",
                "volume_l": 7.5,
                "metadata": {"poc3_anchor_role": "rear_chamber"},
            },
            {
                "id": "poc3_throat_chamber",
                "type": "acoustic_chamber",
                "node": "throat_chamber_node",
                "volume_m3": 0.00125,
                "metadata": {"poc3_anchor_role": "throat_chamber"},
            },
        ],
    }


def _compile(graph: dict[str, Any]):
    validation = validate_acoustic_graph_ir(graph)
    result = compile_acoustic_graph_ir_to_model_dict(graph)
    return validation, result


def test_acoustic_chamber_with_volume_l_compiles_successfully() -> None:
    graph = _minimal_chamber_graph(
        {
            "id": "rear_chamber",
            "type": "acoustic_chamber",
            "node": "driver_rear",
            "volume_l": 1.25,
        }
    )

    validation, result = _compile(graph)

    assert validation.is_valid, validation.errors
    assert result.is_success, result.errors
    assert result.unsupported_element_ids == []
    assert result.compiled_element_ids == ["driver", "rear_chamber"]
    assert result.model_dict is not None
    chamber = result.model_dict["acoustic_chambers"][0]
    assert chamber["id"] == "rear_chamber"
    assert chamber["type"] == "acoustic_chamber"
    assert chamber["node"] == "driver_rear"
    assert chamber["volume"] == "0.00125 m3"
    assert chamber["volume_m3"] == pytest.approx(0.00125)
    assert chamber["volume_l"] == pytest.approx(1.25)
    assert chamber["compiler_semantics"] == "volume_only_structural_chamber"


def test_acoustic_chamber_with_volume_m3_compiles_successfully() -> None:
    graph = _minimal_chamber_graph(
        {
            "id": "throat_chamber",
            "type": "acoustic_chamber",
            "node": "throat_chamber_node",
            "volume_m3": 0.0025,
        }
    )

    _validation, result = _compile(graph)

    assert result.is_success, result.errors
    assert result.model_dict is not None
    chamber = result.model_dict["acoustic_chambers"][0]
    assert chamber["id"] == "throat_chamber"
    assert chamber["node"] == "throat_chamber_node"
    assert chamber["volume_m3"] == pytest.approx(0.0025)
    assert chamber["volume_l"] == pytest.approx(2.5)


def test_compiled_chamber_output_preserves_id_node_type_and_volume() -> None:
    graph = _minimal_chamber_graph(
        {
            "id": "preserved_chamber",
            "type": "acoustic_chamber",
            "node": "driver_rear",
            "volume_l": 3.0,
        }
    )

    _validation, result = _compile(graph)

    assert result.is_success, result.errors
    assert result.model_dict is not None
    assert result.compiled_element_count == 2
    chamber = result.model_dict["acoustic_chambers"][0]
    assert chamber["source_graph_element_id"] == "preserved_chamber"
    assert set(chamber) >= {
        "id",
        "type",
        "node",
        "volume",
        "volume_m3",
        "volume_l",
        "compiler_semantics",
        "source_graph_element_id",
    }


def test_poc3_style_rear_and_throat_chamber_fixture_compiles_structurally() -> None:
    graph = _poc3_style_chamber_graph()

    validation, result = _compile(graph)

    assert validation.is_valid, validation.errors
    assert result.is_success, result.errors
    assert result.model_dict is not None
    assert result.compiled_element_ids == ["driver", "poc3_rear_chamber", "poc3_throat_chamber"]
    assert result.compiled_element_count == 3
    chambers = {item["id"]: item for item in result.model_dict["acoustic_chambers"]}
    assert chambers["poc3_rear_chamber"]["node"] == "driver_rear"
    assert chambers["poc3_rear_chamber"]["volume_l"] == pytest.approx(7.5)
    assert chambers["poc3_throat_chamber"]["node"] == "throat_chamber_node"
    assert chambers["poc3_throat_chamber"]["volume_l"] == pytest.approx(1.25)


@pytest.mark.parametrize(
    "mutator, expected_substring",
    [
        (
            lambda chamber: chamber.pop("volume_l"),
            "volume requires exactly one",
        ),
        (
            lambda chamber: chamber.update({"volume_l": 0.0}),
            "volume.volume_l must be a positive number",
        ),
        (
            lambda chamber: chamber.update({"volume_m3": 0.001}),
            "volume is ambiguous",
        ),
        (
            lambda chamber: chamber.update({"node": "missing_chamber_node"}),
            "references unknown node",
        ),
    ],
)
def test_invalid_chamber_volume_or_node_fails_explicitly(mutator, expected_substring: str) -> None:
    chamber = {
        "id": "invalid_chamber",
        "type": "acoustic_chamber",
        "node": "driver_rear",
        "volume_l": 1.25,
    }
    mutator(chamber)
    graph = _minimal_chamber_graph(chamber)

    validation, result = _compile(graph)

    assert not validation.is_valid
    assert not result.is_success
    assert result.model_dict is None
    assert any(expected_substring in error for error in result.errors), result.errors


def test_unsupported_chamber_feature_is_warned_not_silently_interpreted() -> None:
    graph = _minimal_chamber_graph(
        {
            "id": "chamber_with_unsupported_feature",
            "type": "acoustic_chamber",
            "node": "driver_rear",
            "volume_l": 1.25,
            "stuffing_density": 0.15,
        }
    )

    validation, result = _compile(graph)

    assert validation.is_valid, validation.errors
    assert result.is_success, result.errors
    assert any("stuffing_density" in warning for warning in result.warnings)
    assert result.model_dict is not None
    chamber = result.model_dict["acoustic_chambers"][0]
    assert "stuffing_density" not in chamber
    assert chamber["compiler_semantics"] == "volume_only_structural_chamber"


def test_compiler_only_chamber_paths_do_not_call_solver(monkeypatch: pytest.MonkeyPatch) -> None:
    import os_lem.api as api

    def fail_if_called(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - defect guard
        raise AssertionError("acoustic_chamber compiler support must not call run_simulation")

    monkeypatch.setattr(api, "run_simulation", fail_if_called)

    _validation, result = _compile(_poc3_style_chamber_graph())

    assert result.is_success, result.errors
    assert result.model_dict is not None



def test_chamber_graph_cannot_emit_solver_target_until_chamber_solver_mapping_is_approved() -> None:
    graph = _poc3_style_chamber_graph()
    graph["metadata"]["compiler_target"] = "existing_solver_model_dict"

    validation, result = _compile(graph)

    assert validation.is_valid, validation.errors
    assert not result.is_success
    assert result.model_dict is None
    assert any("does not yet support acoustic_chamber solver emission" in error for error in result.errors), result.errors
    assert any("acoustic_chamber" in error for error in result.errors), result.errors


def test_existing_gdn13_style_graph_without_chambers_remains_compilable() -> None:
    graph = {
        "metadata": {
            "name": "gdn13_guard_without_chambers",
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
                    "Re_ohm": 6.50,
                    "Le_mH": 1.00,
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

    first = compile_acoustic_graph_ir_to_model_dict(deepcopy(graph))
    second = compile_acoustic_graph_ir_to_model_dict(deepcopy(graph))

    assert first.is_success, first.errors
    assert second.is_success, second.errors
    assert first == second
    assert first.model_dict is not None
    assert "acoustic_chambers" not in first.model_dict
