"""GDN13 graph-defined vs hand-mapped solver-output equivalence smoke.

This test exercises only internal os-lem equivalence:

graph IR -> validator -> compiler -> existing model_dict -> solver

against the accepted hand-mapped GDN13 offset-driver TQWT model construction.
It does not compare to HornResp, does not claim external parity, and does not
replace the accepted hand-mapped path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from os_lem.acoustic_graph_ir import (
    compile_acoustic_graph_ir_to_model_dict,
    validate_acoustic_graph_ir,
)
from os_lem.api import run_simulation
from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    build_gdn13_offset_tqwt_model_dict,
    load_hornresp_gdn13_response_table,
)


OBSERVABLES_REQUIRED_FOR_EQUIVALENCE = (
    "spl_total_diagnostic",
    "spl_mouth",
)


def _accepted_gdn13_solver_graph_ir() -> dict[str, Any]:
    """Return the accepted GDN13 graph IR, configured for solver-equivalence smoke.

    The graph values are the accepted GDN13 offset-driver TQWT interpretation.
    The compiler metadata requests an existing solver model_dict target and
    default diagnostic observations.  That opt-in keeps the earlier compiler
    skeleton behavior intact while making this bounded internal solver smoke
    explicit.
    """

    return {
        "metadata": {
            "name": "gdn13_offset_tqwt_graph_defined_solver_equivalence_smoke",
            "case_id": "gdn13_offset_tqwt",
            "compiler_target": "existing_solver_model_dict",
            "emit_default_diagnostic_observations": True,
            "solver_equivalence_smoke_only": True,
            "non_claim": "internal graph-vs-handmapped equivalence only; not HornResp parity",
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
                "segments": 8,
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
                "segments": 16,
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


def _bounded_gdn13_frequency_subset() -> np.ndarray:
    """Use a deterministic bounded subset of the accepted HornResp grid.

    This is not a HornResp comparison.  The grid is used only as a stable
    representative set for internal graph-vs-handmapped solver equivalence.
    """

    table_path = (
        Path(__file__).resolve().parents[1]
        / "reference_data"
        / "hornresp_gdn13_offset_tqwt"
        / "gdn13tl.txt"
    )
    frequency_hz = load_hornresp_gdn13_response_table(table_path)["frequency_hz"]
    targets = np.asarray(
        [20.0, 25.0, 31.5, 32.773887, 40.0, 60.0, 100.0, 250.0, 600.0, 1000.0],
        dtype=float,
    )
    indices = sorted({int(np.argmin(np.abs(frequency_hz - target))) for target in targets})
    subset = np.asarray(frequency_hz[indices], dtype=float)
    assert subset.ndim == 1
    assert subset.size >= 8
    return subset


def _compiled_graph_model_dict() -> dict[str, Any]:
    graph = _accepted_gdn13_solver_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    assert validation.is_valid is True, validation.errors

    compiled = compile_acoustic_graph_ir_to_model_dict(graph)
    assert compiled.is_success is True, compiled.errors
    assert compiled.model_dict is not None
    return compiled.model_dict


def _handmapped_model_dict() -> dict[str, Any]:
    return build_gdn13_offset_tqwt_model_dict(profile="parabolic")


def _solver_result_projection(model_dict: dict[str, Any], frequency_hz: np.ndarray) -> dict[str, np.ndarray]:
    result = run_simulation(model_dict, frequency_hz)

    assert result.zin_complex_ohm is not None
    projected: dict[str, np.ndarray] = {
        "frequency_hz": np.asarray(result.frequencies_hz, dtype=float),
        "zin_complex_ohm": np.asarray(result.zin_complex_ohm, dtype=complex),
    }
    for observable_id in OBSERVABLES_REQUIRED_FOR_EQUIVALENCE:
        assert observable_id in result.series
        projected[observable_id] = np.asarray(result.series[observable_id], dtype=float)

    if "spl_driver_front_diagnostic" in result.series:
        projected["spl_driver_front_diagnostic"] = np.asarray(
            result.series["spl_driver_front_diagnostic"],
            dtype=float,
        )
    return projected


def _difference_summary(actual: np.ndarray, expected: np.ndarray) -> dict[str, float]:
    delta = np.asarray(actual) - np.asarray(expected)
    if np.iscomplexobj(delta):
        abs_delta = np.abs(delta)
    else:
        abs_delta = np.abs(delta.astype(float))
    return {
        "max_abs": float(np.max(abs_delta)),
        "mean_abs": float(np.mean(abs_delta)),
    }


def test_gdn13_graph_validates_compiles_and_produces_solver_model_dict() -> None:
    graph = _accepted_gdn13_solver_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    compiled = compile_acoustic_graph_ir_to_model_dict(graph)

    assert validation.is_valid is True
    assert compiled.is_success is True
    assert compiled.model_dict is not None
    assert compiled.model_dict["meta"]["compiler_target"] == "existing_solver_model_dict"
    assert compiled.model_dict["driver"]["model"] == "ts_classic"

    element_ids = [element["id"] for element in compiled.model_dict["elements"]]
    assert "driver_front_radiation_diagnostic" in element_ids
    assert "rear_closed_stub_s1_to_s2" in element_ids
    assert "forward_open_line_s2_to_s3" in element_ids
    assert "mouth_s3_radiation" in element_ids

    observation_ids = [observation["id"] for observation in compiled.model_dict["observations"]]
    assert observation_ids == ["zin", "spl_mouth", "spl_total_diagnostic"]


def test_gdn13_graph_defined_and_handmapped_solver_outputs_match_tightly() -> None:
    frequency_hz = _bounded_gdn13_frequency_subset()
    graph_result = _solver_result_projection(_compiled_graph_model_dict(), frequency_hz)
    handmapped_result = _solver_result_projection(_handmapped_model_dict(), frequency_hz)

    np.testing.assert_allclose(graph_result["frequency_hz"], handmapped_result["frequency_hz"], rtol=0.0, atol=0.0)
    np.testing.assert_allclose(
        graph_result["zin_complex_ohm"],
        handmapped_result["zin_complex_ohm"],
        rtol=1.0e-10,
        atol=1.0e-10,
    )
    for observable_id in OBSERVABLES_REQUIRED_FOR_EQUIVALENCE:
        np.testing.assert_allclose(
            graph_result[observable_id],
            handmapped_result[observable_id],
            rtol=1.0e-10,
            atol=1.0e-10,
        )

    if "spl_driver_front_diagnostic" in graph_result and "spl_driver_front_diagnostic" in handmapped_result:
        np.testing.assert_allclose(
            graph_result["spl_driver_front_diagnostic"],
            handmapped_result["spl_driver_front_diagnostic"],
            rtol=1.0e-10,
            atol=1.0e-10,
        )


def test_gdn13_graph_solver_equivalence_reports_zero_internal_differences() -> None:
    frequency_hz = _bounded_gdn13_frequency_subset()
    graph_result = _solver_result_projection(_compiled_graph_model_dict(), frequency_hz)
    handmapped_result = _solver_result_projection(_handmapped_model_dict(), frequency_hz)

    summaries = {
        "zin_complex_ohm": _difference_summary(graph_result["zin_complex_ohm"], handmapped_result["zin_complex_ohm"]),
        "spl_total_diagnostic": _difference_summary(
            graph_result["spl_total_diagnostic"],
            handmapped_result["spl_total_diagnostic"],
        ),
        "spl_mouth": _difference_summary(graph_result["spl_mouth"], handmapped_result["spl_mouth"]),
    }

    for summary in summaries.values():
        assert summary["max_abs"] <= 1.0e-9
        assert summary["mean_abs"] <= 1.0e-9


def test_scope_non_claims_remain_internal_graph_vs_handmapped_only() -> None:
    graph_model = _compiled_graph_model_dict()
    non_claims = graph_model["meta"]["non_claims"]

    assert "no external HornResp parity claim" in non_claims
    assert "no Akabak/HornResp replacement claim" in non_claims
    assert "does not replace accepted hand-mapped path" in non_claims
    assert _handmapped_model_dict()["meta"]["name"] == "gdn13_offset_tqwt_hornresp_mapping_trial"
