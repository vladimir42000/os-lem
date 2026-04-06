from __future__ import annotations

from copy import deepcopy

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_split_merge_rear_path import (
    NO_FRONTEND_CONTRACT_CHANGE,
    build_direct_plus_branched_split_merge_rear_path_model_dict,
)
from os_lem.solve import (
    direct_plus_branched_split_merge_rear_path_front_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_contribution_spl,
    direct_plus_branched_split_merge_rear_path_rear_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_rear_contribution_spl,
    solve_frequency_point,
    solve_frequency_sweep,
    summed_radiator_observation_pressure,
)


CANONICAL_FREQUENCIES_HZ = np.array([50.0, 80.0, 125.0, 200.0, 315.0, 500.0])


def _regression_model_dict() -> dict[str, object]:
    model_dict = deepcopy(build_direct_plus_branched_split_merge_rear_path_model_dict())
    model_dict["observations"] += [
        {"id": "direct_q_b", "type": "element_volume_velocity", "target": "direct_leg", "location": "b"},
        {"id": "exit_q_b", "type": "element_volume_velocity", "target": "shared_exit", "location": "b"},
    ]
    return model_dict


def test_direct_plus_branched_split_merge_rear_path_contribution_regression_path_assembles() -> None:
    model, warnings = normalize_model(_regression_model_dict())

    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)
    assert len(system.recombination_topologies) == 1
    assert len(system.direct_plus_branched_split_merge_rear_path_skeletons) == 1
    assert len(system.direct_plus_branched_split_merge_rear_path_contribution_contracts) == 1

    skeleton = system.direct_plus_branched_split_merge_rear_path_skeletons[0]
    contract = system.direct_plus_branched_split_merge_rear_path_contribution_contracts[0]

    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.direct_branch_element_id == "direct_leg"
    assert skeleton.split_feed_element_id == "split_feed"
    assert skeleton.recombined_leg_element_ids == ("merge_main", "merge_aux")
    assert skeleton.shared_exit_element_id == "shared_exit"
    assert skeleton.direct_rear_mouth_radiator_id == "rear_direct_rad"
    assert skeleton.merged_rear_mouth_radiator_id == "rear_merged_rad"

    assert contract.front_radiator_id == "front_rad"
    assert contract.direct_branch_element_id == "direct_leg"
    assert contract.direct_rear_mouth_radiator_id == "rear_direct_rad"
    assert contract.split_feed_element_id == "split_feed"
    assert contract.recombined_leg_element_ids == ("merge_main", "merge_aux")
    assert contract.shared_exit_element_id == "shared_exit"
    assert contract.merged_rear_mouth_radiator_id == "rear_merged_rad"


