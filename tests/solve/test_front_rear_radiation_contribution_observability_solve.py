from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import build_back_loaded_horn_model_dict
from os_lem.solve import (
    front_radiation_contribution_pressure,
    front_radiation_contribution_spl,
    radiator_observation_pressure,
    radiator_spl,
    rear_radiation_contribution_pressure,
    rear_radiation_contribution_spl,
    solve_frequency_sweep,
)


FREQUENCIES_HZ = np.array([80.0, 160.0, 320.0])


def test_front_and_rear_radiation_contribution_helpers_match_direct_radiator_observations() -> None:
    model, warnings = normalize_model(build_back_loaded_horn_model_dict())
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, FREQUENCIES_HZ)

    observability = system.front_rear_radiation_contribution_observabilities[0]

    front_pressure = front_radiation_contribution_pressure(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
    rear_pressure = rear_radiation_contribution_pressure(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
    expected_front_pressure = radiator_observation_pressure(
        sweep,
        system,
        "front_rad",
        1.0,
        radiation_space="2pi",
    )
    expected_rear_pressure = radiator_observation_pressure(
        sweep,
        system,
        "mouth_rad",
        1.0,
        radiation_space="2pi",
    )
    front_spl = front_radiation_contribution_spl(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
    rear_spl = rear_radiation_contribution_spl(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
    expected_front_spl = radiator_spl(
        sweep,
        system,
        "front_rad",
        1.0,
        radiation_space="2pi",
    )
    expected_rear_spl = radiator_spl(
        sweep,
        system,
        "mouth_rad",
        1.0,
        radiation_space="2pi",
    )

    np.testing.assert_allclose(front_pressure, expected_front_pressure, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(rear_pressure, expected_rear_pressure, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(front_spl, expected_front_spl, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(rear_spl, expected_rear_spl, rtol=1e-10, atol=1e-12)
    assert front_pressure.shape == (FREQUENCIES_HZ.size,)
    assert rear_pressure.shape == (FREQUENCIES_HZ.size,)
    assert np.all(np.isfinite(front_spl))
    assert np.all(np.isfinite(rear_spl))
    assert not np.allclose(front_spl, rear_spl)
