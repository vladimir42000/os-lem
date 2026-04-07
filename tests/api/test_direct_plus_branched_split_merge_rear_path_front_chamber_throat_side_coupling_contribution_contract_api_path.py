from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side import (
    NO_FRONTEND_CONTRACT_CHANGE,
    build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict,
)
from os_lem.solve import (
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_spl,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_spl,
    solve_frequency_sweep,
)


def test_run_simulation_supports_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contract() -> None:
    model_dict = build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict()
    frequencies = np.array([60.0, 120.0, 240.0, 480.0])

    result = run_simulation(model_dict, frequencies)
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, frequencies)
    assert len(system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts) == 1
    contract = system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts[0]

    expected_front = direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_spl(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    expected_rear = direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_spl(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )

    np.testing.assert_allclose(result.series["spl_front"], expected_front, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["spl_rear_sum"], expected_rear, rtol=1e-10, atol=1e-12)
    assert result.units["spl_front"] == "dB"
    assert result.units["spl_rear_sum"] == "dB"
    assert np.all(np.isfinite(result.series["spl_front"]))
    assert np.all(np.isfinite(result.series["spl_rear_sum"]))
    assert not np.allclose(result.series["spl_front"], result.series["spl_rear_sum"])
