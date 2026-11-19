"""POC3 graph-versus-handmapped internal solver-equivalence regression.

Both paths represent the exact same five-element accepted POC3 model and run
through the same kernel on its existing 533-point reference frequency grid.
This checks graph construction and compiler mapping, not HornResp/Akabak
parity, external correctness, model replacement, or a released feature.

The accepted ``throat_chamber`` is a finite waveguide, not a distinct
volume-only acoustic_chamber element. No volumetric chamber is invented.
"""

from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import yaml

from os_lem.acoustic_graph_ir import (
    compile_acoustic_graph_ir_to_model_dict,
    validate_acoustic_graph_ir,
)
from os_lem.api import run_simulation
from os_lem.solve import radiator_observation_pressure, summed_radiator_observation_pressure


REPO_ROOT = Path(__file__).resolve().parents[2]
POC3_MODEL_PATH = REPO_ROOT / "proof" / "poc3_blh_benchmark_pass1" / "model.yaml"
POC3_FREQ_GRID_PATH = REPO_ROOT / "proof" / "poc3_blh_benchmark_pass1" / "source_inputs" / "poc3_hr_all.txt"
CONSTRUCTION_HELPER_PATH = REPO_ROOT / "tests" / "graph" / "test_poc3_blh_graph_to_handmapped_construction_equivalence_smoke.py"

REQUIRED_AUTHORITY_PATH = "proof/poc3_blh_benchmark_pass1/model.yaml"
GRAPH_VALIDATOR_CALLABLE = "os_lem.acoustic_graph_ir.validate_acoustic_graph_ir"
GRAPH_COMPILER_CALLABLE = "os_lem.acoustic_graph_ir.compile_acoustic_graph_ir_to_model_dict"
SOLVER_CALLABLE = "os_lem.api.run_simulation"

DIAGNOSTIC_CLASSIFICATION = "graph_defined_poc3_internal_solver_equivalence_regression"
SOLVER_EQUIVALENCE_STATUS = "established_for_accepted_poc3_internal_model_only"
CHAMBER_BEARING_PROOF_STATUS = "no_volume_only_chamber_in_accepted_poc3_authority"
POC3_NODES = ("front", "rear", "throat", "bend", "mouth")

# These tolerances are roundoff allowances for identical solver inputs, not
# limits fit to a mismatched model. The full grid includes near-cancellation
# of complex radiated pressures at some frequencies.
COMPLEX_RTOL = 1.0e-9
COMPLEX_ATOL = 1.0e-10
SPL_ATOL_DB = 1.0e-8


