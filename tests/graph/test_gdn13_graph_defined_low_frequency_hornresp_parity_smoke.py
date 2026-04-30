"""Graph-defined GDN13 low-frequency HornResp parity smoke.

This test preserves only the already accepted low-frequency parity semantics for
one GDN13 offset-driver TQWT case through the graph-defined construction path:

graph IR -> validator -> compiler -> existing model_dict -> existing solver

It compares graph-defined os-lem outputs against the accepted HornResp fixture
only in the low-frequency band.  It does not claim full-band SPL parity, general
HornResp parity, Akabak/HornResp replacement, optimizer integration, or
replacement of the accepted hand-mapped GDN13 path.
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
from os_lem.gdn13_offset_tqwt_opt_parity_gate import (
    SPL_MAE_THRESHOLD_DB,
    SPL_RMS_THRESHOLD_DB,
    ZE_MAE_THRESHOLD_OHM,
    ZE_RMS_THRESHOLD_OHM,
)
from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    LOW_FREQUENCY_LIMIT_HZ,
    PRIMARY_SPL_OBSERVABLE_ID,
    SECONDARY_MOUTH_SPL_OBSERVABLE_ID,
    load_hornresp_gdn13_response_table,
)


CASE_ID = "gdn13_offset_tqwt"
HORNRESP_FIXTURE_RELATIVE_PATH = "tests/reference_data/hornresp_gdn13_offset_tqwt/gdn13tl.txt"
FULL_BAND_SPL_CLAIM = False
MOUTH_ONLY_SPL_CLAIM = False


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _hornresp_response_path() -> Path:
    return _repo_root() / "tests" / "reference_data" / "hornresp_gdn13_offset_tqwt" / "gdn13tl.txt"


def _accepted_gdn13_graph_ir() -> dict[str, Any]:
    """Return the accepted GDN13 graph IR for the graph-defined parity smoke.

    The GDN13 values are the accepted offset-driver TQWT interpretation.  The
    graph metadata opts into the existing solver model_dict target already added
    by the graph compiler skeleton; the test still makes only a bounded
    low-frequency HornResp comparison.
    """

    return {
        "metadata": {
            "name": "gdn13_offset_tqwt_graph_defined_low_frequency_hornresp_parity_smoke",
            "case_id": CASE_ID,
            "compiler_target": "existing_solver_model_dict",
            "emit_default_diagnostic_observations": True,
            "hornresp_parity_scope": "low_frequency_only_frequency_hz_le_600",
            "full_band_spl_claim": FULL_BAND_SPL_CLAIM,
            "mouth_only_spl_claim": MOUTH_ONLY_SPL_CLAIM,
            "non_claim": "graph-defined low-frequency GDN13 parity only; not full-band or general HornResp parity",
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


def _metric_summary(delta: np.ndarray) -> dict[str, float]:
    delta = np.asarray(delta, dtype=float)
    return {
        "mae": float(np.mean(np.abs(delta))),
        "rms": float(np.sqrt(np.mean(delta * delta))),
        "max_abs": float(np.max(np.abs(delta))),
    }


def _compiled_graph_model_dict() -> dict[str, Any]:
    graph = _accepted_gdn13_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    assert validation.is_valid is True, validation.errors

    compiled = compile_acoustic_graph_ir_to_model_dict(graph)
    assert compiled.is_success is True, compiled.errors
    assert compiled.model_dict is not None
    return compiled.model_dict


def evaluate_gdn13_graph_defined_low_frequency_hornresp_parity_smoke() -> dict[str, Any]:
    """Return the bounded graph-defined low-frequency HornResp parity report."""

    graph = _accepted_gdn13_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    compiled = compile_acoustic_graph_ir_to_model_dict(graph)
    assert validation.is_valid is True, validation.errors
    assert compiled.is_success is True, compiled.errors
    assert compiled.model_dict is not None

    hornresp_path = _hornresp_response_path()
    hornresp = load_hornresp_gdn13_response_table(hornresp_path)
    frequency_hz = np.asarray(hornresp["frequency_hz"], dtype=float)
    hornresp_spl_db = np.asarray(hornresp["spl_db"], dtype=float)
    hornresp_ze_ohm = np.asarray(hornresp["ze_ohm"], dtype=float)

    result = run_simulation(compiled.model_dict, frequency_hz)
    assert result.zin_complex_ohm is not None
    assert PRIMARY_SPL_OBSERVABLE_ID in result.series
    assert SECONDARY_MOUTH_SPL_OBSERVABLE_ID in result.series

    result_frequency_hz = np.asarray(result.frequencies_hz, dtype=float)
    np.testing.assert_allclose(result_frequency_hz, frequency_hz, rtol=0.0, atol=0.0)

    graph_spl_total_db = np.asarray(result.series[PRIMARY_SPL_OBSERVABLE_ID], dtype=float)
    graph_spl_mouth_db = np.asarray(result.series[SECONDARY_MOUTH_SPL_OBSERVABLE_ID], dtype=float)
    graph_ze_ohm = np.abs(np.asarray(result.zin_complex_ohm, dtype=complex))

    assert graph_spl_total_db.shape == frequency_hz.shape
    assert graph_spl_mouth_db.shape == frequency_hz.shape
    assert graph_ze_ohm.shape == frequency_hz.shape
    assert np.all(np.isfinite(graph_spl_total_db))
    assert np.all(np.isfinite(graph_spl_mouth_db))
    assert np.all(np.isfinite(graph_ze_ohm))

    low_mask = frequency_hz <= LOW_FREQUENCY_LIMIT_HZ
    assert int(np.count_nonzero(low_mask)) >= 10

    spl_delta = graph_spl_total_db - hornresp_spl_db
    mouth_delta = graph_spl_mouth_db - hornresp_spl_db
    ze_delta = graph_ze_ohm - hornresp_ze_ohm

    spl_low = _metric_summary(spl_delta[low_mask])
    spl_full = _metric_summary(spl_delta)
    ze_low = _metric_summary(ze_delta[low_mask])
    ze_full = _metric_summary(ze_delta)
    mouth_low = _metric_summary(mouth_delta[low_mask])
    mouth_full = _metric_summary(mouth_delta)

    spl_parity_passed = bool(
        spl_low["mae"] <= SPL_MAE_THRESHOLD_DB
        and spl_low["rms"] <= SPL_RMS_THRESHOLD_DB
    )
    impedance_parity_passed = bool(
        ze_low["mae"] <= ZE_MAE_THRESHOLD_OHM
        and ze_low["rms"] <= ZE_RMS_THRESHOLD_OHM
    )

    return {
        "case_id": CASE_ID,
        "task": "test/v0.9.0-gdn13-graph-defined-low-frequency-hornresp-parity-smoke",
        "graph_validator_callable": "os_lem.acoustic_graph_ir.validate_acoustic_graph_ir",
        "graph_compiler_callable": "os_lem.acoustic_graph_ir.compile_acoustic_graph_ir_to_model_dict",
        "solver_callable": "os_lem.api.run_simulation",
        "hornresp_fixture_path": HORNRESP_FIXTURE_RELATIVE_PATH,
        "frequency_count": int(frequency_hz.size),
        "frequency_band_used_for_parity": {
            "scope": "low_frequency_only",
            "predicate": "frequency_hz <= 600.0",
            "limit_hz": float(LOW_FREQUENCY_LIMIT_HZ),
            "count": int(np.count_nonzero(low_mask)),
            "min_hz": float(frequency_hz[low_mask][0]),
            "max_hz": float(frequency_hz[low_mask][-1]),
        },
        "spl_reference": "HornResp SPL column",
        "spl_observable": PRIMARY_SPL_OBSERVABLE_ID,
        "spl_low_frequency_metrics": spl_low,
        "spl_low_frequency_thresholds": {
            "mae_db": SPL_MAE_THRESHOLD_DB,
            "rms_db": SPL_RMS_THRESHOLD_DB,
        },
        "spl_parity_passed": spl_parity_passed,
        "impedance_reference": "HornResp Ze column",
        "impedance_observable": "abs(zin_complex_ohm)",
        "impedance_low_frequency_metrics": ze_low,
        "impedance_low_frequency_thresholds": {
            "mae_ohm": ZE_MAE_THRESHOLD_OHM,
            "rms_ohm": ZE_RMS_THRESHOLD_OHM,
        },
        "impedance_parity_passed": impedance_parity_passed,
        "full_band_spl_metrics_visible_limitation": spl_full,
        "full_band_impedance_metrics_visible_context": ze_full,
        "mouth_only_rejected_observable": SECONDARY_MOUTH_SPL_OBSERVABLE_ID,
        "mouth_only_low_frequency_metrics_rejected_context": mouth_low,
        "mouth_only_full_band_metrics_rejected_context": mouth_full,
        "full_band_spl_claim": FULL_BAND_SPL_CLAIM,
        "mouth_only_spl_claim": MOUTH_ONLY_SPL_CLAIM,
        "graph_defined_low_frequency_hornresp_parity_passed": bool(spl_parity_passed and impedance_parity_passed),
        "non_claims": [
            "this does not establish full-band SPL parity",
            "this does not establish general graph-defined HornResp parity",
            "this does not establish full Akabak/HornResp replacement",
            "this does not replace the accepted hand-mapped GDN13 path",
            "this does not authorize topology optimization",
            "this does not implement Studio or optimizer integration",
            "this does not implement Akabak/HornResp import",
            "this does not change solver-core behavior",
            "this does not open arbitrary graph engine behavior",
        ],
    }


def test_gdn13_graph_defined_validates_compiles_and_runs_against_hornresp_grid() -> None:
    graph = _accepted_gdn13_graph_ir()
    validation = validate_acoustic_graph_ir(graph)
    compiled = compile_acoustic_graph_ir_to_model_dict(graph)

    assert validation.is_valid is True
    assert compiled.is_success is True
    assert compiled.model_dict is not None

    hornresp = load_hornresp_gdn13_response_table(_hornresp_response_path())
    result = run_simulation(compiled.model_dict, hornresp["frequency_hz"])

    assert np.asarray(result.frequencies_hz).shape == np.asarray(hornresp["frequency_hz"]).shape
    assert result.zin_complex_ohm is not None
    assert PRIMARY_SPL_OBSERVABLE_ID in result.series
    assert SECONDARY_MOUTH_SPL_OBSERVABLE_ID in result.series


def test_gdn13_graph_defined_low_frequency_hornresp_parity_passes_with_total_spl() -> None:
    report = evaluate_gdn13_graph_defined_low_frequency_hornresp_parity_smoke()

    assert report["frequency_band_used_for_parity"]["predicate"] == "frequency_hz <= 600.0"
    assert report["spl_observable"] == PRIMARY_SPL_OBSERVABLE_ID
    assert report["spl_parity_passed"] is True
    assert report["spl_low_frequency_metrics"]["mae"] <= SPL_MAE_THRESHOLD_DB
    assert report["spl_low_frequency_metrics"]["rms"] <= SPL_RMS_THRESHOLD_DB
    assert report["impedance_observable"] == "abs(zin_complex_ohm)"
    assert report["impedance_parity_passed"] is True
    assert report["impedance_low_frequency_metrics"]["mae"] <= ZE_MAE_THRESHOLD_OHM
    assert report["impedance_low_frequency_metrics"]["rms"] <= ZE_RMS_THRESHOLD_OHM
    assert report["graph_defined_low_frequency_hornresp_parity_passed"] is True


def test_gdn13_graph_defined_parity_keeps_mouth_only_and_full_band_as_non_claims() -> None:
    report = evaluate_gdn13_graph_defined_low_frequency_hornresp_parity_smoke()

    assert report["mouth_only_rejected_observable"] == SECONDARY_MOUTH_SPL_OBSERVABLE_ID
    assert report["mouth_only_spl_claim"] is False
    assert report["full_band_spl_claim"] is False
    assert report["full_band_spl_metrics_visible_limitation"]["max_abs"] >= report["spl_low_frequency_metrics"]["max_abs"]
    assert "this does not establish full-band SPL parity" in report["non_claims"]
    assert "this does not establish general graph-defined HornResp parity" in report["non_claims"]
    assert "this does not establish full Akabak/HornResp replacement" in report["non_claims"]
