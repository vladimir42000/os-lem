from __future__ import annotations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import NO_FRONTEND_CONTRACT_CHANGE, build_back_loaded_horn_model_dict
from os_lem.solve import (
    radiator_observation_pressure,
    rear_radiation_path_group_delay,
    rear_radiation_path_phase_deg,
    rear_radiation_path_pressure_transfer,
    solve_frequency_point,
    solve_frequency_sweep,
)


CANONICAL_FREQUENCIES_HZ = np.array([50.0, 80.0, 125.0, 200.0, 315.0, 500.0])


def test_direct_rear_path_regression_path_assembles() -> None:
    model, warnings = normalize_model(build_back_loaded_horn_model_dict())

    assert warnings == []
    assert NO_FRONTEND_CONTRACT_CHANGE is True

    system = assemble_system(model)
    assert len(system.back_loaded_horn_skeletons) == 1
    assert len(system.rear_radiation_delay_path_observabilities) == 1

    skeleton = system.back_loaded_horn_skeletons[0]
    observability = system.rear_radiation_delay_path_observabilities[0]

    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.rear_path_element_id == "rear_leg"
    assert skeleton.mouth_radiator_id == "mouth_rad"
    assert observability.front_node_name == "front"
    assert observability.front_radiator_id == "front_rad"
    assert observability.rear_path_element_id == "rear_leg"
    assert observability.rear_path_element_kind == "waveguide_1d"
    assert observability.rear_mouth_node_name == "mouth"
    assert observability.rear_radiator_id == "mouth_rad"


def test_direct_rear_path_regression_path_extracts_stable_transfer_phase_and_delay() -> None:
    model, warnings = normalize_model(build_back_loaded_horn_model_dict())
    assert warnings == []

    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, CANONICAL_FREQUENCIES_HZ)
    observability = system.rear_radiation_delay_path_observabilities[0]

    p_front = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space="2pi")
    p_rear = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")
    manual_transfer = np.zeros(CANONICAL_FREQUENCIES_HZ.size, dtype=np.complex128)
    np.divide(p_rear, p_front, out=manual_transfer, where=np.abs(p_front) > 1.0e-30)

    transfer = rear_radiation_path_pressure_transfer(
        sweep,
        system,
        observability,
        1.0,
        radiation_space="2pi",
    )
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

    np.testing.assert_allclose(transfer, manual_transfer, rtol=1e-10, atol=1e-12)
    assert transfer.shape == (CANONICAL_FREQUENCIES_HZ.size,)
    assert phase_deg.shape == (CANONICAL_FREQUENCIES_HZ.size,)
    assert group_delay_s.shape == (CANONICAL_FREQUENCIES_HZ.size,)
    assert np.all(np.isfinite(transfer))
    assert np.all(np.isfinite(phase_deg))
    assert np.all(np.isfinite(group_delay_s))

    transfer_mag = np.abs(transfer)
    assert transfer_mag[0] > 1.0
    assert transfer_mag[1] > 1.0
    assert transfer_mag[2] > 1.2
    assert transfer_mag[3] < 0.2
    assert transfer_mag[4] < 0.1
    assert transfer_mag[5] < 0.05

    assert -20.0 < phase_deg[0] < 10.0
    assert -220.0 < phase_deg[1] < -130.0
    assert -90.0 < phase_deg[2] < -10.0
    assert 0.0 < phase_deg[3] < 60.0
    assert 40.0 < phase_deg[4] < 120.0
    assert -90.0 < phase_deg[5] < -20.0

    assert 0.010 < group_delay_s[0] < 0.020
    assert 0.003 < group_delay_s[1] < 0.010
    assert -0.010 < group_delay_s[2] < -0.002
    assert -0.005 < group_delay_s[3] < 0.0005
    assert -0.001 < group_delay_s[4] < 0.001
    assert 0.001 < group_delay_s[5] < 0.004


def test_direct_rear_path_regression_path_preserves_branch_balance_and_closed_end_sanity() -> None:
    result = run_simulation(build_back_loaded_horn_model_dict(), CANONICAL_FREQUENCIES_HZ)
    model, warnings = normalize_model(build_back_loaded_horn_model_dict())
    assert warnings == []
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 160.0)

    rear_port_into_inject = -point.waveguide_endpoint_flow["rear_port"].node_b
    throat_entry_from_inject = point.waveguide_endpoint_flow["throat_entry"].node_a
    blind_up_into_side = -point.waveguide_endpoint_flow["blind_upstream"].node_b
    blind_down_from_side = point.waveguide_endpoint_flow["blind_downstream"].node_a
    blind_closed_end = point.waveguide_endpoint_flow["blind_downstream"].node_b

    assert result.units["p_front"] == "Pa"
    assert result.units["mouth_q"] == "m^3/s"
    assert np.all(np.isfinite(result.series["p_front"]))
    assert np.all(np.isfinite(result.series["p_mouth"]))
    assert np.all(np.isfinite(result.series["rear_leg_q_a"]))
    assert np.all(np.isfinite(result.series["rear_leg_q_b"]))
    np.testing.assert_allclose(rear_port_into_inject, throat_entry_from_inject, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(blind_down_from_side, blind_up_into_side, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.series["blind_down_q_a"], result.series["blind_up_q_b"], rtol=1e-10, atol=1e-12)
    assert abs(blind_closed_end) < 1.0e-10
    assert np.all(np.abs(result.series["blind_down_q_b"]) < 1.0e-10)
    assert not np.allclose(result.series["p_front"], result.series["p_mouth"])
