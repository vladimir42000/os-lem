from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import build_back_loaded_horn_model_dict
from os_lem.solve import (
    radiator_observation_pressure,
    rear_radiation_path_group_delay,
    rear_radiation_path_phase_deg,
    rear_radiation_path_pressure_transfer,
    solve_frequency_sweep,
)


FREQUENCIES_HZ = np.array([50.0, 80.0, 125.0, 200.0, 315.0, 500.0])


def test_rear_radiation_path_pressure_transfer_matches_manual_rear_over_front_ratio() -> None:
    model, warnings = normalize_model(build_back_loaded_horn_model_dict())
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, FREQUENCIES_HZ)

    observability = system.rear_radiation_delay_path_observabilities[0]
    p_front = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space="2pi")
    p_rear = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")
    expected = p_rear / p_front

    transfer = rear_radiation_path_pressure_transfer(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )

    np.testing.assert_allclose(transfer, expected, rtol=1e-10, atol=1e-12)
    assert transfer.shape == (FREQUENCIES_HZ.size,)
    assert np.all(np.isfinite(transfer))


def test_rear_radiation_path_phase_and_group_delay_are_finite_and_nontrivial() -> None:
    model, warnings = normalize_model(build_back_loaded_horn_model_dict())
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, FREQUENCIES_HZ)

    observability = system.rear_radiation_delay_path_observabilities[0]
    phase_deg = rear_radiation_path_phase_deg(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
    group_delay_s = rear_radiation_path_group_delay(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )

    assert phase_deg.shape == (FREQUENCIES_HZ.size,)
    assert group_delay_s.shape == (FREQUENCIES_HZ.size,)
    assert np.all(np.isfinite(phase_deg))
    assert np.all(np.isfinite(group_delay_s))
    assert not np.allclose(phase_deg, phase_deg[0])
    assert not np.allclose(group_delay_s, 0.0)
    assert np.max(np.abs(group_delay_s)) < 0.1
