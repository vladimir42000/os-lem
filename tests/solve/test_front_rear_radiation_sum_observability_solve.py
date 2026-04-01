from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.solve import (
    front_rear_radiation_sum_pressure,
    front_rear_radiation_sum_spl,
    radiator_observation_pressure,
    radiator_spl,
    solve_frequency_sweep,
)


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "front_rear_sum_demo", "radiation_space": "2pi"},
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
        "observations": [],
    }


def test_front_rear_radiation_sum_pressure_matches_manual_two_radiator_pressure_sum() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, np.array([80.0, 160.0, 320.0]))

    observability = system.front_rear_radiation_sum_observabilities[0]
    p_front = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space="2pi")
    p_rear = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")
    expected = p_front + p_rear

    combined = front_rear_radiation_sum_pressure(sweep, system, observability, 1.0, radiation_space="2pi")
    combined_spl = front_rear_radiation_sum_spl(sweep, system, observability, 1.0, radiation_space="2pi")
    rear_only_spl = radiator_spl(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")

    np.testing.assert_allclose(combined, expected, rtol=1e-10, atol=1e-12)
    assert combined.shape == (3,)
    assert np.all(np.isfinite(combined_spl))
    assert not np.allclose(combined_spl, rear_only_spl)
