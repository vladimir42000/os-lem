from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


def _split_merge_model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "split_merge_horn_demo", "radiation_space": "2pi"},
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
                "node_b": "split",
                "length": "22 cm",
                "area_start": "85 cm2",
                "area_end": "90 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "leg_main",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "40 cm",
                "area_start": "90 cm2",
                "area_end": "105 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "leg_tap",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "28 cm",
                "area_start": "55 cm2",
                "area_end": "65 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "mouth",
                "length": "34 cm",
                "area_start": "105 cm2",
                "area_end": "108 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "flanged_piston",
                "area": "108 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_split", "type": "node_pressure", "target": "split"},
            {"id": "p_merge", "type": "node_pressure", "target": "merge"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "leg_main", "location": "a"},
            {"id": "tap_q_a", "type": "element_volume_velocity", "target": "leg_tap", "location": "a"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "leg_main", "location": "b"},
            {"id": "tap_q_b", "type": "element_volume_velocity", "target": "leg_tap", "location": "b"},
            {"id": "exit_q_a", "type": "element_volume_velocity", "target": "exit", "location": "a"},
            {"id": "exit_q_b", "type": "element_volume_velocity", "target": "exit", "location": "b"},
            {"id": "mouth_rad_q", "type": "element_volume_velocity", "target": "mouth_rad"},
            {"id": "spl_total", "type": "spl", "target": "mouth_rad", "distance": "1 m", "radiation_space": "2pi"},
        ],
    }


def test_run_simulation_supports_split_merge_horn_skeleton_end_to_end() -> None:
    model_dict = _split_merge_model_dict()
    frequencies = np.array([70.0, 140.0, 280.0])

    result = run_simulation(model_dict, frequencies)
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert len(system.parallel_branch_bundles) == 1
    assert len(system.acoustic_junctions) == 2
    assert len(system.split_merge_horn_skeletons) == 1
    assert result.series["spl_total"].shape == (3,)
    assert result.units["p_split"] == "Pa"
    assert result.units["exit_q_a"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["spl_total"]))
    assert np.all(np.isfinite(result.series["p_split"].real))
    assert np.all(np.isfinite(result.series["p_merge"].imag))

    np.testing.assert_allclose(
        result.series["stem_q_b"],
        result.series["main_q_a"] + result.series["tap_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.series["exit_q_a"],
        result.series["main_q_b"] + result.series["tap_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(result.series["exit_q_b"], result.series["mouth_rad_q"], rtol=1e-10, atol=1e-12)
    assert not np.allclose(result.series["main_q_a"], result.series["tap_q_a"])
