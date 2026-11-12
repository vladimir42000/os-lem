"""Diagnostic observations must reuse explicitly modeled radiation loads."""

from copy import deepcopy

import numpy as np
import pytest

from os_lem.acoustic_graph_ir import compile_acoustic_graph_ir_to_model_dict
from os_lem.api import run_simulation
from test_acoustic_graph_ir_compiler_skeleton import _gdn13_shaped_graph


def _graph(front_first=False):
    graph = _gdn13_shaped_graph()
    graph["metadata"].update(
        compiler_target="existing_solver_model_dict",
        emit_default_diagnostic_observations=True,
    )
    front = {
        "id": "explicit_front",
        "type": "radiation_load",
        "node": "driver_front",
        "area_cm2": 82.0,
        "radiation_space": "2pi",
    }
    graph["elements"].insert(0 if front_first else len(graph["elements"]), front)
    return graph


def _compile(graph):
    result = compile_acoustic_graph_ir_to_model_dict(graph)
    assert result.is_success, result.errors
    return result.model_dict


@pytest.mark.parametrize("front_first", [False, True])
def test_diagnostics_preserve_explicit_loads_and_impedance(front_first):
    graph = _graph(front_first)
    diagnostic = _compile(graph)
    graph["metadata"]["emit_default_diagnostic_observations"] = False
    plain = _compile(graph)
    assert diagnostic["elements"] == plain["elements"]
    observations = {item["id"]: item for item in diagnostic["observations"]}
    assert observations["spl_mouth"]["target"] == "mouth_s3_radiation"
    assert [term["target"] for term in observations["spl_total_diagnostic"]["terms"]] == [
        "explicit_front", "mouth_s3_radiation",
    ]
    # Same observation on both models isolates the physical loading change.
    plain["observations"] = deepcopy(diagnostic["observations"])
    frequencies = np.geomspace(20.0, 1000.0, 81)
    actual = run_simulation(diagnostic, frequencies)
    expected = run_simulation(plain, frequencies)
    np.testing.assert_allclose(actual.zin_complex_ohm, expected.zin_complex_ohm, rtol=1e-12, atol=1e-12)
    for key in expected.series:
        np.testing.assert_allclose(actual.series[key], expected.series[key], rtol=1e-12, atol=1e-12)


def test_legacy_graph_without_front_load_keeps_diagnostic_fallback():
    graph = _gdn13_shaped_graph()
    graph["metadata"].update(
        compiler_target="existing_solver_model_dict",
        emit_default_diagnostic_observations=True,
    )
    model = _compile(graph)
    front = [e for e in model["elements"] if e.get("node") == "driver_front"]
    assert len(front) == 1
    assert front[0]["id"] == "driver_front_radiation_diagnostic"
    assert front[0]["model"] == "infinite_baffle_piston"


def test_front_only_graph_cannot_mislabel_front_as_mouth():
    graph = _graph()
    graph["elements"] = [e for e in graph["elements"] if e["id"] != "mouth_s3_radiation"]
    result = compile_acoustic_graph_ir_to_model_dict(graph)
    assert not result.is_success
    assert any("mouth" in error for error in result.errors)


def test_ambiguous_front_targets_return_a_compile_error():
    graph = _graph()
    duplicate = deepcopy(graph["elements"][-1])
    duplicate["id"] = "another_front"
    graph["elements"].append(duplicate)
    result = compile_acoustic_graph_ir_to_model_dict(graph)
    assert not result.is_success
    assert result.model_dict is None
    assert any("exactly one driver-front" in error for error in result.errors)
