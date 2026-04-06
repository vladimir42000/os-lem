from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


NO_FRONTEND_CONTRACT_CHANGE = True


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "direct_plus_branched_split_merge_rear_path_demo", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "front",
            "node_rear": "rear",
        },
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "flanged_piston",
                "area": "132 cm2",
            },
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "junction",
                "length": "20 cm",
                "area_start": "82 cm2",
                "area_end": "88 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "direct_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_direct",
                "length": "34 cm",
                "area_start": "88 cm2",
                "area_end": "96 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "split_feed",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "split",
                "length": "18 cm",
                "area_start": "44 cm2",
                "area_end": "50 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "merge_main",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "26 cm",
                "area_start": "50 cm2",
                "area_end": "58 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "merge_aux",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "31 cm",
                "area_start": "42 cm2",
                "area_end": "47 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "shared_exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "rear_mouth_merged",
                "length": "22 cm",
                "area_start": "58 cm2",
                "area_end": "62 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_direct_rad",
                "type": "radiator",
                "node": "rear_mouth_direct",
                "model": "flanged_piston",
                "area": "96 cm2",
            },
            {
                "id": "rear_merged_rad",
                "type": "radiator",
                "node": "rear_mouth_merged",
                "model": "flanged_piston",
                "area": "62 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_junction", "type": "node_pressure", "target": "junction"},
            {"id": "p_split", "type": "node_pressure", "target": "split"},
            {"id": "p_merge", "type": "node_pressure", "target": "merge"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "direct_q_a", "type": "element_volume_velocity", "target": "direct_leg", "location": "a"},
            {"id": "feed_q_a", "type": "element_volume_velocity", "target": "split_feed", "location": "a"},
            {"id": "feed_q_b", "type": "element_volume_velocity", "target": "split_feed", "location": "b"},
            {"id": "direct_q_b", "type": "element_volume_velocity", "target": "direct_leg", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "merge_main", "location": "a"},
            {"id": "aux_q_a", "type": "element_volume_velocity", "target": "merge_aux", "location": "a"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "merge_main", "location": "b"},
            {"id": "aux_q_b", "type": "element_volume_velocity", "target": "merge_aux", "location": "b"},
            {"id": "exit_q_a", "type": "element_volume_velocity", "target": "shared_exit", "location": "a"},
            {"id": "exit_q_b", "type": "element_volume_velocity", "target": "shared_exit", "location": "b"},
            {"id": "direct_rad_q", "type": "element_volume_velocity", "target": "rear_direct_rad"},
            {"id": "merged_rad_q", "type": "element_volume_velocity", "target": "rear_merged_rad"},
            {"id": "spl_front", "type": "spl", "target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_direct_rear", "type": "spl", "target": "rear_direct_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_merged_rear", "type": "spl", "target": "rear_merged_rad", "distance": "1 m", "radiation_space": "2pi"},
        ],
    }


def test_run_simulation_supports_direct_plus_branched_split_merge_rear_path_skeleton_end_to_end() -> None:
    model_dict = _model_dict()
    frequencies = np.array([80.0, 160.0, 320.0])

    result = run_simulation(model_dict, frequencies)
    normalized, warnings = normalize_model(model_dict)
    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(normalized)

    assert len(system.direct_plus_branched_split_merge_rear_path_skeletons) == 1
    assert result.units["p_junction"] == "Pa"
    assert result.units["p_split"] == "Pa"
    assert result.units["p_merge"] == "Pa"
    assert result.units["stem_q_b"] == "m^3/s"
    assert result.units["direct_rad_q"] == "m^3/s"
    assert result.units["merged_rad_q"] == "m^3/s"
    assert result.units["spl_front"] == "dB"
    assert result.units["spl_direct_rear"] == "dB"
    assert result.units["spl_merged_rear"] == "dB"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["p_junction"].real))
    assert np.all(np.isfinite(result.series["p_split"].imag))
    assert np.all(np.isfinite(result.series["p_merge"].imag))
    assert np.all(np.isfinite(result.series["spl_front"]))
    assert np.all(np.isfinite(result.series["spl_direct_rear"]))
    assert np.all(np.isfinite(result.series["spl_merged_rear"]))

    np.testing.assert_allclose(
        result.series["stem_q_b"],
        result.series["direct_q_a"] + result.series["feed_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.series["feed_q_b"],
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
        result.series["direct_rad_q"],
        result.series["direct_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.series["merged_rad_q"],
        result.series["exit_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(result.series["spl_direct_rear"], result.series["spl_merged_rear"])
