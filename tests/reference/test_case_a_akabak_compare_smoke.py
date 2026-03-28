from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.reference_case_a import (
    CASE_A_TOPOLOGY,
    build_case_a_model_dict,
    compare_case_a_against_akabak,
    load_case_a_reference_bundle,
    write_case_a_compare_outputs,
)


REFERENCE_DIR = Path("tests/reference_data/akabak_case_a")


def test_case_a_reference_bundle_uses_one_shared_frequency_grid() -> None:
    bundle = load_case_a_reference_bundle(REFERENCE_DIR)

    assert bundle.impedance_magnitude_ohm.frequency_hz.shape == (120,)
    np.testing.assert_array_equal(
        bundle.impedance_magnitude_ohm.frequency_hz,
        bundle.pressure_db.frequency_hz,
    )
    np.testing.assert_array_equal(
        bundle.impedance_magnitude_ohm.frequency_hz,
        bundle.pressure_pa.frequency_hz,
    )
    np.testing.assert_array_equal(
        bundle.impedance_magnitude_ohm.frequency_hz,
        bundle.pressure_phase_deg.frequency_hz,
    )
    assert "Topology: Split-Path Recombination" in bundle.script_text


def test_case_a_smoke_compare_produces_bounded_current_metrics() -> None:
    comparison = compare_case_a_against_akabak(REFERENCE_DIR)

    assert comparison.topology == CASE_A_TOPOLOGY
    assert comparison.metrics["frequency_grid_shared"] is True
    assert comparison.metrics["reference_impedance_phase_available"] is False
    assert comparison.metrics["frequency_point_count"] == 120
    assert comparison.metrics["zmag_high_band_corr"] > 0.99
    assert comparison.metrics["pressure_db_low_band_corr"] > 0.98
    assert comparison.metrics["pressure_phase_low_band_corr"] > 0.95
    assert comparison.metrics["pressure_db_overall_mae"] < 10.0
    assert comparison.metrics["zmag_overall_mae_ohm"] < 30.0
    assert comparison.oslem_pressure_db.shape == comparison.frequency_hz.shape
    assert comparison.oslem_impedance_magnitude_ohm.shape == comparison.frequency_hz.shape
    assert np.all(np.isfinite(comparison.oslem_pressure_db))
    assert np.all(np.isfinite(comparison.oslem_impedance_magnitude_ohm))


def test_case_a_compare_writer_emits_csv_and_summary_json(tmp_path: Path) -> None:
    outdir = tmp_path / "case_a_compare"
    write_case_a_compare_outputs(REFERENCE_DIR, outdir)

    csv_path = outdir / "case_a_compare.csv"
    summary_path = outdir / "summary.json"
    assert csv_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["case"] == "Case A"
    assert summary["topology"] == CASE_A_TOPOLOGY
    assert "case_a_compare.csv" in summary["generated_files"]
    assert summary["metrics"]["reference_impedance_phase_available"] is False


def test_case_a_model_dict_matches_the_bounded_parallel_bundle_plus_shared_exit_interpretation() -> None:
    model_dict = build_case_a_model_dict()
    element_ids = {element["id"] for element in model_dict["elements"]}

    assert element_ids == {"rear_box", "path1", "path2", "exit", "mouth"}
    path1 = next(element for element in model_dict["elements"] if element["id"] == "path1")
    path2 = next(element for element in model_dict["elements"] if element["id"] == "path2")
    exit_line = next(element for element in model_dict["elements"] if element["id"] == "exit")
    mouth = next(element for element in model_dict["elements"] if element["id"] == "mouth")

    assert path1["node_a"] == path2["node_a"] == "front"
    assert path1["node_b"] == path2["node_b"] == "merge"
    assert exit_line["node_a"] == "merge"
    assert exit_line["node_b"] == mouth["node"] == "mouth"
