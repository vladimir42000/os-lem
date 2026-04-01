from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "back_loaded_horn_demo", "radiation_space": "2pi"},
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
            {"id": "rear_chamber", "type": "volume", "node": "rear", "value": "10 l"},
            {"id": "throat_chamber", "type": "volume", "node": "throat", "value": "1.6 l"},
            {"id": "rear_port", "type": "waveguide_1d", "node_a": "rear", "node_b": "inject", "length": "11 cm", "area_start": "42 cm2", "area_end": "45 cm2", "profile": "conical", "segments": 2},
            {"id": "throat_entry", "type": "waveguide_1d", "node_a": "inject", "node_b": "throat", "length": "8 cm", "area_start": "45 cm2", "area_end": "48 cm2", "profile": "conical", "segments": 2},
            {"id": "blind_upstream", "type": "waveguide_1d", "node_a": "throat", "node_b": "throat_side", "length": "4 cm", "area_start": "48 cm2", "area_end": "41 cm2", "profile": "conical", "segments": 2},
            {"id": "blind_downstream", "type": "waveguide_1d", "node_a": "throat_side", "node_b": "blind", "length": "5 cm", "area_start": "41 cm2", "area_end": "39 cm2", "profile": "conical", "segments": 2},
            {"id": "rear_leg", "type": "waveguide_1d", "node_a": "throat", "node_b": "mouth", "length": "61 cm", "area_start": "48 cm2", "area_end": "105 cm2", "profile": "conical", "segments": 7},
            {"id": "front_rad", "type": "radiator", "node": "front", "model": "flanged_piston", "area": "130 cm2"},
            {"id": "mouth_rad", "type": "radiator", "node": "mouth", "model": "flanged_piston", "area": "105 cm2"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_front", "type": "node_pressure", "target": "front"},
            {"id": "p_mouth", "type": "node_pressure", "target": "mouth"},
            {"id": "front_q", "type": "element_volume_velocity", "target": "front_rad"},
            {"id": "mouth_q", "type": "element_volume_velocity", "target": "mouth_rad"},
            {"id": "rear_leg_q_a", "type": "element_volume_velocity", "target": "rear_leg", "location": "a"},
            {"id": "rear_leg_q_b", "type": "element_volume_velocity", "target": "rear_leg", "location": "b"},
            {"id": "blind_down_q_b", "type": "element_volume_velocity", "target": "blind_downstream", "location": "b"},
        ],
    }


def test_run_simulation_supports_back_loaded_horn_skeleton_end_to_end() -> None:
    model_dict = _model_dict()
    frequencies = np.array([80.0, 160.0, 320.0])

    result = run_simulation(model_dict, frequencies)
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert len(system.back_loaded_horn_skeletons) == 1
    assert result.units["p_front"] == "Pa"
    assert result.units["mouth_q"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["front_q"]))
    assert np.all(np.isfinite(result.series["mouth_q"]))
    assert np.all(np.isfinite(result.series["rear_leg_q_a"]))
    assert np.all(np.isfinite(result.series["rear_leg_q_b"]))
    assert np.all(np.abs(result.series["blind_down_q_b"]) < 1.0e-10)
    assert not np.allclose(result.series["p_front"], result.series["p_mouth"])
