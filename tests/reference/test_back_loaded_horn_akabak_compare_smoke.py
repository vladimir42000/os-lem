from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import (
    BACK_LOADED_HORN_TOPOLOGY,
    NO_FRONTEND_CONTRACT_CHANGE,
    build_back_loaded_horn_model_dict,
    compare_back_loaded_horn_against_akabak,
    write_back_loaded_horn_compare_outputs,
)
from os_lem.reference_rear_chamber_tapped import load_rear_chamber_reference_bundle


REFERENCE_DIR = Path("tests/reference_data/akabak_rear_chamber_tapped")


def test_back_loaded_horn_smoke_model_assembles_one_supported_skeleton() -> None:
    model_dict = build_back_loaded_horn_model_dict()
    normalized, warnings = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True
    assert len(system.back_loaded_horn_skeletons) == 1
    assert len(system.dual_radiator_topologies) == 1
    assert len(system.direct_front_radiation_topologies) == 1

    skeleton = system.back_loaded_horn_skeletons[0]
    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.rear_chamber_element_id == "rear_chamber"
    assert skeleton.rear_path_element_id == "rear_leg"
    assert skeleton.mouth_radiator_id == "mouth_rad"


def test_back_loaded_horn_smoke_run_simulation_preserves_sidebranch_and_mouth_outputs() -> None:
    model_dict = build_back_loaded_horn_model_dict()
    frequencies = np.array([80.0, 160.0, 320.0])

    result = run_simulation(model_dict, frequencies)

    assert result.units["p_mouth"] == "Pa"
    assert result.units["mouth_q"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["front_q"]))
    assert np.all(np.isfinite(result.series["rear_leg_q_a"]))
    assert np.all(np.isfinite(result.series["rear_leg_q_b"]))
    assert np.all(np.abs(result.series["blind_down_q_b"]) < 1.0e-10)
    np.testing.assert_allclose(
        result.series["blind_down_q_a"],
        result.series["blind_up_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(result.series["p_front"], result.series["p_mouth"])


def test_back_loaded_horn_smoke_compare_produces_bounded_family_metrics() -> None:
    comparison = compare_back_loaded_horn_against_akabak(REFERENCE_DIR)

    assert comparison.topology == BACK_LOADED_HORN_TOPOLOGY
    assert comparison.metrics["frequency_grid_shared"] is True
    assert comparison.metrics["reference_impedance_phase_available"] is False
    assert comparison.metrics["no_frontend_contract_change"] is True
    assert comparison.metrics["frequency_point_count"] == 120.0
    assert comparison.metrics["pressure_db_low_band_point_count"] == 80.0
    assert comparison.metrics["pressure_db_low_band_max_hz"] == 2000.0
    assert comparison.metrics["zmag_shape_corr"] > 0.10
    assert comparison.metrics["zmag_shape_normalized_mae"] < 0.20
    assert comparison.metrics["zmag_centered_mae_ohm"] < 35.0
    assert comparison.metrics["pressure_db_shape_corr"] > 0.70
    assert comparison.metrics["pressure_db_shape_normalized_mae"] < 0.40
    assert comparison.metrics["pressure_db_centered_mae"] < 30.0
    assert comparison.metrics["pressure_db_low_band_centered_mae"] < 20.0
    assert comparison.metrics["pressure_pa_shape_normalized_mae"] < 0.50
    assert comparison.metrics["pressure_phase_overall_mae_deg"] < 120.0
    assert comparison.metrics["blind_closed_end_max_abs_m3_s"] < 1.0e-10
    assert comparison.metrics["throat_side_sidebranch_balance_mae_m3_s"] < 1.0e-10
    assert np.all(np.isfinite(comparison.oslem_pressure_db))
    assert np.all(np.isfinite(comparison.oslem_impedance_magnitude_ohm))
    assert np.all(np.isfinite(comparison.observables["front_q_mag_m3_s"]))


def test_back_loaded_horn_compare_writer_emits_csv_summary_and_observables(tmp_path: Path) -> None:
    outdir = tmp_path / "back_loaded_horn_compare"
    write_back_loaded_horn_compare_outputs(REFERENCE_DIR, outdir)

    csv_path = outdir / "back_loaded_horn_compare.csv"
    observables_path = outdir / "back_loaded_horn_observables.csv"
    summary_path = outdir / "summary.json"
    assert csv_path.exists()
    assert observables_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["case"] == "TH-family back-loaded horn smoke"
    assert summary["topology"] == BACK_LOADED_HORN_TOPOLOGY
    assert summary["no_frontend_contract_change"] is True
    assert "back_loaded_horn_compare.csv" in summary["generated_files"]
    assert "back_loaded_horn_observables.csv" in summary["generated_files"]


def test_back_loaded_horn_smoke_reference_bundle_still_uses_one_shared_frequency_grid() -> None:
    bundle = load_rear_chamber_reference_bundle(REFERENCE_DIR)

    assert bundle.impedance_magnitude_ohm.frequency_hz.shape == (120,)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_db.frequency_hz)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_pa.frequency_hz)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_phase_deg.frequency_hz)
