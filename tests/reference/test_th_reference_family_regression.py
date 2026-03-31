from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_front_chamber_throat_side import (
    FRONT_CHAMBER_THROAT_SIDE_TOPOLOGY,
    NO_FRONTEND_CONTRACT_CHANGE,
    build_front_chamber_throat_side_model_dict,
    compare_front_chamber_throat_side_against_akabak,
    write_front_chamber_throat_side_compare_outputs,
)


REFERENCE_DIR = Path("tests/reference_data/akabak_rear_chamber_tapped")


def test_th_reference_family_canonical_path_assembles() -> None:
    model_dict = build_front_chamber_throat_side_model_dict()
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert NO_FRONTEND_CONTRACT_CHANGE is True
    assert len(system.front_chamber_throat_side_coupling_topologies) == 1

    topology = system.front_chamber_throat_side_coupling_topologies[0]
    assert topology.rear_node_name == "rear"
    assert topology.injection_node_name == "inject"
    assert topology.throat_node_name == "throat"
    assert topology.throat_side_node_name == "throat_side"
    assert topology.blind_node_name == "blind"
    assert topology.front_chamber_node_name == "front"
    assert topology.tap_node_name == "tap"
    assert topology.merge_node_name == "merge"
    assert topology.mouth_node_name == "mouth"


def test_th_reference_family_run_simulation_preserves_core_balances() -> None:
    model_dict = build_front_chamber_throat_side_model_dict()
    frequencies = np.array([80.0, 160.0, 320.0])

    result = run_simulation(model_dict, frequencies)

    assert result.units["p_front"] == "Pa"
    assert result.units["blind_down_q_b"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["p_front"].real))
    assert np.all(np.isfinite(result.series["p_throat_side"].imag))

    np.testing.assert_allclose(
        result.series["blind_down_q_a"],
        result.series["blind_up_q_b"] + result.series["front_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert np.all(np.abs(result.series["blind_down_q_b"]) < 1.0e-10)
    np.testing.assert_allclose(
        result.series["exit_q_a"],
        result.series["main_q_b"] + result.series["tap_down_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(result.series["p_front"], result.series["p_throat_side"])


def test_th_reference_family_smoke_metrics_remain_bounded() -> None:
    comparison = compare_front_chamber_throat_side_against_akabak(REFERENCE_DIR)

    assert comparison.topology == FRONT_CHAMBER_THROAT_SIDE_TOPOLOGY
    assert comparison.metrics["frequency_grid_shared"] is True
    assert comparison.metrics["reference_impedance_phase_available"] is False
    assert comparison.metrics["no_frontend_contract_change"] is True
    assert comparison.metrics["frequency_point_count"] == 120.0
    assert comparison.metrics["zmag_overall_corr"] > 0.20
    assert comparison.metrics["zmag_overall_mae_ohm"] < 30.0
    assert comparison.metrics["pressure_db_overall_corr"] > 0.72
    assert comparison.metrics["pressure_db_low_band_point_count"] == 80.0
    assert comparison.metrics["pressure_db_low_band_max_hz"] == 2000.0
    assert comparison.metrics["pressure_db_low_band_mae"] < 15.0
    assert comparison.metrics["pressure_db_low_band_corr"] > 0.30
    assert comparison.metrics["pressure_phase_overall_mae_deg"] < 90.0
    assert comparison.metrics["blind_closed_end_max_abs_m3_s"] < 1.0e-10
    assert comparison.metrics["throat_side_coupling_balance_mae_m3_s"] < 1.0e-10
    assert np.all(np.isfinite(comparison.oslem_pressure_db))
    assert np.all(np.isfinite(comparison.oslem_impedance_magnitude_ohm))
    assert np.all(np.isfinite(comparison.observables["front_q_b_mag_m3_s"]))


def test_th_reference_family_writer_emits_regression_artifacts(tmp_path: Path) -> None:
    outdir = tmp_path / "th_reference_family"
    write_front_chamber_throat_side_compare_outputs(REFERENCE_DIR, outdir)

    csv_path = outdir / "front_chamber_throat_side_compare.csv"
    observables_path = outdir / "front_chamber_throat_side_observables.csv"
    summary_path = outdir / "summary.json"
    assert csv_path.exists()
    assert observables_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["case"] == "TH front-chamber throat-side smoke"
    assert summary["topology"] == FRONT_CHAMBER_THROAT_SIDE_TOPOLOGY
    assert summary["no_frontend_contract_change"] is True
    assert "front_chamber_throat_side_compare.csv" in summary["generated_files"]
    assert "front_chamber_throat_side_observables.csv" in summary["generated_files"]