def test_direct_plus_branched_split_merge_rear_path_contribution_regression_path_extracts_stable_contributions() -> None:
    model_dict = _regression_model_dict()
    result = run_simulation(model_dict, CANONICAL_FREQUENCIES_HZ)

    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, CANONICAL_FREQUENCIES_HZ)
    contract = system.direct_plus_branched_split_merge_rear_path_contribution_contracts[0]

    front_pressure = direct_plus_branched_split_merge_rear_path_front_contribution_pressure(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    rear_pressure = direct_plus_branched_split_merge_rear_path_rear_contribution_pressure(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    front_spl = direct_plus_branched_split_merge_rear_path_front_contribution_spl(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    rear_spl = direct_plus_branched_split_merge_rear_path_rear_contribution_spl(
        sweep,
        system,
        contract,
        1.0,
        radiation_space="2pi",
    )
    expected_rear_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [
            {"target": "rear_direct_rad", "distance": 1.0},
            {"target": "rear_merged_rad", "distance": 1.0},
        ],
        radiation_space="2pi",
    )
    expected_total_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [
            {"target": "front_rad", "distance": 1.0},
            {"target": "rear_direct_rad", "distance": 1.0},
            {"target": "rear_merged_rad", "distance": 1.0},
        ],
        radiation_space="2pi",
    )

    np.testing.assert_allclose(result.series["spl_front"], front_spl, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["spl_rear_sum"], rear_spl, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(rear_pressure, expected_rear_pressure, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(front_pressure + rear_pressure, expected_total_pressure, rtol=1e-10, atol=1e-12)

    assert result.units["spl_front"] == "dB"
    assert result.units["spl_rear_sum"] == "dB"
    assert np.all(np.isfinite(front_pressure))
    assert np.all(np.isfinite(rear_pressure))
    assert np.all(np.isfinite(result.series["spl_front"]))
    assert np.all(np.isfinite(result.series["spl_rear_sum"]))

    rear_minus_front_db = result.series["spl_rear_sum"] - result.series["spl_front"]
    assert rear_minus_front_db[0] > 1.0
    assert rear_minus_front_db[1] > 4.0
    assert rear_minus_front_db[2] > 15.0
    assert rear_minus_front_db[3] > 1.0
    assert rear_minus_front_db[4] < 0.0
    assert rear_minus_front_db[5] > 5.0

    rear_to_front_mag = np.abs(rear_pressure) / np.maximum(np.abs(front_pressure), 1.0e-30)
    assert rear_to_front_mag[0] > 1.1
    assert rear_to_front_mag[1] > 1.5
    assert rear_to_front_mag[2] > 6.0
    assert rear_to_front_mag[3] > 1.1
    assert rear_to_front_mag[4] < 1.0
    assert rear_to_front_mag[5] > 1.5

    direct_merged_delta_db = result.series["spl_direct"] - result.series["spl_merged"]
    assert direct_merged_delta_db[0] > 5.0
    assert direct_merged_delta_db[1] > 5.0
    assert direct_merged_delta_db[2] > 2.0
    assert direct_merged_delta_db[3] < -10.0
    assert direct_merged_delta_db[4] > 8.0
    assert np.max(direct_merged_delta_db) - np.min(direct_merged_delta_db) > 20.0

    total_minus_front_db = result.series["spl_total"] - result.series["spl_front"]
    assert total_minus_front_db[0] < -10.0
    assert total_minus_front_db[1] < 0.0
    assert total_minus_front_db[2] > 15.0
    assert total_minus_front_db[3] > 5.0
    assert total_minus_front_db[4] > 3.0
    assert total_minus_front_db[5] > 3.0


def test_direct_plus_branched_split_merge_rear_path_contribution_regression_path_preserves_structural_sanity() -> None:
    model_dict = _regression_model_dict()
    result = run_simulation(model_dict, CANONICAL_FREQUENCIES_HZ)
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 160.0)

    stem_to_junction = -point.waveguide_endpoint_flow["stem"].node_b
    direct_from_junction = point.waveguide_endpoint_flow["direct_leg"].node_a
    feed_from_junction = point.waveguide_endpoint_flow["split_feed"].node_a
    feed_to_split = -point.waveguide_endpoint_flow["split_feed"].node_b
    main_from_split = point.waveguide_endpoint_flow["merge_main"].node_a
    aux_from_split = point.waveguide_endpoint_flow["merge_aux"].node_a
    exit_from_merge = -point.waveguide_endpoint_flow["shared_exit"].node_a
    main_into_merge = point.waveguide_endpoint_flow["merge_main"].node_b
    aux_into_merge = point.waveguide_endpoint_flow["merge_aux"].node_b

    np.testing.assert_allclose(stem_to_junction, direct_from_junction + feed_from_junction, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(feed_to_split, main_from_split + aux_from_split, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(exit_from_merge, main_into_merge + aux_into_merge, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["stem_q_b"], result.series["direct_q_a"] + result.series["feed_q_a"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["feed_q_b"], result.series["main_q_a"] + result.series["aux_q_a"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["exit_q_a"], result.series["main_q_b"] + result.series["aux_q_b"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["direct_q_b"], result.series["direct_rad_q"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["exit_q_b"], result.series["merged_rad_q"], rtol=1e-10, atol=1e-12)

    assert np.all(np.isfinite(result.series["p_junction"]))
    assert np.all(np.isfinite(result.series["p_split"]))
    assert np.all(np.isfinite(result.series["p_merge"]))
    assert not np.allclose(result.series["spl_rear_sum"], result.series["spl_direct"])
    assert not np.allclose(result.series["spl_rear_sum"], result.series["spl_merged"])
    assert not np.allclose(result.series["spl_total"], result.series["spl_front"])
    assert not np.allclose(result.series["spl_total"], result.series["spl_rear_sum"])