def _load_construction_helper_module():
    assert CONSTRUCTION_HELPER_PATH.exists(), (
        "missing accepted POC3 graph-to-handmapped construction-equivalence helper: "
        f"{CONSTRUCTION_HELPER_PATH}"
    )
    spec = importlib.util.spec_from_file_location(
        "_poc3_blh_graph_to_handmapped_construction_equivalence_smoke",
        CONSTRUCTION_HELPER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_poc3_authority_model() -> dict[str, Any]:
    assert POC3_MODEL_PATH.exists(), f"missing accepted POC3 authority model: {POC3_MODEL_PATH}"
    data = yaml.safe_load(POC3_MODEL_PATH.read_text())
    assert isinstance(data, dict), "POC3 model.yaml must load as a mapping"
    return data


def _accepted_poc3_graph_ir() -> dict[str, Any]:
    helper = _load_construction_helper_module()
    authority_model = helper._load_poc3_authority_model()
    graph = helper._poc3_graph_from_authority(authority_model)
    assert isinstance(graph, dict)
    metadata = dict(graph.get("metadata", {}))
    metadata.update(
        {
            "name": "poc3_graph_defined_solver_execution_diagnostic_smoke",
            "case_id": "poc3_blh_benchmark_pass1",
            "compiler_target": "existing_solver_model_dict",
            "emit_default_diagnostic_observations": True,
        }
    )
    return {**graph, "metadata": metadata}


def _handmapped_model_dict() -> dict[str, Any]:
    return deepcopy(_load_poc3_authority_model())


def _compiled_graph_model_dict() -> dict[str, Any]:
    graph = _accepted_poc3_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    assert validation.is_valid is True, validation.errors

    compiled = compile_acoustic_graph_ir_to_model_dict(graph)
    assert compiled.is_success is True, compiled.errors
    assert compiled.model_dict is not None
    return compiled.model_dict


def _load_reference_frequency_grid() -> np.ndarray:
    values: list[float] = []
    if POC3_FREQ_GRID_PATH.exists():
        for line in POC3_FREQ_GRID_PATH.read_text(errors="replace").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", ";")):
                continue
            first = stripped.replace(",", " ").split()[0]
            try:
                value = float(first)
            except ValueError:
                continue
            if np.isfinite(value) and value > 0.0:
                values.append(value)

    if not values:
        values = [20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0, 160.0, 250.0, 400.0, 630.0, 1000.0]

    grid = np.unique(np.asarray(values, dtype=float))
    assert grid.ndim == 1 and grid.size >= 8
    return grid


def _bounded_poc3_frequency_subset() -> np.ndarray:
    grid = _load_reference_frequency_grid()
    targets = np.asarray(
        [20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0, 160.0, 250.0, 400.0, 630.0, 1000.0],
        dtype=float,
    )
    in_range_targets = [target for target in targets if grid.min() <= target <= grid.max()]
    if len(in_range_targets) < 8:
        quantile_indices = np.linspace(0, grid.size - 1, num=min(12, grid.size), dtype=int)
        indices = sorted(set(int(index) for index in quantile_indices))
    else:
        indices = sorted({int(np.argmin(np.abs(grid - target))) for target in in_range_targets})
    subset = np.asarray(grid[indices], dtype=float)
    assert subset.ndim == 1
    assert 8 <= subset.size <= 16
    return subset


def _copy_authority_observations_if_needed(graph_model: dict[str, Any], handmapped_model: Mapping[str, Any]) -> dict[str, Any]:
    graph_copy = deepcopy(graph_model)
    authority_observations = handmapped_model.get("observations")
    if isinstance(authority_observations, list) and authority_observations:
        graph_copy["observations"] = deepcopy(authority_observations)
    return graph_copy


def _solver_result_projection(model_dict: dict[str, Any], frequency_hz: np.ndarray) -> dict[str, np.ndarray]:
    with_pressures = deepcopy(model_dict)
    with_pressures["observations"].extend(
        {"id": f"p_node_{node}", "type": "node_pressure", "target": node}
        for node in POC3_NODES
    )
    result = run_simulation(with_pressures, frequency_hz)
    assert result.zin_complex_ohm is not None
    projected: dict[str, np.ndarray] = {
        "frequency_hz": np.asarray(result.frequencies_hz, dtype=float),
        "zin_complex_ohm": np.asarray(result.zin_complex_ohm, dtype=complex),
    }
    for key, value in result.series.items():
        if "spl" in str(key).lower():
            projected[str(key)] = np.asarray(value, dtype=float)
        elif str(key).startswith("p_node_"):
            projected[str(key)] = np.asarray(value, dtype=complex)
    for radiator_id in ("front_rad", "mouth_rad"):
        projected[f"p_radiated_{radiator_id}"] = radiator_observation_pressure(
            result.sweep, result.system, radiator_id, 1.0, "2pi"
        )
    projected["p_radiated_total"] = summed_radiator_observation_pressure(
        result.sweep,
        result.system,
        [
            {"target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"target": "mouth_rad", "distance": "1 m", "radiation_space": "2pi"},
        ],
    )
    return projected


def _difference_summary(actual: np.ndarray, expected: np.ndarray) -> dict[str, float]:
    delta = np.asarray(actual) - np.asarray(expected)
    abs_delta = np.abs(delta)
    return {
        "max_abs": float(np.max(abs_delta)),
        "mean_abs": float(np.mean(abs_delta)),
    }


def _graph_chamber_records(model_dict: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(element)
        for element in model_dict.get("elements", [])
        if isinstance(element, Mapping) and element.get("type") == "acoustic_chamber"
    ]


def _equivalence_diagnostic_report() -> dict[str, Any]:
    handmapped_model = _handmapped_model_dict()
    graph_model = _copy_authority_observations_if_needed(_compiled_graph_model_dict(), handmapped_model)
    frequency_hz = _load_reference_frequency_grid()

    graph_result = _solver_result_projection(graph_model, frequency_hz)
    handmapped_result = _solver_result_projection(handmapped_model, frequency_hz)
    common_spl_fields = sorted(
        key
        for key in set(graph_result).intersection(handmapped_result)
        if "spl" in key.lower()
    )
    compared_fields = [
        "zin_complex_ohm",
        *(f"p_node_{node}" for node in POC3_NODES),
        "p_radiated_front_rad",
        "p_radiated_mouth_rad",
        "p_radiated_total",
        *common_spl_fields,
    ]
    differences: dict[str, dict[str, float]] = {}
    for field in compared_fields:
        differences[field] = _difference_summary(graph_result[field], handmapped_result[field])

    graph_chamber_records = _graph_chamber_records(graph_model)
    return {
        "diagnostic_classification": DIAGNOSTIC_CLASSIFICATION,
        "solver_execution_status": "passed",
        "solver_equivalence_status": SOLVER_EQUIVALENCE_STATUS,
        "chamber_bearing_proof_status": CHAMBER_BEARING_PROOF_STATUS,
        "authority_path": REQUIRED_AUTHORITY_PATH,
        "frequency_hz": frequency_hz.tolist(),
        "frequency_count": int(frequency_hz.size),
        "compared_solver_fields": ["frequency_hz", *compared_fields],
        "common_spl_fields": common_spl_fields,
        "differences": differences,
        "thresholds_used_for_equivalence": {
            "complex_relative": COMPLEX_RTOL,
            "complex_absolute_ohm_or_pa": COMPLEX_ATOL,
            "spl_absolute_db": SPL_ATOL_DB,
        },
        "threshold_rationale": "same accepted physical model and solver; double-precision roundoff only, including complex pressure cancellation",
        "graph_model_element_count": len(graph_model.get("elements", [])),
        "handmapped_model_element_count": len(handmapped_model.get("elements", [])) if isinstance(handmapped_model.get("elements"), list) else None,
        "graph_acoustic_chamber_count": len(graph_chamber_records),
        "graph_acoustic_chamber_records": graph_chamber_records,
        "graph_chamber_records_exposed": True,
        "numerical_differences_visible": True,
        "later_equivalence_alignment_required": False,
        "strict_bit_equivalence_claim": False,
        "solver_equivalence_claim": True,
        "hornresp_parity_claim": False,
        "akabak_parity_claim": False,
        "external_parity_claim": False,
        "handmapped_replacement_claim": False,
        "optimizer_or_studio_consumption_claim": False,
    }


def evaluate_poc3_graph_defined_solver_equivalence_smoke() -> dict[str, Any]:
    """Probe entrypoint kept for script compatibility; returns diagnostic report."""
    return _equivalence_diagnostic_report()


def test_poc3_graph_validates_compiles_and_preserves_five_physical_elements() -> None:
    graph = _accepted_poc3_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    compiled = compile_acoustic_graph_ir_to_model_dict(graph)

    assert validation.is_valid is True, validation.errors
    assert compiled.is_success is True, compiled.errors
    assert compiled.model_dict is not None
    assert compiled.model_dict["meta"]["compiler_target"] == "existing_solver_model_dict"
    authority = _handmapped_model_dict()
    graph_model = compiled.model_dict
    assert len(graph_model["elements"]) == len(authority["elements"]) == 5
    assert {item["id"] for item in graph_model["elements"]} == {item["id"] for item in authority["elements"]}
    for expected in authority["elements"]:
        actual = next(item for item in graph_model["elements"] if item["id"] == expected["id"])
        assert actual["type"] == expected["type"]
        if expected["type"] == "radiator":
            assert actual["node"] == expected["node"]
            assert actual["model"] == expected["model"] == "infinite_baffle_piston"
        else:
            assert (actual["node_a"], actual["node_b"]) == (expected["node_a"], expected["node_b"])
            assert actual["segments"] == expected["segments"]
    assert graph_model["driver"]["model"] == authority["driver"]["model"] == "em_explicit"
    assert graph_model["driver"]["Mms"] == authority["driver"]["Mms"]
    assert graph_model["driver"]["source_voltage_rms"] == authority["driver"]["source_voltage_rms"]
    assert _graph_chamber_records(graph_model) == []


def test_native_graph_diagnostic_observations_reuse_explicit_front_and_mouth_loads() -> None:
    graph_model = _compiled_graph_model_dict()
    observations = {item["id"]: item for item in graph_model["observations"]}
    assert observations["zin"] == {"id": "zin", "type": "input_impedance", "target": "drv1"}
    assert observations["spl_mouth"]["target"] == "mouth_rad"
    assert [term["target"] for term in observations["spl_total_diagnostic"]["terms"]] == ["front_rad", "mouth_rad"]
    assert {item["id"] for item in graph_model["elements"] if item["type"] == "radiator"} == {"front_rad", "mouth_rad"}

    frequency_hz = _load_reference_frequency_grid()
    native_graph_result = run_simulation(graph_model, frequency_hz)
    handmapped_result = run_simulation(_handmapped_model_dict(), frequency_hz)
    np.testing.assert_allclose(
        native_graph_result.series["spl_mouth"], handmapped_result.series["spl_mouth"],
        rtol=0.0, atol=SPL_ATOL_DB,
    )
    np.testing.assert_allclose(
        native_graph_result.series["spl_total_diagnostic"], handmapped_result.series["spl_total"],
        rtol=0.0, atol=SPL_ATOL_DB,
    )


def test_duplicate_front_radiation_fails_compilation_as_structured_error() -> None:
    graph = _accepted_poc3_graph_ir()
    graph["elements"].append(
        {
            "id": "unwanted_second_front_radiator",
            "type": "radiation_load",
            "node": "front",
            "area_m2": 0.0022,
            "radiation_space": "2pi",
            "model": "infinite_baffle_piston",
        }
    )
    validation = validate_acoustic_graph_ir(graph)
    assert validation.is_valid is True, validation.errors

    compiled = compile_acoustic_graph_ir_to_model_dict(graph)
    assert compiled.is_success is False
    assert compiled.model_dict is None
    assert any("exactly one explicit front radiator" in error for error in compiled.errors)


def test_poc3_graph_defined_and_handmapped_models_both_run_through_solver() -> None:
    frequency_hz = _load_reference_frequency_grid()
    handmapped_model = _handmapped_model_dict()
    graph_model = _copy_authority_observations_if_needed(_compiled_graph_model_dict(), handmapped_model)

    graph_result = _solver_result_projection(graph_model, frequency_hz)
    handmapped_result = _solver_result_projection(handmapped_model, frequency_hz)

    np.testing.assert_allclose(graph_result["frequency_hz"], frequency_hz, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(handmapped_result["frequency_hz"], frequency_hz, rtol=0.0, atol=0.0)
    assert graph_result["zin_complex_ohm"].shape == frequency_hz.shape
    assert handmapped_result["zin_complex_ohm"].shape == frequency_hz.shape
    assert np.all(np.isfinite(graph_result["zin_complex_ohm"]))
    assert np.all(np.isfinite(handmapped_result["zin_complex_ohm"]))
    assert frequency_hz.size == 533
    complex_fields = [
        "zin_complex_ohm", *(f"p_node_{node}" for node in POC3_NODES),
        "p_radiated_front_rad", "p_radiated_mouth_rad", "p_radiated_total",
    ]
    for field in complex_fields:
        np.testing.assert_allclose(graph_result[field], handmapped_result[field], rtol=COMPLEX_RTOL, atol=COMPLEX_ATOL)
    for field in ("spl_front", "spl_mouth", "spl_total"):
        np.testing.assert_allclose(graph_result[field], handmapped_result[field], rtol=0.0, atol=SPL_ATOL_DB)


def test_poc3_diagnostic_report_records_full_grid_roundoff_and_thresholds() -> None:
    report = _equivalence_diagnostic_report()
    assert report["solver_execution_status"] == "passed"
    assert report["solver_equivalence_status"] == SOLVER_EQUIVALENCE_STATUS
    assert report["frequency_count"] == 533
    assert report["thresholds_used_for_equivalence"]["complex_relative"] == COMPLEX_RTOL
    assert report["thresholds_used_for_equivalence"]["spl_absolute_db"] == SPL_ATOL_DB
    assert report["later_equivalence_alignment_required"] is False
    assert report["numerical_differences_visible"] is True
    assert "zin_complex_ohm" in report["differences"]
    assert report["differences"]["zin_complex_ohm"]["max_abs"] < COMPLEX_ATOL
    assert report["differences"]["zin_complex_ohm"]["mean_abs"] >= 0.0
    for field in report["common_spl_fields"]:
        assert field in report["differences"]
        assert report["differences"][field]["max_abs"] >= 0.0
        assert report["differences"][field]["mean_abs"] >= 0.0
        assert report["differences"][field]["max_abs"] < SPL_ATOL_DB


def test_poc3_diagnostic_report_does_not_invent_volume_chambers() -> None:
    report = _equivalence_diagnostic_report()
    assert "graph_acoustic_chamber_count" in report
    assert "graph_acoustic_chamber_records" in report
    assert report["graph_acoustic_chamber_count"] == 0
    assert report["graph_acoustic_chamber_records"] == []
    assert report["graph_chamber_records_exposed"] is True
    assert report["chamber_bearing_proof_status"] == CHAMBER_BEARING_PROOF_STATUS


def test_scope_non_claims_remain_internal_equivalence_only() -> None:
    report = _equivalence_diagnostic_report()
    assert report["strict_bit_equivalence_claim"] is False
    assert report["solver_equivalence_claim"] is True
    assert report["hornresp_parity_claim"] is False
    assert report["akabak_parity_claim"] is False
    assert report["external_parity_claim"] is False
    assert report["handmapped_replacement_claim"] is False
    assert report["optimizer_or_studio_consumption_claim"] is False
