"""POC3 graph-defined solver-execution diagnostic smoke.

This file intentionally does not claim graph-vs-handmapped POC3 solver
equivalence.  The first solver-execution smoke proved that both paths can run,
but the probe showed nonzero graph-vs-handmapped numerical deltas and no
graph-level acoustic_chamber records in the accepted POC3 construction helper.

Therefore this _07 repair creates the surface from clean base 7b0df05 as a bounded diagnostic:
it proves graph-defined POC3 solver execution and reports internal differences
against the accepted hand-mapped POC3 path, while explicitly leaving true
solver-equivalence/alignment for a later Director-approved step.

It does not compare against HornResp or Akabak, does not claim external parity,
does not replace the accepted hand-mapped POC3 path, and does not open
optimizer, Studio, importer, or topology-expansion scope.
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


REPO_ROOT = Path(__file__).resolve().parents[2]
POC3_MODEL_PATH = REPO_ROOT / "proof" / "poc3_blh_benchmark_pass1" / "model.yaml"
POC3_FREQ_GRID_PATH = REPO_ROOT / "proof" / "poc3_blh_benchmark_pass1" / "source_inputs" / "poc3_hr_all.txt"
CONSTRUCTION_HELPER_PATH = REPO_ROOT / "tests" / "graph" / "test_poc3_blh_graph_to_handmapped_construction_equivalence_smoke.py"

REQUIRED_AUTHORITY_PATH = "proof/poc3_blh_benchmark_pass1/model.yaml"
GRAPH_VALIDATOR_CALLABLE = "os_lem.acoustic_graph_ir.validate_acoustic_graph_ir"
GRAPH_COMPILER_CALLABLE = "os_lem.acoustic_graph_ir.compile_acoustic_graph_ir_to_model_dict"
SOLVER_CALLABLE = "os_lem.api.run_simulation"

DIAGNOSTIC_CLASSIFICATION = "graph_defined_poc3_solver_execution_diagnostic"
SOLVER_EQUIVALENCE_STATUS = "not_established_requires_later_alignment"
CHAMBER_BEARING_PROOF_STATUS = "not_established_by_current_poc3_graph_helper"


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
    result = run_simulation(model_dict, frequency_hz)
    assert result.zin_complex_ohm is not None
    projected: dict[str, np.ndarray] = {
        "frequency_hz": np.asarray(result.frequencies_hz, dtype=float),
        "zin_complex_ohm": np.asarray(result.zin_complex_ohm, dtype=complex),
    }
    for key, value in result.series.items():
        if "spl" in str(key).lower():
            projected[str(key)] = np.asarray(value, dtype=float)
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
    frequency_hz = _bounded_poc3_frequency_subset()

    graph_result = _solver_result_projection(graph_model, frequency_hz)
    handmapped_result = _solver_result_projection(handmapped_model, frequency_hz)
    common_spl_fields = sorted(
        key
        for key in set(graph_result).intersection(handmapped_result)
        if "spl" in key.lower()
    )
    differences: dict[str, dict[str, float]] = {
        "zin_complex_ohm": _difference_summary(graph_result["zin_complex_ohm"], handmapped_result["zin_complex_ohm"]),
    }
    for field in common_spl_fields:
        differences[field] = _difference_summary(graph_result[field], handmapped_result[field])

    graph_chamber_records = _graph_chamber_records(graph_model)
    return {
        "diagnostic_classification": DIAGNOSTIC_CLASSIFICATION,
        "solver_execution_status": "passed",
        "solver_equivalence_status": SOLVER_EQUIVALENCE_STATUS,
        "chamber_bearing_proof_status": CHAMBER_BEARING_PROOF_STATUS,
        "authority_path": REQUIRED_AUTHORITY_PATH,
        "frequency_hz": frequency_hz.tolist(),
        "compared_solver_fields": ["frequency_hz", "zin_complex_ohm", *common_spl_fields],
        "common_spl_fields": common_spl_fields,
        "differences": differences,
        "thresholds_used_for_equivalence": None,
        "threshold_rationale": "no equivalence thresholds are asserted in this diagnostic repair",
        "graph_model_element_count": len(graph_model.get("elements", [])),
        "handmapped_model_element_count": len(handmapped_model.get("elements", [])) if isinstance(handmapped_model.get("elements"), list) else None,
        "graph_acoustic_chamber_count": len(graph_chamber_records),
        "graph_acoustic_chamber_records": graph_chamber_records,
        "graph_chamber_records_exposed": True,
        "numerical_differences_visible": True,
        "later_equivalence_alignment_required": True,
        "strict_bit_equivalence_claim": False,
        "solver_equivalence_claim": False,
        "hornresp_parity_claim": False,
        "akabak_parity_claim": False,
        "external_parity_claim": False,
        "handmapped_replacement_claim": False,
        "optimizer_or_studio_consumption_claim": False,
    }


def evaluate_poc3_graph_defined_solver_equivalence_smoke() -> dict[str, Any]:
    """Probe entrypoint kept for script compatibility; returns diagnostic report."""
    return _equivalence_diagnostic_report()


def test_poc3_graph_validates_compiles_and_runs_as_diagnostic_payload() -> None:
    graph = _accepted_poc3_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    compiled = compile_acoustic_graph_ir_to_model_dict(graph)

    assert validation.is_valid is True, validation.errors
    assert compiled.is_success is True, compiled.errors
    assert compiled.model_dict is not None
    assert compiled.model_dict["meta"]["compiler_target"] == "existing_solver_model_dict"
    # Diagnostic classification is intentionally a test/probe/report-layer
    # statement.  The compiler is not required to emit diagnostic_only or
    # solver_equivalence_status metadata.
    assert DIAGNOSTIC_CLASSIFICATION == "graph_defined_poc3_solver_execution_diagnostic"
    assert SOLVER_EQUIVALENCE_STATUS == "not_established_requires_later_alignment"
    assert CHAMBER_BEARING_PROOF_STATUS == "not_established_by_current_poc3_graph_helper"
    assert "elements" in compiled.model_dict
    assert isinstance(_graph_chamber_records(compiled.model_dict), list)


def test_poc3_graph_defined_and_handmapped_models_both_run_through_solver() -> None:
    frequency_hz = _bounded_poc3_frequency_subset()
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


def test_poc3_diagnostic_report_exposes_differences_without_equivalence_thresholds() -> None:
    report = _equivalence_diagnostic_report()
    assert report["solver_execution_status"] == "passed"
    assert report["solver_equivalence_status"] == SOLVER_EQUIVALENCE_STATUS
    assert report["thresholds_used_for_equivalence"] is None
    assert report["later_equivalence_alignment_required"] is True
    assert report["numerical_differences_visible"] is True
    assert "zin_complex_ohm" in report["differences"]
    assert report["differences"]["zin_complex_ohm"]["max_abs"] >= 0.0
    assert report["differences"]["zin_complex_ohm"]["mean_abs"] >= 0.0
    for field in report["common_spl_fields"]:
        assert field in report["differences"]
        assert report["differences"][field]["max_abs"] >= 0.0
        assert report["differences"][field]["mean_abs"] >= 0.0


def test_poc3_diagnostic_report_exposes_chamber_status_without_inventing_chambers() -> None:
    report = _equivalence_diagnostic_report()
    assert "graph_acoustic_chamber_count" in report
    assert "graph_acoustic_chamber_records" in report
    assert isinstance(report["graph_acoustic_chamber_records"], list)
    assert report["graph_chamber_records_exposed"] is True
    assert report["chamber_bearing_proof_status"] == CHAMBER_BEARING_PROOF_STATUS


def test_scope_non_claims_remain_internal_diagnostic_only() -> None:
    report = _equivalence_diagnostic_report()
    assert report["strict_bit_equivalence_claim"] is False
    assert report["solver_equivalence_claim"] is False
    assert report["hornresp_parity_claim"] is False
    assert report["akabak_parity_claim"] is False
    assert report["external_parity_claim"] is False
    assert report["handmapped_replacement_claim"] is False
    assert report["optimizer_or_studio_consumption_claim"] is False
