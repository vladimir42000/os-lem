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
    Waveguide1DElement,
)
from os_lem.solve import (
    _waveguide_equivalent_admittance_matrix,
    solve_frequency_point,
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



def _minimal_waveguide_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        volumes=[
            VolumeElement(id="rear_vol", node="rear", value_m3=0.02),
        ],
        radiators=[
            RadiatorElement(id="port_rad", node="port", model="flanged_piston", area_m2=0.01),
        ],
        waveguides=[
            Waveguide1DElement(
                id="wg1",
                node_a="front",
                node_b="port",
                length_m=0.40,
                area_start_m2=0.01,
                area_end_m2=0.02,
                profile="conical",
                segments=8,
            )
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


def test_waveguide_endpoint_flow_is_exposed_with_explicit_endpoint_names() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    sweep = solve_frequency_sweep(model, system, [100.0, 200.0])

    assert tuple(point.waveguide_endpoint_flow.keys()) == ("wg1",)
    assert tuple(sweep.waveguide_endpoint_flow.keys()) == ("wg1",)

    point_flow = point.waveguide_endpoint_flow["wg1"]
    sweep_flow = sweep.waveguide_endpoint_flow["wg1"]

    assert isinstance(point_flow.node_a, complex)
    assert isinstance(point_flow.node_b, complex)
    assert sweep_flow.node_a.shape == (2,)
    assert sweep_flow.node_b.shape == (2,)
    assert np.all(np.isfinite(sweep_flow.node_a.real))
    assert np.all(np.isfinite(sweep_flow.node_a.imag))
    assert np.all(np.isfinite(sweep_flow.node_b.real))
    assert np.all(np.isfinite(sweep_flow.node_b.imag))


def test_waveguide_endpoint_flow_first_sweep_point_matches_one_frequency_solver() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    sweep = solve_frequency_sweep(model, system, [100.0, 200.0])

    np.testing.assert_allclose(sweep.waveguide_endpoint_flow["wg1"].node_a[0], point.waveguide_endpoint_flow["wg1"].node_a)
    np.testing.assert_allclose(sweep.waveguide_endpoint_flow["wg1"].node_b[0], point.waveguide_endpoint_flow["wg1"].node_b)


def test_waveguide_endpoint_flow_matches_reduced_two_port_relation() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    waveguide = model.waveguides[0]
    Y_branch = _waveguide_equivalent_admittance_matrix(point.omega_rad_s, waveguide)
    endpoint_pressures = np.array([point.pressures[0], point.pressures[2]], dtype=np.complex128)
    expected_flow = Y_branch @ endpoint_pressures

    np.testing.assert_allclose(point.waveguide_endpoint_flow["wg1"].node_a, expected_flow[0])
    np.testing.assert_allclose(point.waveguide_endpoint_flow["wg1"].node_b, expected_flow[1])
