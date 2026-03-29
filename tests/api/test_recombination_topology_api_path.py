from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


def _recombination_model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "recombination_demo", "radiation_space": "2pi"},
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
                "id": "path_main",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "merge",
                "length": "48 cm",
                "area_start": "90 cm2",
                "area_end": "85 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "path_tap",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "merge",
                "length": "29 cm",
                "area_start": "45 cm2",
                "area_end": "40 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "shared_exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "mouth",
                "length": "34 cm",
                "area_start": "125 cm2",
                "area_end": "150 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "flanged_piston",
                "area": "150 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_merge", "type": "node_pressure", "target": "merge"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "path_main", "location": "b"},
            {"id": "tap_q_b", "type": "element_volume_velocity", "target": "path_tap", "location": "b"},
            {"id": "exit_q_a", "type": "element_volume_velocity", "target": "shared_exit", "location": "a"},
            {"id": "exit_q_b", "type": "element_volume_velocity", "target": "shared_exit", "location": "b"},
            {"id": "mouth_rad_q", "type": "element_volume_velocity", "target": "mouth_rad"},
        ],
    }


def test_run_simulation_supports_recombination_topology_end_to_end() -> None:
    model_dict = _recombination_model_dict()
    frequencies = np.array([60.0, 120.0, 240.0])

    result = run_simulation(model_dict, frequencies)
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert len(system.recombination_topologies) == 1
    assert result.units["p_merge"] == "Pa"
    assert result.units["main_q_b"] == "m^3/s"
    assert result.units["mouth_rad_q"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["p_merge"].real))
    assert np.all(np.isfinite(result.series["p_merge"].imag))

    np.testing.assert_allclose(
        result.series["main_q_b"] + result.series["tap_q_b"],
        result.series["exit_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.series["exit_q_b"],
        result.series["mouth_rad_q"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(result.series["main_q_b"], result.series["tap_q_b"])
