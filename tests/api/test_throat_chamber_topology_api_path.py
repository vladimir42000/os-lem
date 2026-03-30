from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


def _throat_chamber_model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "throat_chamber_demo", "radiation_space": "2pi"},
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
            "node_front": "tap",
            "node_rear": "rear",
        },
        "elements": [
            {"id": "rear_chamber", "type": "volume", "node": "rear", "value": "10 l"},
            {"id": "throat_chamber", "type": "volume", "node": "throat", "value": "1.6 l"},
            {
                "id": "rear_port",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "inject",
                "length": "11 cm",
                "area_start": "42 cm2",
                "area_end": "45 cm2",
                "profile": "conical",
                "segments": 2,
            },
            {
                "id": "throat_entry",
                "type": "waveguide_1d",
                "node_a": "inject",
                "node_b": "throat",
                "length": "8 cm",
                "area_start": "45 cm2",
                "area_end": "48 cm2",
                "profile": "conical",
                "segments": 2,
            },
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "throat",
                "node_b": "split",
                "length": "19 cm",
                "area_start": "48 cm2",
                "area_end": "88 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "main_leg",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "46 cm",
                "area_start": "88 cm2",
                "area_end": "102 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "tap_upstream",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "tap",
                "length": "18 cm",
                "area_start": "52 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "tap_downstream",
                "type": "waveguide_1d",
                "node_a": "tap",
                "node_b": "merge",
                "length": "16 cm",
                "area_start": "55 cm2",
                "area_end": "62 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "mouth",
                "length": "32 cm",
                "area_start": "102 cm2",
                "area_end": "105 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "flanged_piston",
                "area": "105 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_inject", "type": "node_pressure", "target": "inject"},
            {"id": "p_throat", "type": "node_pressure", "target": "throat"},
            {"id": "p_tap", "type": "node_pressure", "target": "tap"},
            {"id": "rear_port_q_b", "type": "element_volume_velocity", "target": "rear_port", "location": "b"},
            {"id": "throat_entry_q_a", "type": "element_volume_velocity", "target": "throat_entry", "location": "a"},
            {"id": "throat_entry_q_b", "type": "element_volume_velocity", "target": "throat_entry", "location": "b"},
            {"id": "stem_q_a", "type": "element_volume_velocity", "target": "stem", "location": "a"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "main_leg", "location": "a"},
            {"id": "tap_up_q_a", "type": "element_volume_velocity", "target": "tap_upstream", "location": "a"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "main_leg", "location": "b"},
            {"id": "tap_down_q_b", "type": "element_volume_velocity", "target": "tap_downstream", "location": "b"},
            {"id": "exit_q_a", "type": "element_volume_velocity", "target": "exit", "location": "a"},
            {"id": "exit_q_b", "type": "element_volume_velocity", "target": "exit", "location": "b"},
            {"id": "mouth_rad_q", "type": "element_volume_velocity", "target": "mouth_rad"},
        ],
    }


def test_run_simulation_supports_throat_chamber_topology_end_to_end() -> None:
    model_dict = _throat_chamber_model_dict()
    frequencies = np.array([80.0, 160.0, 320.0])

    result = run_simulation(model_dict, frequencies)
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert len(system.throat_chamber_topologies) == 1
    assert result.units["p_throat"] == "Pa"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["p_inject"].real))
    assert np.all(np.isfinite(result.series["p_throat"].imag))

    np.testing.assert_allclose(result.series["rear_port_q_b"], result.series["throat_entry_q_a"], rtol=1e-10, atol=1e-12)
    assert np.all(np.abs(result.series["throat_entry_q_b"]) > np.abs(result.series["stem_q_a"]))
    np.testing.assert_allclose(
        result.series["stem_q_b"],
        result.series["main_q_a"] + result.series["tap_up_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        result.series["exit_q_a"],
        result.series["main_q_b"] + result.series["tap_down_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(result.series["exit_q_b"], result.series["mouth_rad_q"], rtol=1e-10, atol=1e-12)
    assert not np.allclose(result.series["p_inject"], result.series["p_throat"])
