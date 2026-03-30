from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.reference_driver_front_chamber import (
    DRIVER_FRONT_CHAMBER_TOPOLOGY,
    NO_FRONTEND_CONTRACT_CHANGE,
    build_driver_front_chamber_model_dict,
    compare_driver_front_chamber_against_akabak,
    write_driver_front_chamber_compare_outputs,
)
from os_lem.reference_rear_chamber_tapped import load_rear_chamber_reference_bundle


REFERENCE_DIR = Path("tests/reference_data/akabak_rear_chamber_tapped")


def test_driver_front_chamber_reference_bundle_uses_existing_th_bundle() -> None:
    bundle = load_rear_chamber_reference_bundle(REFERENCE_DIR)

    assert bundle.impedance_magnitude_ohm.frequency_hz.shape == (120,)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_db.frequency_hz)
    np.testing.assert_array_equal(bundle.impedance_magnitude_ohm.frequency_hz, bundle.pressure_phase_deg.frequency_hz)
    assert "AIYIMA Cu  taped horn" in bundle.script_text


def test_driver_front_chamber_smoke_compare_produces_bounded_current_metrics() -> None:
    comparison = compare_driver_front_chamber_against_akabak(REFERENCE_DIR)

    assert comparison.topology == DRIVER_FRONT_CHAMBER_TOPOLOGY
    assert comparison.metrics["frequency_grid_shared"] is True
    assert comparison.metrics["reference_impedance_phase_available"] is False
    assert comparison.metrics["no_frontend_contract_change"] is True
    assert comparison.metrics["frequency_point_count"] == 120.0
    assert comparison.metrics["zmag_overall_corr"] > 0.20
    assert comparison.metrics["zmag_overall_mae_ohm"] < 30.0
    assert comparison.metrics["pressure_db_overall_corr"] > 0.75
    assert comparison.metrics["pressure_db_overall_mae"] < 15.0
    assert comparison.metrics["pressure_phase_overall_mae_deg"] < 90.0
    assert comparison.metrics["blind_closed_end_max_abs_m3_s"] < 1.0e-10
    assert comparison.metrics["front_tap_balance_mae_m3_s"] < 1.0e-10
    assert comparison.oslem_pressure_db.shape == comparison.frequency_hz.shape
    assert np.all(np.isfinite(comparison.oslem_pressure_db))
    assert np.all(np.isfinite(comparison.oslem_impedance_magnitude_ohm))
    assert np.all(np.isfinite(comparison.observables["front_q_b_mag_m3_s"]))


def test_driver_front_chamber_compare_writer_emits_csv_summary_and_observables(tmp_path: Path) -> None:
    outdir = tmp_path / "driver_front_chamber_compare"
    write_driver_front_chamber_compare_outputs(REFERENCE_DIR, outdir)

    csv_path = outdir / "driver_front_chamber_compare.csv"
    observables_path = outdir / "driver_front_chamber_observables.csv"
    summary_path = outdir / "summary.json"
    assert csv_path.exists()
    assert observables_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["case"] == "TH driver-front chamber smoke"
    assert summary["topology"] == DRIVER_FRONT_CHAMBER_TOPOLOGY
    assert summary["no_frontend_contract_change"] is True
    assert "driver_front_chamber_compare.csv" in summary["generated_files"]
    assert "driver_front_chamber_observables.csv" in summary["generated_files"]


def test_driver_front_chamber_model_dict_matches_the_bounded_current_supported_case() -> None:
    model_dict = build_driver_front_chamber_model_dict()
    element_ids = {element["id"] for element in model_dict["elements"]}

    assert NO_FRONTEND_CONTRACT_CHANGE is True
    assert element_ids == {
        "rear_chamber",
        "throat_chamber",
        "front_chamber",
        "rear_port",
        "throat_entry",
        "blind_segment",
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
    blind_segment = next(element for element in model_dict["elements"] if element["id"] == "blind_segment")
    stem = next(element for element in model_dict["elements"] if element["id"] == "stem")
    tap_up = next(element for element in model_dict["elements"] if element["id"] == "tap_upstream")
    tap_down = next(element for element in model_dict["elements"] if element["id"] == "tap_downstream")
    front_coupling = next(element for element in model_dict["elements"] if element["id"] == "front_coupling")
    main_leg = next(element for element in model_dict["elements"] if element["id"] == "main_leg")
    exit_line = next(element for element in model_dict["elements"] if element["id"] == "exit")
    mouth = next(element for element in model_dict["elements"] if element["id"] == "mouth_rad")

    assert rear_port["node_a"] == "rear"
    assert rear_port["node_b"] == throat_entry["node_a"] == "inject"
    assert throat_entry["node_b"] == blind_segment["node_a"] == stem["node_a"] == "throat"
    assert blind_segment["node_b"] == "blind"
    assert stem["node_b"] == main_leg["node_a"] == tap_up["node_a"] == "split"
    assert tap_up["node_b"] == tap_down["node_a"] == front_coupling["node_b"] == "tap"
    assert front_coupling["node_a"] == "front"
    assert main_leg["node_b"] == tap_down["node_b"] == exit_line["node_a"] == "merge"
    assert exit_line["node_b"] == mouth["node"] == "mouth"
