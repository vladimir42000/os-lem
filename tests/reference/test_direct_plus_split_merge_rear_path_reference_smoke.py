from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_split_merge_rear_path import (
    DEFAULT_FREQUENCIES_HZ,
    DIRECT_PLUS_SPLIT_MERGE_REAR_PATH_TOPOLOGY,
    NO_FRONTEND_CONTRACT_CHANGE,
    build_direct_plus_split_merge_rear_path_model_dict,
    compare_direct_plus_split_merge_rear_path_against_refined_reference,
    write_direct_plus_split_merge_rear_path_compare_outputs,
)


def test_direct_plus_split_merge_rear_path_smoke_model_assembles_one_supported_skeleton() -> None:
    model_dict = build_direct_plus_split_merge_rear_path_model_dict()
    normalized, warnings = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True
    assert len(system.split_merge_horn_skeletons) == 1
    assert len(system.direct_plus_split_merge_rear_path_skeletons) == 1

    skeleton = system.direct_plus_split_merge_rear_path_skeletons[0]
    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.rear_leg_element_ids == ("leg_main", "leg_aux")
    assert skeleton.shared_exit_element_id == "shared_exit"
    assert skeleton.rear_mouth_radiator_id == "rear_mouth_rad"


def test_direct_plus_split_merge_rear_path_smoke_run_simulation_preserves_split_merge_balance() -> None:
    frequencies_hz = np.array([60.0, 120.0, 240.0, 480.0])
    result = run_simulation(build_direct_plus_split_merge_rear_path_model_dict(), frequencies_hz)

    assert result.units["p_split"] == "Pa"
    assert result.units["exit_q_b"] == "m^3/s"
    assert result.units["spl_total"] == "dB"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["spl_front"]))
    assert np.all(np.isfinite(result.series["spl_rear"]))
    assert np.all(np.isfinite(result.series["spl_total"]))

    np.testing.assert_allclose(
        result.series["stem_q_b"],
        result.series["main_q_a"] + result.series["aux_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.series["exit_q_a"],
        result.series["main_q_b"] + result.series["aux_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.series["rear_rad_q"],
        result.series["exit_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(result.series["main_q_a"], result.series["aux_q_a"])
    assert not np.allclose(result.series["spl_total"], result.series["spl_front"])
    assert not np.allclose(result.series["spl_total"], result.series["spl_rear"])


def test_direct_plus_split_merge_rear_path_smoke_compare_produces_bounded_refinement_metrics() -> None:
    comparison = compare_direct_plus_split_merge_rear_path_against_refined_reference()

    assert comparison.topology == DIRECT_PLUS_SPLIT_MERGE_REAR_PATH_TOPOLOGY
    assert comparison.metrics["frequency_grid_shared"] is True
    assert comparison.metrics["reference_kind"] == "refined_segmentation_surrogate"
    assert comparison.metrics["reference_refinement_factor"] == 2.0
    assert comparison.metrics["no_frontend_contract_change"] is True
    assert comparison.metrics["frequency_point_count"] == float(DEFAULT_FREQUENCIES_HZ.size)
    assert comparison.metrics["zmag_shape_corr"] > 0.999
    assert comparison.metrics["zmag_shape_normalized_mae"] < 0.01
    assert comparison.metrics["front_spl_centered_mae"] < 0.10
    assert comparison.metrics["rear_spl_centered_mae"] < 0.10
    assert comparison.metrics["total_spl_centered_mae"] < 0.10
    assert comparison.metrics["split_balance_mae_m3_s"] < 1.0e-10
    assert comparison.metrics["merge_balance_mae_m3_s"] < 1.0e-10
    assert comparison.metrics["rear_exit_match_mae_m3_s"] < 1.0e-10
    assert comparison.metrics["main_aux_inflow_delta_centered_mae_m3_s"] < 1.0e-4
    assert comparison.metrics["main_aux_inflow_delta_span_m3_s"] > 1.0e-4
    assert comparison.metrics["rear_minus_front_span_db"] > 20.0
    assert comparison.metrics["total_minus_front_span_db"] > 20.0
    assert np.all(np.isfinite(comparison.base_total_spl_db))
    assert np.all(np.isfinite(comparison.refined_total_spl_db))
    assert np.all(np.isfinite(comparison.observables["base_main_aux_inflow_delta_mag_m3_s"]))


def test_direct_plus_split_merge_rear_path_compare_writer_emits_csv_summary_and_observables(tmp_path: Path) -> None:
    outdir = tmp_path / "direct_plus_split_merge_rear_path_compare"
    write_direct_plus_split_merge_rear_path_compare_outputs(outdir)

    csv_path = outdir / "direct_plus_split_merge_rear_path_compare.csv"
    observables_path = outdir / "direct_plus_split_merge_rear_path_observables.csv"
    summary_path = outdir / "summary.json"
    assert csv_path.exists()
    assert observables_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["case"] == "direct-plus-split-merge-rear-path smoke"
    assert summary["topology"] == DIRECT_PLUS_SPLIT_MERGE_REAR_PATH_TOPOLOGY
    assert summary["no_frontend_contract_change"] is True
    assert "direct_plus_split_merge_rear_path_compare.csv" in summary["generated_files"]
    assert "direct_plus_split_merge_rear_path_observables.csv" in summary["generated_files"]
