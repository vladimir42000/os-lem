from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side import (
    build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict,
)
from os_lem.solve import (
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_spl,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_spl,
    radiator_observation_pressure,
    solve_frequency_sweep,
    summed_radiator_observation_pressure,
)


def test_solve_frequency_sweep_supports_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contract() -> None:
    model, warnings = normalize_model(
        build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict()
    )
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, np.array([60.0, 120.0, 240.0, 480.0]))

    assert len(system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts) == 1
    contract = system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts[0]

    front_pressure = direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_pressure(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    rear_pressure = direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_pressure(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )

    expected_front_pressure = radiator_observation_pressure(
        sweep,
        system,
        contract.front_radiator_id,
        1.0,
        radiation_space="2pi",
    )
    expected_rear_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [
            {"target": contract.direct_rear_mouth_radiator_id, "distance": 1.0},
            {"target": contract.merged_rear_mouth_radiator_id, "distance": 1.0},
        ],
        radiation_space="2pi",
    )

    np.testing.assert_allclose(front_pressure, expected_front_pressure, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(rear_pressure, expected_rear_pressure, rtol=1e-10, atol=1e-12)
    assert np.all(np.isfinite(front_pressure.real))
    assert np.all(np.isfinite(front_pressure.imag))
    assert np.all(np.isfinite(rear_pressure.real))
    assert np.all(np.isfinite(rear_pressure.imag))
    assert not np.allclose(front_pressure, rear_pressure)


def test_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_spl_is_finite_and_distinct() -> None:
    model, warnings = normalize_model(
        build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict()
    )
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, np.array([70.0, 140.0, 280.0, 560.0]))
    contract = system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts[0]

    front_spl = direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_spl(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    rear_spl = direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_spl(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )

    assert np.all(np.isfinite(front_spl))
    assert np.all(np.isfinite(rear_spl))
    assert front_spl.shape == rear_spl.shape == (4,)
    assert not np.allclose(front_spl, rear_spl)
