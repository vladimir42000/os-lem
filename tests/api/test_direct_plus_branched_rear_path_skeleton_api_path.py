from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


NO_FRONTEND_CONTRACT_CHANGE = True


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "direct_plus_branched_rear_path_demo", "radiation_space": "2pi"},
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
                "id": "rear_main_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_main",
                "length": "45 cm",
                "area_start": "95 cm2",
                "area_end": "110 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "rear_aux_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_aux",
                "length": "26 cm",
                "area_start": "40 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_main_rad",
                "type": "radiator",
                "node": "rear_mouth_main",
                "model": "flanged_piston",
                "area": "110 cm2",
            },
            {
                "id": "rear_aux_rad",
                "type": "radiator",
                "node": "rear_mouth_aux",
                "model": "flanged_piston",
                "area": "55 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_junction", "type": "node_pressure", "target": "junction"},
            {"id": "front_q", "type": "element_volume_velocity", "target": "front_rad"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "rear_main_leg", "location": "a"},
            {"id": "aux_q_a", "type": "element_volume_velocity", "target": "rear_aux_leg", "location": "a"},
            {"id": "main_rad_q", "type": "element_volume_velocity", "target": "rear_main_rad"},
            {"id": "aux_rad_q", "type": "element_volume_velocity", "target": "rear_aux_rad"},
            {"id": "spl_front", "type": "spl", "target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_main", "type": "spl", "target": "rear_main_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_aux", "type": "spl", "target": "rear_aux_rad", "distance": "1 m", "radiation_space": "2pi"},
        ],
    }


def test_run_simulation_supports_direct_plus_branched_rear_path_skeleton_end_to_end() -> None:
    model_dict = _model_dict()
    frequencies = np.array([60.0, 120.0, 240.0])

    result = run_simulation(model_dict, frequencies)
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)

    assert len(system.direct_plus_branched_rear_path_skeletons) == 1
    assert result.units["p_junction"] == "Pa"
    assert result.units["front_q"] == "m^3/s"
    assert result.units["main_rad_q"] == "m^3/s"
    assert result.units["aux_rad_q"] == "m^3/s"
    assert result.units["spl_front"] == "dB"
    assert result.units["spl_main"] == "dB"
    assert result.units["spl_aux"] == "dB"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["p_junction"].real))
    assert np.all(np.isfinite(result.series["p_junction"].imag))
    assert np.all(np.isfinite(result.series["spl_front"]))
    assert np.all(np.isfinite(result.series["spl_main"]))
    assert np.all(np.isfinite(result.series["spl_aux"]))

    np.testing.assert_allclose(
        result.series["stem_q_b"],
        result.series["main_q_a"] + result.series["aux_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(result.series["spl_main"], result.series["spl_aux"])
