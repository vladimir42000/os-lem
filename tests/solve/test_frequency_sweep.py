from __future__ import annotations

import numpy as np
import pytest

from os_lem.assemble import assemble_system
from os_lem.model import (
    Driver,
    DuctElement,
    NormalizedModel,
    RadiatorElement,
    VolumeElement,
)
from os_lem.solve import solve_frequency_point, solve_frequency_sweep


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


def test_solve_frequency_sweep_returns_expected_shapes_and_finite_outputs() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [20.0, 50.0, 100.0])

    assert sweep.frequency_hz.shape == (3,)
    assert sweep.omega_rad_s.shape == (3,)
    assert sweep.node_order == ("front", "rear", "port")
    assert sweep.pressures.shape == (3, 3)
    assert sweep.coil_current.shape == (3,)
    assert sweep.cone_velocity.shape == (3,)
    assert sweep.cone_displacement.shape == (3,)

    assert np.all(np.isfinite(sweep.pressures.real))
    assert np.all(np.isfinite(sweep.pressures.imag))
    assert np.all(np.isfinite(sweep.coil_current.real))
    assert np.all(np.isfinite(sweep.coil_current.imag))
    assert np.all(np.isfinite(sweep.cone_velocity.real))
    assert np.all(np.isfinite(sweep.cone_velocity.imag))
    assert np.all(np.isfinite(sweep.cone_displacement.real))
    assert np.all(np.isfinite(sweep.cone_displacement.imag))


def test_sweep_first_point_matches_one_frequency_solver() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    sweep = solve_frequency_sweep(model, system, [100.0, 200.0])

    np.testing.assert_allclose(sweep.pressures[0], point.pressures)
    np.testing.assert_allclose(sweep.coil_current[0], point.coil_current)
    np.testing.assert_allclose(sweep.cone_velocity[0], point.cone_velocity)
    np.testing.assert_allclose(sweep.cone_displacement[0], point.cone_displacement)


def test_sweep_input_impedance_matches_voltage_over_current() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [40.0, 100.0, 200.0])
    expected = model.driver.source_voltage_rms / sweep.coil_current

    np.testing.assert_allclose(sweep.input_impedance, expected)


@pytest.mark.parametrize(
    "frequencies, message",
    [
        ([], "must not be empty"),
        ([[100.0, 200.0]], "must be a 1D sequence"),
        ([0.0, 100.0], "must be > 0"),
    ],
)
def test_solve_frequency_sweep_rejects_invalid_frequency_input(frequencies, message: str) -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    with pytest.raises(ValueError, match=message):
        solve_frequency_sweep(model, system, frequencies)
