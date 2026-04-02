from __future__ import annotations

from copy import deepcopy

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import NO_FRONTEND_CONTRACT_CHANGE, build_back_loaded_horn_model_dict
from os_lem.solve import (
    front_radiation_contribution_pressure,
    front_radiation_contribution_spl,
    front_rear_radiation_sum_pressure,
    rear_radiation_contribution_pressure,
    rear_radiation_contribution_spl,
    solve_frequency_point,
    solve_frequency_sweep,
)


CANONICAL_FREQUENCIES_HZ = np.array([50.0, 80.0, 125.0, 200.0, 315.0, 500.0])


def _regression_model_dict() -> dict[str, object]:
    model_dict = deepcopy(build_back_loaded_horn_model_dict())
    model_dict["observations"] = [
        {"id": "spl_front", "type": "spl", "target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
        {"id": "spl_rear", "type": "spl", "target": "mouth_rad", "distance": "1 m", "radiation_space": "2pi"},
        {
            "id": "spl_front_rear_sum",
            "type": "spl_sum",
            "radiation_space": "2pi",
            "terms": [
                {"target": "front_rad", "distance": "1 m"},
                {"target": "mouth_rad", "distance": "1 m"},
            ],
        },
        {"id": "rear_leg_q_a", "type": "element_volume_velocity", "target": "rear_leg", "location": "a"},
        {"id": "rear_leg_q_b", "type": "element_volume_velocity", "target": "rear_leg", "location": "b"},
        {"id": "blind_up_q_b", "type": "element_volume_velocity", "target": "blind_upstream", "location": "b"},
        {"id": "blind_down_q_a", "type": "element_volume_velocity", "target": "blind_downstream", "location": "a"},
        {"id": "blind_down_q_b", "type": "element_volume_velocity", "target": "blind_downstream", "location": "b"},
    ]
    return model_dict


def test_front_rear_radiation_contribution_regression_path_assembles() -> None:
    model, warnings = normalize_model(_regression_model_dict())

    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)
    assert len(system.back_loaded_horn_skeletons) == 1
    assert len(system.front_rear_radiation_sum_observabilities) == 1
    assert len(system.front_rear_radiation_contribution_observabilities) == 1

    skeleton = system.back_loaded_horn_skeletons[0]
    observability = system.front_rear_radiation_contribution_observabilities[0]

    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.mouth_radiator_id == "mouth_rad"
    assert observability.front_radiator_id == "front_rad"
    assert observability.rear_radiator_id == "mouth_rad"
    assert observability.front_node_name == "front"
    assert observability.rear_mouth_node_name == "mouth"


def test_front_rear_radiation_contribution_regression_path_extracts_stable_contributions() -> None:
    model_dict = _regression_model_dict()
    result = run_simulation(model_dict, CANONICAL_FREQUENCIES_HZ)

    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, CANONICAL_FREQUENCIES_HZ)
    contribution_observability = system.front_rear_radiation_contribution_observabilities[0]
    sum_observability = system.front_rear_radiation_sum_observabilities[0]

    front_pressure = front_radiation_contribution_pressure(
        sweep,
        system,
        contribution_observability,
        1.0,
        radiation_space="2pi",
    )
    rear_pressure = rear_radiation_contribution_pressure(
        sweep,
        system,
        contribution_observability,
        1.0,
        radiation_space="2pi",
    )
    front_spl = front_radiation_contribution_spl(
        sweep,
        system,
        contribution_observability,
        1.0,
        radiation_space="2pi",
    )
    rear_spl = rear_radiation_contribution_spl(
        sweep,
        system,
        contribution_observability,
        1.0,
        radiation_space="2pi",
    )
    recomposed_sum_pressure = front_pressure + rear_pressure
    helper_sum_pressure = front_rear_radiation_sum_pressure(
        sweep,
        system,
        sum_observability,
        1.0,
        radiation_space="2pi",
    )

    np.testing.assert_allclose(result.series["spl_front"], front_spl, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["spl_rear"], rear_spl, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(recomposed_sum_pressure, helper_sum_pressure, rtol=1e-10, atol=1e-12)

    assert result.units["spl_front"] == "dB"
    assert result.units["spl_rear"] == "dB"
    assert np.all(np.isfinite(front_pressure))
    assert np.all(np.isfinite(rear_pressure))
    assert np.all(np.isfinite(result.series["spl_front"]))
    assert np.all(np.isfinite(result.series["spl_rear"]))

    rear_minus_front_db = result.series["spl_rear"] - result.series["spl_front"]
    assert rear_minus_front_db[0] > 2.0
    assert rear_minus_front_db[1] > 1.0
    assert rear_minus_front_db[2] > 4.0
    assert rear_minus_front_db[3] < -15.0
    assert rear_minus_front_db[4] < -25.0
    assert rear_minus_front_db[5] < -30.0

    rear_to_front_mag = np.abs(rear_pressure) / np.maximum(np.abs(front_pressure), 1.0e-30)
    assert rear_to_front_mag[0] > 1.3
    assert rear_to_front_mag[1] > 1.1
    assert rear_to_front_mag[2] > 1.6
    assert rear_to_front_mag[3] < 0.1
    assert rear_to_front_mag[4] < 0.05
    assert rear_to_front_mag[5] < 0.02



def test_front_rear_radiation_contribution_regression_path_preserves_structural_sanity() -> None:
    model_dict = _regression_model_dict()
    result = run_simulation(model_dict, CANONICAL_FREQUENCIES_HZ)
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 160.0)

    rear_port_into_inject = -point.waveguide_endpoint_flow["rear_port"].node_b
    throat_entry_from_inject = point.waveguide_endpoint_flow["throat_entry"].node_a
    blind_up_into_side = -point.waveguide_endpoint_flow["blind_upstream"].node_b
    blind_down_from_side = point.waveguide_endpoint_flow["blind_downstream"].node_a
    blind_closed_end = point.waveguide_endpoint_flow["blind_downstream"].node_b

    np.testing.assert_allclose(rear_port_into_inject, throat_entry_from_inject, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(blind_down_from_side, blind_up_into_side, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["blind_down_q_a"], result.series["blind_up_q_b"], rtol=1e-10, atol=1e-12)
    assert abs(blind_closed_end) < 1.0e-10
    assert np.all(np.abs(result.series["blind_down_q_b"]) < 1.0e-10)
    assert not np.allclose(result.series["spl_front"], result.series["spl_rear"])
    assert not np.allclose(result.series["spl_front_rear_sum"], result.series["spl_front"])
    assert not np.allclose(result.series["spl_front_rear_sum"], result.series["spl_rear"])
