from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_rear_path import build_direct_plus_branched_rear_path_model_dict
from os_lem.solve import (
    direct_plus_branched_rear_path_front_contribution_pressure,
    direct_plus_branched_rear_path_front_contribution_spl,
    direct_plus_branched_rear_path_rear_contribution_pressure,
    direct_plus_branched_rear_path_rear_contribution_spl,
    radiator_observation_pressure,
    radiator_spl,
    solve_frequency_sweep,
    summed_radiator_observation_pressure,
    summed_radiator_spl,
)


FREQUENCIES_HZ = np.array([60.0, 120.0, 240.0, 480.0])


def test_direct_plus_branched_rear_path_contribution_helpers_match_explicit_front_and_rear_sums() -> None:
    model, warnings = normalize_model(build_direct_plus_branched_rear_path_model_dict())
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, FREQUENCIES_HZ)

    contract = system.direct_plus_branched_rear_path_contribution_contracts[0]

    front_pressure = direct_plus_branched_rear_path_front_contribution_pressure(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    rear_pressure = direct_plus_branched_rear_path_rear_contribution_pressure(
        sweep,
        system,
        contract,
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
    expected_rear_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [
            {"target": "rear_main_rad", "distance": 1.0},
            {"target": "rear_aux_rad", "distance": 1.0},
        ],
        radiation_space="2pi",
    )
    front_spl = direct_plus_branched_rear_path_front_contribution_spl(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    rear_spl = direct_plus_branched_rear_path_rear_contribution_spl(
        sweep,
        system,
        contract,
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
    expected_rear_spl = summed_radiator_spl(
        sweep,
        system,
        [
            {"target": "rear_main_rad", "distance": 1.0},
            {"target": "rear_aux_rad", "distance": 1.0},
        ],
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
    assert not np.allclose(rear_pressure, radiator_observation_pressure(sweep, system, "rear_main_rad", 1.0, radiation_space="2pi"))
