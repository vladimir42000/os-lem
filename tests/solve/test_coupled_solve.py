from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.model import (
    Driver,
    DuctElement,
    NormalizedModel,
    RadiatorElement,
    VolumeElement,
)
from os_lem.solve import build_coupled_system, solve_frequency_point


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


def test_build_coupled_system_has_expected_shape() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    built = build_coupled_system(model, system, 100.0)

    assert built.A.shape == (5, 5)
    assert built.b.shape == (5,)
    assert built.acoustic_matrix.shape == (3, 3)
    assert np.iscomplexobj(built.A)
    assert np.iscomplexobj(built.b)


def test_build_coupled_system_places_source_voltage_in_electrical_rhs() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    built = build_coupled_system(model, system, 100.0)

    n = len(system.node_order)
    assert built.b[n] == model.driver.source_voltage_rms
    np.testing.assert_allclose(built.b[:n], 0.0 + 0.0j)
    np.testing.assert_allclose(built.b[n + 1], 0.0 + 0.0j)


def test_solve_frequency_point_returns_finite_complex_outputs() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 100.0)

    assert solved.frequency_hz == 100.0
    assert solved.node_order == ("front", "rear", "port")
    assert solved.pressures.shape == (3,)
    assert solved.solution_vector.shape == (5,)

    assert np.iscomplexobj(solved.pressures)
    assert isinstance(solved.coil_current, complex)
    assert isinstance(solved.cone_velocity, complex)
    assert isinstance(solved.cone_displacement, complex)

    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))
    assert np.isfinite(solved.coil_current.real)
    assert np.isfinite(solved.coil_current.imag)
    assert np.isfinite(solved.cone_velocity.real)
    assert np.isfinite(solved.cone_velocity.imag)
    assert np.isfinite(solved.cone_displacement.real)
    assert np.isfinite(solved.cone_displacement.imag)


def test_solve_frequency_point_displacement_matches_velocity_relation() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 100.0)
    expected = solved.cone_velocity / (1j * solved.omega_rad_s)

    np.testing.assert_allclose(solved.cone_displacement, expected)


def test_coupled_build_rejects_nonpositive_frequency() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    try:
        build_coupled_system(model, system, 0.0)
    except ValueError as exc:
        assert "must be > 0" in str(exc)
    else:
        raise AssertionError("expected ValueError for nonpositive frequency")


def test_coupled_solve_rejects_nonpositive_frequency() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    try:
        solve_frequency_point(model, system, 0.0)
    except ValueError as exc:
        assert "must be > 0" in str(exc)
    else:
        raise AssertionError("expected ValueError for nonpositive frequency")
