from __future__ import annotations

from copy import deepcopy

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import NO_FRONTEND_CONTRACT_CHANGE, build_back_loaded_horn_model_dict
from os_lem.solve import (
    front_rear_radiation_sum_pressure,
    front_rear_radiation_sum_spl,
    radiator_observation_pressure,
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


def test_back_loaded_horn_radiation_sum_regression_path_assembles() -> None:
    model, warnings = normalize_model(_regression_model_dict())

    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)
    assert len(system.back_loaded_horn_skeletons) == 1
    assert len(system.front_rear_radiation_sum_observabilities) == 1

    skeleton = system.back_loaded_horn_skeletons[0]
    observability = system.front_rear_radiation_sum_observabilities[0]

    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.mouth_radiator_id == "mouth_rad"
    assert skeleton.front_node_name == "front"
    assert skeleton.mouth_node_name == "mouth"
    assert observability.front_radiator_id == "front_rad"
    assert observability.rear_radiator_id == "mouth_rad"
    assert observability.front_node_name == "front"
    assert observability.rear_mouth_node_name == "mouth"


def test_back_loaded_horn_radiation_sum_regression_path_extracts_expected_sum() -> None:
    model_dict = _regression_model_dict()
    result = run_simulation(model_dict, CANONICAL_FREQUENCIES_HZ)

    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, CANONICAL_FREQUENCIES_HZ)
    observability = system.front_rear_radiation_sum_observabilities[0]

    manual_pressure_sum = radiator_observation_pressure(
        sweep,
        system,
        "front_rad",
        1.0,
        radiation_space="2pi",
    ) + radiator_observation_pressure(
        sweep,
        system,
        "mouth_rad",
        1.0,
        radiation_space="2pi",
    )
    helper_pressure_sum = front_rear_radiation_sum_pressure(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
    helper_spl_sum = front_rear_radiation_sum_spl(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )

    np.testing.assert_allclose(helper_pressure_sum, manual_pressure_sum, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["spl_front_rear_sum"], helper_spl_sum, rtol=1e-10, atol=1e-12)
    assert result.units["spl_front_rear_sum"] == "dB"
    assert np.all(np.isfinite(result.series["spl_front_rear_sum"]))
    assert not np.allclose(result.series["spl_front_rear_sum"], result.series["spl_front"])
    assert not np.allclose(result.series["spl_front_rear_sum"], result.series["spl_rear"])


def test_back_loaded_horn_radiation_sum_regression_path_preserves_structural_sanity() -> None:
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
    np.testing.assert_allclose(
        result.series["blind_down_q_a"],
        result.series["blind_up_q_b"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert abs(blind_closed_end) < 1.0e-10
    assert np.all(np.abs(result.series["blind_down_q_b"]) < 1.0e-10)
