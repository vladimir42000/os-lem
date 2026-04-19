from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.reference_hyperbolic_flare_akabak import (
    FREQUENCY_GRID_HZ,
    HYPERBOLIC_FLARE_AKABAK_REFERENCE_KIND,
    HYPERBOLIC_FLARE_AKABAK_TOPOLOGY,
    REFERENCE_SEGMENTS,
    build_hyperbolic_flare_model_dict,
    build_hyperbolic_flare_segmented_conical_reference_model_dict,
    compare_hyperbolic_flare_against_akabak_oriented_reference,
    load_hyperbolic_flare_akabak_reference_bundle,
    write_hyperbolic_flare_akabak_compare_outputs,
)


REFERENCE_DIR = Path("tests/reference_data/akabak_hyperbolic_flare")


def test_hyperbolic_flare_akabak_reference_bundle_uses_one_shared_frequency_grid() -> None:
    bundle = load_hyperbolic_flare_akabak_reference_bundle(REFERENCE_DIR)

    assert bundle.impedance_magnitude_ohm.frequency_hz.shape == (120,)
    np.testing.assert_allclose(bundle.impedance_magnitude_ohm.frequency_hz, FREQUENCY_GRID_HZ)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_db.frequency_hz)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_pa.frequency_hz)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_phase_deg.frequency_hz)
    assert "Akabak-oriented hyperbolic flare smoke" in bundle.script_text
    assert "12 conical segments" in bundle.script_text


def test_hyperbolic_flare_akabak_oriented_smoke_compare_produces_bounded_current_metrics() -> None:
    comparison = compare_hyperbolic_flare_against_akabak_oriented_reference(REFERENCE_DIR)

    assert comparison.topology == HYPERBOLIC_FLARE_AKABAK_TOPOLOGY
    assert comparison.metrics["frequency_grid_shared"] is True
    assert comparison.metrics["reference_kind"] == HYPERBOLIC_FLARE_AKABAK_REFERENCE_KIND
    assert comparison.metrics["reference_segments"] == REFERENCE_SEGMENTS
    assert comparison.metrics["reference_impedance_phase_available"] is False
    assert comparison.metrics["frequency_point_count"] == 120
    assert comparison.metrics["zmag_high_band_corr"] > 0.999
    assert comparison.metrics["zmag_overall_mae_ohm"] < 1.0
    assert comparison.metrics["zmag_max_abs_delta_ohm"] < 14.0
    assert comparison.metrics["pressure_db_low_band_corr"] > 0.998
    assert comparison.metrics["pressure_db_overall_mae"] < 3.0
    assert comparison.metrics["pressure_db_max_abs_delta"] < 17.0
    assert comparison.metrics["pressure_phase_overall_mae_deg"] < 9.0
    assert comparison.metrics["pressure_phase_max_abs_delta_deg"] < 145.0
    assert comparison.oslem_pressure_db.shape == comparison.frequency_hz.shape
    assert comparison.oslem_impedance_magnitude_ohm.shape == comparison.frequency_hz.shape
    assert np.all(np.isfinite(comparison.oslem_pressure_db))
    assert np.all(np.isfinite(comparison.oslem_impedance_magnitude_ohm))


def test_hyperbolic_flare_akabak_compare_writer_emits_csv_and_summary_json(tmp_path: Path) -> None:
    outdir = tmp_path / "hyperbolic_flare_akabak_compare"
    write_hyperbolic_flare_akabak_compare_outputs(REFERENCE_DIR, outdir)

    csv_path = outdir / "hyperbolic_flare_akabak_compare.csv"
    summary_path = outdir / "summary.json"
    assert csv_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["case"] == "Hyperbolic flare Akabak-oriented smoke"
    assert summary["topology"] == HYPERBOLIC_FLARE_AKABAK_TOPOLOGY
    assert summary["metrics"]["reference_kind"] == HYPERBOLIC_FLARE_AKABAK_REFERENCE_KIND
    assert "hyperbolic_flare_akabak_compare.csv" in summary["generated_files"]


def test_hyperbolic_flare_model_dicts_match_the_bounded_current_case_and_reference_surrogate() -> None:
    model_dict = build_hyperbolic_flare_model_dict()
    reference_model_dict = build_hyperbolic_flare_segmented_conical_reference_model_dict()

    element_ids = [element["id"] for element in model_dict["elements"]]
    reference_ids = [element["id"] for element in reference_model_dict["elements"]]

    assert element_ids == ["front_rad", "rear_vol", "wg1", "mouth_rad"]
    assert reference_ids[:2] == ["front_rad", "rear_vol"]
    assert reference_ids[-1] == "mouth_rad"
    assert reference_ids[2:-1] == [f"hyp_seg_{idx:02d}" for idx in range(1, REFERENCE_SEGMENTS + 1)]

    waveguide = next(element for element in model_dict["elements"] if element["id"] == "wg1")
    assert waveguide["profile"] == "hyperbolic"
    assert waveguide["segments"] == 12

    first_segment = next(element for element in reference_model_dict["elements"] if element["id"] == "hyp_seg_01")
    last_segment = next(element for element in reference_model_dict["elements"] if element["id"] == f"hyp_seg_{REFERENCE_SEGMENTS:02d}")
    assert first_segment["node_a"] == "rear"
    assert last_segment["node_b"] == "mouth"
    assert all(element["profile"] == "conical" for element in reference_model_dict["elements"][2:-1])
