from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


def _branched_horn_model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "branched_horn_demo", "radiation_space": "2pi"},
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
                "length": "30 cm",
                "area_start": "90 cm2",
                "area_end": "95 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "main_branch",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "mouth_main",
                "length": "45 cm",
                "area_start": "95 cm2",
                "area_end": "110 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "tap_branch",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "mouth_tap",
                "length": "26 cm",
                "area_start": "40 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "main_rad",
                "type": "radiator",
                "node": "mouth_main",
                "model": "flanged_piston",
                "area": "110 cm2",
            },
            {
                "id": "tap_rad",
                "type": "radiator",
                "node": "mouth_tap",
                "model": "flanged_piston",
                "area": "55 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_junction", "type": "node_pressure", "target": "junction"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "main_branch", "location": "a"},
            {"id": "tap_q_a", "type": "element_volume_velocity", "target": "tap_branch", "location": "a"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "main_branch", "location": "b"},
            {"id": "tap_q_b", "type": "element_volume_velocity", "target": "tap_branch", "location": "b"},
            {"id": "main_rad_q", "type": "element_volume_velocity", "target": "main_rad"},
            {"id": "tap_rad_q", "type": "element_volume_velocity", "target": "tap_rad"},
            {
                "id": "spl_total",
                "type": "spl_sum",
                "radiation_space": "2pi",
                "terms": [
                    {"target": "main_rad", "distance": "1 m"},
                    {"target": "tap_rad", "distance": "1 m"},
                ],
            },
        ],
    }


def test_run_simulation_supports_branched_horn_skeleton_end_to_end() -> None:
    model_dict = _branched_horn_model_dict()
    frequencies = np.array([60.0, 120.0, 240.0])

    result = run_simulation(model_dict, frequencies)
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert len(system.branched_horn_skeletons) == 1
    assert result.series["spl_total"].shape == (3,)
    assert result.units["p_junction"] == "Pa"
    assert result.units["stem_q_b"] == "m^3/s"
    assert result.units["main_rad_q"] == "m^3/s"
    assert result.units["tap_rad_q"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["spl_total"]))
    assert np.all(np.isfinite(result.series["p_junction"].real))
    assert np.all(np.isfinite(result.series["p_junction"].imag))

    np.testing.assert_allclose(
        result.series["stem_q_b"],
        result.series["main_q_a"] + result.series["tap_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(result.series["main_q_b"], result.series["main_rad_q"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["tap_q_b"], result.series["tap_rad_q"], rtol=1e-10, atol=1e-12)
    assert not np.allclose(result.series["main_q_a"], result.series["tap_q_a"])
