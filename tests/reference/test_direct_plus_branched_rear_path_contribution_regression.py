from __future__ import annotations

from copy import deepcopy

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_rear_path import (
    NO_FRONTEND_CONTRACT_CHANGE,
    build_direct_plus_branched_rear_path_model_dict,
)
from os_lem.solve import (
    direct_plus_branched_rear_path_front_contribution_pressure,
    direct_plus_branched_rear_path_front_contribution_spl,
    direct_plus_branched_rear_path_rear_contribution_pressure,
    direct_plus_branched_rear_path_rear_contribution_spl,
    solve_frequency_point,
    solve_frequency_sweep,
    summed_radiator_observation_pressure,
)


CANONICAL_FREQUENCIES_HZ = np.array([50.0, 80.0, 125.0, 200.0, 315.0, 500.0])


def _regression_model_dict() -> dict[str, object]:
    model_dict = deepcopy(build_direct_plus_branched_rear_path_model_dict())
    model_dict["observations"] += [
        {"id": "main_q_b", "type": "element_volume_velocity", "target": "rear_main_leg", "location": "b"},
        {"id": "aux_q_b", "type": "element_volume_velocity", "target": "rear_aux_leg", "location": "b"},
    ]
    return model_dict


def test_direct_plus_branched_rear_path_contribution_regression_path_assembles() -> None:
    model, warnings = normalize_model(_regression_model_dict())

    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)
    assert len(system.branched_horn_skeletons) == 1
    assert len(system.direct_plus_branched_rear_path_skeletons) == 1
    assert len(system.direct_plus_branched_rear_path_contribution_contracts) == 1

    skeleton = system.direct_plus_branched_rear_path_skeletons[0]
    contract = system.direct_plus_branched_rear_path_contribution_contracts[0]

    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.rear_branch_element_ids == ("rear_main_leg", "rear_aux_leg")
    assert skeleton.rear_mouth_radiator_ids == ("rear_main_rad", "rear_aux_rad")
    assert contract.front_radiator_id == "front_rad"
    assert contract.rear_mouth_radiator_ids == ("rear_main_rad", "rear_aux_rad")
    assert contract.rear_branch_element_ids == ("rear_main_leg", "rear_aux_leg")


def test_direct_plus_branched_rear_path_contribution_regression_path_extracts_stable_contributions() -> None:
    model_dict = _regression_model_dict()
    result = run_simulation(model_dict, CANONICAL_FREQUENCIES_HZ)

    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, CANONICAL_FREQUENCIES_HZ)
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
    expected_rear_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [
            {"target": "rear_main_rad", "distance": 1.0},
            {"target": "rear_aux_rad", "distance": 1.0},
        ],
        radiation_space="2pi",
    )
    expected_total_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [
            {"target": "front_rad", "distance": 1.0},
            {"target": "rear_main_rad", "distance": 1.0},
            {"target": "rear_aux_rad", "distance": 1.0},
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
    assert rear_minus_front_db[1] > 3.0
    assert rear_minus_front_db[2] > 10.0
    assert rear_minus_front_db[3] > 4.0
    assert rear_minus_front_db[4] > 10.0
    assert rear_minus_front_db[5] < 0.0

    rear_to_front_mag = np.abs(rear_pressure) / np.maximum(np.abs(front_pressure), 1.0e-30)
    assert rear_to_front_mag[0] > 1.1
    assert rear_to_front_mag[1] > 1.4
    assert rear_to_front_mag[2] > 4.0
    assert rear_to_front_mag[3] > 1.5
    assert rear_to_front_mag[4] > 4.0
    assert rear_to_front_mag[5] < 1.0

    main_aux_delta_db = result.series["spl_main"] - result.series["spl_aux"]
    assert np.all(main_aux_delta_db > 0.0)
    assert main_aux_delta_db[3] > 4.0
    assert main_aux_delta_db[4] > 10.0


def test_direct_plus_branched_rear_path_contribution_regression_path_preserves_structural_sanity() -> None:
    model_dict = _regression_model_dict()
    result = run_simulation(model_dict, CANONICAL_FREQUENCIES_HZ)
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 160.0)

    stem_to_junction = -point.waveguide_endpoint_flow["stem"].node_b
    main_from_junction = point.waveguide_endpoint_flow["rear_main_leg"].node_a
    aux_from_junction = point.waveguide_endpoint_flow["rear_aux_leg"].node_a

    np.testing.assert_allclose(stem_to_junction, main_from_junction + aux_from_junction, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["stem_q_b"], result.series["main_q_a"] + result.series["aux_q_a"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["main_q_b"], result.series["main_rad_q"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["aux_q_b"], result.series["aux_rad_q"], rtol=1e-10, atol=1e-12)

    assert np.all(np.isfinite(result.series["p_junction"]))
    assert not np.allclose(result.series["spl_rear_sum"], result.series["spl_main"])
    assert not np.allclose(result.series["spl_rear_sum"], result.series["spl_aux"])
    assert not np.allclose(result.series["spl_total"], result.series["spl_front"])
    assert not np.allclose(result.series["spl_total"], result.series["spl_rear_sum"])
