from __future__ import annotations

import numpy as np
import pytest

from os_lem.assemble import assemble_system
from os_lem.constants import P_REF, RHO0
from os_lem.elements.radiator import on_axis_circular_piston_directivity, radiator_impedance
from os_lem.model import (
    Driver,
    DuctElement,
    NormalizedModel,
    RadiatorElement,
    VolumeElement,
    Waveguide1DElement,
)
from os_lem.solve import (
    radiator_observation_pressure,
    radiator_spl,
    solve_frequency_sweep,
)


def _driver() -> Driver:
    return Driver(
        id="drv1",
        Re=6.0,
        Le=0.0,
        Bl=7.0,
        Mms=0.02,
        Cms=1.0e-3,
        Rms=1.0,
        Sd=0.013,
        node_front="front",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def _minimal_vented_like_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        volumes=[
            VolumeElement(id="rear_vol", node="rear", value_m3=0.02),
        ],
        ducts=[
            DuctElement(id="port_duct", node_a="front", node_b="port", length_m=0.10, area_m2=0.01),
        ],
        radiators=[
            RadiatorElement(id="port_rad", node="port", model="flanged_piston", area_m2=0.01),
        ],
        node_order=["front", "rear", "port"],
    )


def test_radiator_observation_pressure_matches_frozen_transfer_relation() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [100.0])
    p_obs = radiator_observation_pressure(sweep, system, "port_rad", 1.0)

    node_pressure = sweep.pressures[0, 2]
    omega = sweep.omega_rad_s[0]
    z_rad = radiator_impedance("flanged_piston", omega, 0.01)
    q_rad = node_pressure / z_rad
    h_q = 1j * omega * RHO0 / (2.0 * np.pi * 1.0)

    np.testing.assert_allclose(p_obs[0], h_q * q_rad)


def test_radiator_spl_is_db_conversion_of_observation_pressure() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [50.0, 100.0, 200.0])
    p_obs = radiator_observation_pressure(sweep, system, "port_rad", 1.0)
    spl = radiator_spl(sweep, system, "port_rad", 1.0)

    expected = 20.0 * np.log10(np.abs(p_obs) / P_REF)
    np.testing.assert_allclose(spl, expected)
    assert np.all(np.isfinite(spl))


def test_radiator_helpers_reject_unknown_radiator_id() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, [100.0])

    with pytest.raises(ValueError, match="unknown radiator id"):
        radiator_observation_pressure(sweep, system, "missing", 1.0)


def test_radiator_helpers_reject_nonpositive_distance() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, [100.0])

    with pytest.raises(ValueError, match="distance_m must be > 0"):
        radiator_observation_pressure(sweep, system, "port_rad", 0.0)


def test_radiator_observation_helpers_accept_explicit_radiation_space_override() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [100.0])
    p_half = radiator_observation_pressure(sweep, system, "port_rad", 1.0, radiation_space="2pi")
    p_full = radiator_observation_pressure(sweep, system, "port_rad", 1.0, radiation_space="4pi")

    np.testing.assert_allclose(p_half, 2.0 * p_full)


def test_explicit_same_radiation_space_removes_default_mixed_space_notch_direction() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="rear_vol", node="rear", value_m3=0.035)],
        ducts=[DuctElement(id="port_duct", node_a="rear", node_b="port", length_m=0.20, area_m2=0.0019634954084936208)],
        radiators=[
            RadiatorElement(id="front_rad", node="front", model="infinite_baffle_piston", area_m2=0.0132),
            RadiatorElement(id="port_rad", node="port", model="unflanged_piston", area_m2=0.0019634954084936208),
        ],
        node_order=["front", "rear", "port"],
        metadata={"name": "vented_box_demo"},
    )
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, [20.0])

    p_driver_default = radiator_observation_pressure(sweep, system, "front_rad", 1.0)
    p_port_default = radiator_observation_pressure(sweep, system, "port_rad", 1.0)
    p_driver_same = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space="2pi")
    p_port_same = radiator_observation_pressure(sweep, system, "port_rad", 1.0, radiation_space="2pi")

    mixed_mag = np.abs(p_driver_default + p_port_default)[0]
    same_mag = np.abs(p_driver_same + p_port_same)[0]

    assert same_mag > mixed_mag


def test_mouth_directivity_only_contract_multiplies_raw_passive_radiator_pressure() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [30.0, 100.0, 500.0])
    p_raw = radiator_observation_pressure(sweep, system, "port_rad", 1.0, radiation_space="2pi")
    p_candidate = radiator_observation_pressure(
        sweep,
        system,
        "port_rad",
        1.0,
        radiation_space="2pi",
        observable_contract="mouth_directivity_only",
    )
    directivity = np.array(
        [on_axis_circular_piston_directivity(float(omega), 0.01) for omega in sweep.omega_rad_s],
        dtype=np.complex128,
    )

    np.testing.assert_allclose(p_candidate, p_raw * directivity)


def test_default_radiator_observation_pressure_remains_raw_without_contract() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [100.0])
    p_default = radiator_observation_pressure(sweep, system, "port_rad", 1.0, radiation_space="2pi")
    p_raw = radiator_observation_pressure(
        sweep,
        system,
        "port_rad",
        1.0,
        radiation_space="2pi",
        observable_contract="raw",
    )

    np.testing.assert_allclose(p_default, p_raw)


def test_mouth_directivity_only_contract_requires_matching_connected_aperture_area() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="rear_vol", node="rear", value_m3=0.020)],
        ducts=[DuctElement(id="port_duct", node_a="rear", node_b="port", length_m=0.12, area_m2=0.008)],
        radiators=[RadiatorElement(id="port_rad", node="port", model="flanged_piston", area_m2=0.01)],
        node_order=["front", "rear", "port"],
    )
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, [100.0])

    with pytest.raises(ValueError, match="connected aperture area"):
        radiator_observation_pressure(
            sweep,
            system,
            "port_rad",
            1.0,
            radiation_space="2pi",
            observable_contract="mouth_directivity_only",
        )


def test_mouth_directivity_only_contract_supports_waveguide_terminus_with_matching_area() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="rear_vol", node="rear", value_m3=0.030)],
        waveguides=[
            Waveguide1DElement(
                id="line",
                node_a="rear",
                node_b="mouth",
                length_m=0.50,
                area_start_m2=0.01,
                area_end_m2=0.01,
                profile="conical",
                segments=4,
            )
        ],
        radiators=[RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.01)],
        node_order=["front", "rear", "mouth"],
    )
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, [80.0, 200.0])

    p_raw = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")
    p_candidate = radiator_observation_pressure(
        sweep,
        system,
        "mouth_rad",
        1.0,
        radiation_space="2pi",
        observable_contract="mouth_directivity_only",
    )
    directivity = np.array(
        [on_axis_circular_piston_directivity(float(omega), 0.01) for omega in sweep.omega_rad_s],
        dtype=np.complex128,
    )

    np.testing.assert_allclose(p_candidate, p_raw * directivity)


def test_mouth_directivity_only_contract_rejects_driver_front_radiator() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="rear_vol", node="rear", value_m3=0.018)],
        radiators=[RadiatorElement(id="front_rad", node="front", model="infinite_baffle_piston", area_m2=0.0132)],
        node_order=["front", "rear"],
    )
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, [100.0])

    with pytest.raises(ValueError, match="passive mouth/port radiators"):
        radiator_observation_pressure(
            sweep,
            system,
            "front_rad",
            1.0,
            radiation_space="2pi",
            observable_contract="mouth_directivity_only",
        )
