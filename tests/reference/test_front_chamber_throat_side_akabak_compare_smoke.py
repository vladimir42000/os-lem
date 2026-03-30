from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.reference_front_chamber_throat_side import (
    FRONT_CHAMBER_THROAT_SIDE_TOPOLOGY,
    NO_FRONTEND_CONTRACT_CHANGE,
    build_front_chamber_throat_side_model_dict,
    compare_front_chamber_throat_side_against_akabak,
    write_front_chamber_throat_side_compare_outputs,
)
from os_lem.reference_rear_chamber_tapped import load_rear_chamber_reference_bundle


REFERENCE_DIR = Path("tests/reference_data/akabak_rear_chamber_tapped")


def test_front_chamber_throat_side_reference_bundle_uses_existing_th_bundle() -> None:
    bundle = load_rear_chamber_reference_bundle(REFERENCE_DIR)

    assert bundle.impedance_magnitude_ohm.frequency_hz.shape == (120,)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_db.frequency_hz)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_phase_deg.frequency_hz)
    assert "AIYIMA Cu  taped horn" in bundle.script_text


def test_front_chamber_throat_side_smoke_compare_produces_bounded_current_metrics() -> None:
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
    assert comparison.oslem_pressure_db.shape == comparison.frequency_hz.shape
    assert np.all(np.isfinite(comparison.oslem_pressure_db))
    assert np.all(np.isfinite(comparison.oslem_impedance_magnitude_ohm))
    assert np.all(np.isfinite(comparison.observables["front_q_b_mag_m3_s"]))


def test_front_chamber_throat_side_compare_writer_emits_csv_summary_and_observables(tmp_path: Path) -> None:
    outdir = tmp_path / "front_chamber_throat_side_compare"
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


def test_front_chamber_throat_side_model_dict_matches_the_bounded_current_supported_case() -> None:
    model_dict = build_front_chamber_throat_side_model_dict()
    element_ids = {element["id"] for element in model_dict["elements"]}

    assert NO_FRONTEND_CONTRACT_CHANGE is True
    assert element_ids == {
        "rear_chamber",
        "throat_chamber",
        "front_chamber",
        "rear_port",
        "throat_entry",
        "blind_upstream",
        "blind_downstream",
        "stem",
        "main_leg",
        "tap_upstream",
        "tap_downstream",
        "front_coupling",
        "exit",
        "mouth_rad",
    }

    rear_port = next(element for element in model_dict["elements"] if element["id"] == "rear_port")
    throat_entry = next(element for element in model_dict["elements"] if element["id"] == "throat_entry")
    blind_upstream = next(element for element in model_dict["elements"] if element["id"] == "blind_upstream")
    blind_downstream = next(element for element in model_dict["elements"] if element["id"] == "blind_downstream")
    stem = next(element for element in model_dict["elements"] if element["id"] == "stem")
    tap_up = next(element for element in model_dict["elements"] if element["id"] == "tap_upstream")
    tap_down = next(element for element in model_dict["elements"] if element["id"] == "tap_downstream")
    front_coupling = next(element for element in model_dict["elements"] if element["id"] == "front_coupling")
    main_leg = next(element for element in model_dict["elements"] if element["id"] == "main_leg")
    exit_line = next(element for element in model_dict["elements"] if element["id"] == "exit")
    mouth = next(element for element in model_dict["elements"] if element["id"] == "mouth_rad")

    assert rear_port["node_a"] == "rear"
    assert rear_port["node_b"] == throat_entry["node_a"] == "inject"
    assert throat_entry["node_b"] == blind_upstream["node_a"] == stem["node_a"] == "throat"
    assert blind_upstream["node_b"] == blind_downstream["node_a"] == front_coupling["node_b"] == "throat_side"
    assert blind_downstream["node_b"] == "blind"
    assert front_coupling["node_a"] == "front"
    assert stem["node_b"] == main_leg["node_a"] == tap_up["node_a"] == "split"
    assert tap_up["node_b"] == tap_down["node_a"] == "tap"
    assert main_leg["node_b"] == tap_down["node_b"] == exit_line["node_a"] == "merge"
    assert exit_line["node_b"] == mouth["node"] == "mouth"
