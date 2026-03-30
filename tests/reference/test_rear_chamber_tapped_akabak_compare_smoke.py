from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.reference_rear_chamber_tapped import (
    NO_FRONTEND_CONTRACT_CHANGE,
    REAR_CHAMBER_TAPPED_TOPOLOGY,
    build_rear_chamber_tapped_model_dict,
    compare_rear_chamber_tapped_against_akabak,
    load_rear_chamber_reference_bundle,
    write_rear_chamber_tapped_compare_outputs,
)


REFERENCE_DIR = Path("tests/reference_data/akabak_rear_chamber_tapped")


def test_rear_chamber_reference_bundle_uses_one_shared_frequency_grid() -> None:
    bundle = load_rear_chamber_reference_bundle(REFERENCE_DIR)

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
    assert "AIYIMA Cu  taped horn" in bundle.script_text


def test_rear_chamber_tapped_smoke_compare_produces_bounded_current_metrics() -> None:
    comparison = compare_rear_chamber_tapped_against_akabak(REFERENCE_DIR)

    assert comparison.topology == REAR_CHAMBER_TAPPED_TOPOLOGY
    assert comparison.metrics["frequency_grid_shared"] is True
    assert comparison.metrics["reference_impedance_phase_available"] is False
    assert comparison.metrics["no_frontend_contract_change"] is True
    assert comparison.metrics["frequency_point_count"] == 120
    assert comparison.metrics["zmag_high_band_corr"] > 0.99
    assert comparison.metrics["pressure_db_low_band_corr"] > 0.80
    assert comparison.metrics["pressure_db_overall_mae"] < 8.0
    assert comparison.metrics["zmag_overall_mae_ohm"] < 30.0
    assert comparison.metrics["pressure_phase_overall_mae_deg"] < 120.0
    assert comparison.oslem_pressure_db.shape == comparison.frequency_hz.shape
    assert comparison.oslem_impedance_magnitude_ohm.shape == comparison.frequency_hz.shape
    assert np.all(np.isfinite(comparison.oslem_pressure_db))
    assert np.all(np.isfinite(comparison.oslem_impedance_magnitude_ohm))
    assert np.all(np.isfinite(comparison.observables["stem_q_b_mag_m3_s"]))


def test_rear_chamber_compare_writer_emits_csv_summary_and_observables(tmp_path: Path) -> None:
    outdir = tmp_path / "rear_chamber_compare"
    write_rear_chamber_tapped_compare_outputs(REFERENCE_DIR, outdir)

    csv_path = outdir / "rear_chamber_tapped_compare.csv"
    observables_path = outdir / "rear_chamber_tapped_observables.csv"
    summary_path = outdir / "summary.json"
    assert csv_path.exists()
    assert observables_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["case"] == "TH rear-chamber tapped smoke"
    assert summary["topology"] == REAR_CHAMBER_TAPPED_TOPOLOGY
    assert summary["no_frontend_contract_change"] is True
    assert "rear_chamber_tapped_compare.csv" in summary["generated_files"]
    assert "rear_chamber_tapped_observables.csv" in summary["generated_files"]


def test_rear_chamber_model_dict_matches_the_bounded_current_supported_case() -> None:
    model_dict = build_rear_chamber_tapped_model_dict()
    element_ids = {element["id"] for element in model_dict["elements"]}

    assert NO_FRONTEND_CONTRACT_CHANGE is True
    assert element_ids == {
        "rear_chamber",
        "stem",
        "main_leg",
        "tap_upstream",
        "tap_downstream",
        "exit",
        "mouth_rad",
    }

    stem = next(element for element in model_dict["elements"] if element["id"] == "stem")
    main_leg = next(element for element in model_dict["elements"] if element["id"] == "main_leg")
    tap_up = next(element for element in model_dict["elements"] if element["id"] == "tap_upstream")
    tap_down = next(element for element in model_dict["elements"] if element["id"] == "tap_downstream")
    exit_line = next(element for element in model_dict["elements"] if element["id"] == "exit")
    mouth = next(element for element in model_dict["elements"] if element["id"] == "mouth_rad")

    assert stem["node_a"] == "rear"
    assert stem["node_b"] == main_leg["node_a"] == tap_up["node_a"] == "split"
    assert tap_up["node_b"] == tap_down["node_a"] == "tap"
    assert main_leg["node_b"] == tap_down["node_b"] == exit_line["node_a"] == "merge"
    assert exit_line["node_b"] == mouth["node"] == "mouth"
