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
    _waveguide_internal_nodal_pressures,
    solve_frequency_point,
    solve_frequency_sweep,
    waveguide_line_profile_particle_velocity,
    waveguide_line_profile_pressure,
    waveguide_line_profile_volume_velocity,
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


def test_waveguide_endpoint_velocity_is_exposed_with_explicit_endpoint_names() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    sweep = solve_frequency_sweep(model, system, [100.0, 200.0])

    assert tuple(point.waveguide_endpoint_velocity.keys()) == ("wg1",)
    assert tuple(sweep.waveguide_endpoint_velocity.keys()) == ("wg1",)

    point_velocity = point.waveguide_endpoint_velocity["wg1"]
    sweep_velocity = sweep.waveguide_endpoint_velocity["wg1"]

    assert isinstance(point_velocity.node_a, complex)
    assert isinstance(point_velocity.node_b, complex)
    assert sweep_velocity.node_a.shape == (2,)
    assert sweep_velocity.node_b.shape == (2,)
    assert np.all(np.isfinite(sweep_velocity.node_a.real))
    assert np.all(np.isfinite(sweep_velocity.node_a.imag))
    assert np.all(np.isfinite(sweep_velocity.node_b.real))
    assert np.all(np.isfinite(sweep_velocity.node_b.imag))


def test_waveguide_endpoint_velocity_first_sweep_point_matches_one_frequency_solver() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    sweep = solve_frequency_sweep(model, system, [100.0, 200.0])

    np.testing.assert_allclose(sweep.waveguide_endpoint_velocity["wg1"].node_a[0], point.waveguide_endpoint_velocity["wg1"].node_a)
    np.testing.assert_allclose(sweep.waveguide_endpoint_velocity["wg1"].node_b[0], point.waveguide_endpoint_velocity["wg1"].node_b)


def test_waveguide_endpoint_velocity_matches_flow_over_local_area() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    waveguide = model.waveguides[0]

    np.testing.assert_allclose(
        point.waveguide_endpoint_velocity["wg1"].node_a,
        point.waveguide_endpoint_flow["wg1"].node_a / waveguide.area_start_m2,
    )
    np.testing.assert_allclose(
        point.waveguide_endpoint_velocity["wg1"].node_b,
        point.waveguide_endpoint_flow["wg1"].node_b / waveguide.area_end_m2,
    )




def _minimal_waveguide_cylindrical_model() -> NormalizedModel:
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
                area_start_m2=0.0125,
                area_end_m2=0.0125,
                profile="conical",
                segments=8,
            )
        ],
        node_order=["front", "rear", "port"],
    )

def _minimal_waveguide_model_reversed() -> NormalizedModel:
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
                node_a="port",
                node_b="front",
                length_m=0.40,
                area_start_m2=0.02,
                area_end_m2=0.01,
                profile="conical",
                segments=8,
            )
        ],
        node_order=["front", "rear", "port"],
    )


def test_waveguide_line_profile_pressure_exposes_requested_axis_and_complex_values() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    profile = waveguide_line_profile_pressure(point, system, "wg1", points=17)

    assert profile.quantity == "pressure"
    assert profile.x_m.shape == (17,)
    assert profile.values.shape == (17,)
    np.testing.assert_allclose(profile.x_m[0], 0.0)
    np.testing.assert_allclose(profile.x_m[-1], model.waveguides[0].length_m)
    assert np.all(np.diff(profile.x_m) > 0.0)
    assert np.all(np.isfinite(profile.values.real))
    assert np.all(np.isfinite(profile.values.imag))


def test_waveguide_line_profile_pressure_endpoints_match_solved_endpoint_pressures() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    profile = waveguide_line_profile_pressure(point, system, "wg1", points=21)

    np.testing.assert_allclose(profile.values[0], point.pressures[0])
    np.testing.assert_allclose(profile.values[-1], point.pressures[2])


def test_waveguide_line_profile_pressure_matches_segmented_nodal_pressures_at_boundaries() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    waveguide = model.waveguides[0]
    profile = waveguide_line_profile_pressure(point, system, "wg1", points=waveguide.segments + 1)
    nodal_pressures = _waveguide_internal_nodal_pressures(
        point.omega_rad_s,
        waveguide,
        point.pressures[0],
        point.pressures[2],
    )

    np.testing.assert_allclose(profile.values, nodal_pressures)


def test_waveguide_line_profile_pressure_reversal_reverses_x_convention_consistently() -> None:
    model_forward = _minimal_waveguide_model()
    system_forward = assemble_system(model_forward)
    point_forward = solve_frequency_point(model_forward, system_forward, 100.0)
    profile_forward = waveguide_line_profile_pressure(point_forward, system_forward, "wg1", points=17)

    model_reverse = _minimal_waveguide_model_reversed()
    system_reverse = assemble_system(model_reverse)
    point_reverse = solve_frequency_point(model_reverse, system_reverse, 100.0)
    profile_reverse = waveguide_line_profile_pressure(point_reverse, system_reverse, "wg1", points=17)

    np.testing.assert_allclose(profile_reverse.x_m, model_reverse.waveguides[0].length_m - profile_forward.x_m[::-1])
    np.testing.assert_allclose(profile_reverse.values, profile_forward.values[::-1])


def test_waveguide_line_profile_pressure_rejects_too_few_points() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 100.0)

    with pytest.raises(ValueError, match="points must be >= 2"):
        waveguide_line_profile_pressure(point, system, "wg1", points=1)


def test_waveguide_line_profile_volume_velocity_exposes_requested_axis_and_complex_values() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=17)

    assert profile.quantity == "volume_velocity"
    assert profile.x_m.shape == (17,)
    assert profile.values.shape == (17,)
    np.testing.assert_allclose(profile.x_m[0], 0.0)
    np.testing.assert_allclose(profile.x_m[-1], model.waveguides[0].length_m)
    assert np.all(np.diff(profile.x_m) > 0.0)
    assert np.all(np.isfinite(profile.values.real))
    assert np.all(np.isfinite(profile.values.imag))


def test_waveguide_line_profile_volume_velocity_endpoints_match_oriented_endpoint_flows() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=21)

    np.testing.assert_allclose(profile.values[0], point.waveguide_endpoint_flow["wg1"].node_a)
    np.testing.assert_allclose(profile.values[-1], -point.waveguide_endpoint_flow["wg1"].node_b)


def test_waveguide_line_profile_volume_velocity_matches_segment_boundary_oriented_flows() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    waveguide = model.waveguides[0]
    profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=waveguide.segments + 1)
    nodal_pressures = _waveguide_internal_nodal_pressures(
        point.omega_rad_s,
        waveguide,
        point.pressures[0],
        point.pressures[2],
    )

    expected = np.empty(waveguide.segments + 1, dtype=np.complex128)
    dx = waveguide.length_m / waveguide.segments
    for seg_idx in range(waveguide.segments):
        area_m2 = waveguide.area_start_m2 + 0.0
    from os_lem.elements.waveguide_1d import segment_midpoint_areas, uniform_segment_admittance
    areas = segment_midpoint_areas(
        waveguide.length_m,
        waveguide.area_start_m2,
        waveguide.area_end_m2,
        waveguide.segments,
    )
    for seg_idx, area_m2 in enumerate(areas):
        Y_seg = uniform_segment_admittance(point.omega_rad_s, dx, float(area_m2))
        q_seg = Y_seg @ np.array([nodal_pressures[seg_idx], nodal_pressures[seg_idx + 1]], dtype=np.complex128)
        expected[seg_idx] = q_seg[0]
        expected[seg_idx + 1] = -q_seg[1]

    np.testing.assert_allclose(profile.values, expected)


def test_waveguide_line_profile_volume_velocity_reversal_reverses_axis_and_flow_sign() -> None:
    model_forward = _minimal_waveguide_model()
    system_forward = assemble_system(model_forward)
    point_forward = solve_frequency_point(model_forward, system_forward, 100.0)
    profile_forward = waveguide_line_profile_volume_velocity(point_forward, system_forward, "wg1", points=17)

    model_reverse = _minimal_waveguide_model_reversed()
    system_reverse = assemble_system(model_reverse)
    point_reverse = solve_frequency_point(model_reverse, system_reverse, 100.0)
    profile_reverse = waveguide_line_profile_volume_velocity(point_reverse, system_reverse, "wg1", points=17)

    np.testing.assert_allclose(profile_reverse.x_m, model_reverse.waveguides[0].length_m - profile_forward.x_m[::-1])
    np.testing.assert_allclose(profile_reverse.values, -profile_forward.values[::-1])


def test_waveguide_line_profile_volume_velocity_rejects_too_few_points() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 100.0)

    with pytest.raises(ValueError, match="points must be >= 2"):
        waveguide_line_profile_volume_velocity(point, system, "wg1", points=1)


def test_waveguide_line_profile_particle_velocity_exposes_requested_axis_and_complex_values() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    profile = waveguide_line_profile_particle_velocity(point, system, "wg1", points=17)

    assert profile.quantity == "particle_velocity"
    assert profile.x_m.shape == (17,)
    assert profile.values.shape == (17,)
    np.testing.assert_allclose(profile.x_m[0], 0.0)
    np.testing.assert_allclose(profile.x_m[-1], model.waveguides[0].length_m)
    assert np.all(np.diff(profile.x_m) > 0.0)
    assert np.all(np.isfinite(profile.values.real))
    assert np.all(np.isfinite(profile.values.imag))


def test_waveguide_line_profile_particle_velocity_endpoints_match_endpoint_velocity_convention() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    profile = waveguide_line_profile_particle_velocity(point, system, "wg1", points=21)

    np.testing.assert_allclose(profile.values[0], point.waveguide_endpoint_velocity["wg1"].node_a)
    np.testing.assert_allclose(profile.values[-1], -point.waveguide_endpoint_velocity["wg1"].node_b)


def test_waveguide_line_profile_particle_velocity_matches_volume_velocity_over_local_area() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    particle_profile = waveguide_line_profile_particle_velocity(point, system, "wg1", points=17)
    flow_profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=17)

    from os_lem.elements.waveguide_1d import area_at_position

    waveguide = model.waveguides[0]
    area = np.array(
        [
            area_at_position(
                waveguide.length_m,
                waveguide.area_start_m2,
                waveguide.area_end_m2,
                float(x_m),
            )
            for x_m in particle_profile.x_m
        ],
        dtype=float,
    )

    np.testing.assert_allclose(particle_profile.values, flow_profile.values / area)


def test_waveguide_line_profile_particle_velocity_reversal_reverses_axis_and_sign() -> None:
    model_forward = _minimal_waveguide_model()
    system_forward = assemble_system(model_forward)
    point_forward = solve_frequency_point(model_forward, system_forward, 100.0)
    profile_forward = waveguide_line_profile_particle_velocity(point_forward, system_forward, "wg1", points=17)

    model_reverse = _minimal_waveguide_model_reversed()
    system_reverse = assemble_system(model_reverse)
    point_reverse = solve_frequency_point(model_reverse, system_reverse, 100.0)
    profile_reverse = waveguide_line_profile_particle_velocity(point_reverse, system_reverse, "wg1", points=17)

    np.testing.assert_allclose(profile_reverse.x_m, model_reverse.waveguides[0].length_m - profile_forward.x_m[::-1])
    np.testing.assert_allclose(profile_reverse.values, -profile_forward.values[::-1])


def test_waveguide_line_profile_particle_velocity_rejects_too_few_points() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 100.0)

    with pytest.raises(ValueError, match="points must be >= 2"):
        waveguide_line_profile_particle_velocity(point, system, "wg1", points=1)


def test_waveguide_line_profiles_share_common_axis_and_cross_profile_identity() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    pressure_profile = waveguide_line_profile_pressure(point, system, "wg1", points=19)
    flow_profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=19)
    particle_profile = waveguide_line_profile_particle_velocity(point, system, "wg1", points=19)

    np.testing.assert_allclose(pressure_profile.x_m, flow_profile.x_m)
    np.testing.assert_allclose(pressure_profile.x_m, particle_profile.x_m)

    from os_lem.elements.waveguide_1d import area_at_position

    waveguide = model.waveguides[0]
    area = np.array(
        [
            area_at_position(
                waveguide.length_m,
                waveguide.area_start_m2,
                waveguide.area_end_m2,
                float(x_m),
            )
            for x_m in particle_profile.x_m
        ],
        dtype=float,
    )

    np.testing.assert_allclose(particle_profile.values, flow_profile.values / area)


def test_waveguide_line_profiles_jointly_match_existing_endpoint_exports() -> None:
    model = _minimal_waveguide_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    pressure_profile = waveguide_line_profile_pressure(point, system, "wg1", points=23)
    flow_profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=23)
    particle_profile = waveguide_line_profile_particle_velocity(point, system, "wg1", points=23)

    np.testing.assert_allclose(pressure_profile.values[0], point.pressures[0])
    np.testing.assert_allclose(pressure_profile.values[-1], point.pressures[2])
    np.testing.assert_allclose(flow_profile.values[0], point.waveguide_endpoint_flow["wg1"].node_a)
    np.testing.assert_allclose(flow_profile.values[-1], -point.waveguide_endpoint_flow["wg1"].node_b)
    np.testing.assert_allclose(particle_profile.values[0], point.waveguide_endpoint_velocity["wg1"].node_a)
    np.testing.assert_allclose(particle_profile.values[-1], -point.waveguide_endpoint_velocity["wg1"].node_b)


def test_waveguide_line_profiles_cylindrical_case_uses_constant_area_identity_everywhere() -> None:
    model = _minimal_waveguide_cylindrical_model()
    system = assemble_system(model)

    point = solve_frequency_point(model, system, 100.0)
    flow_profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=29)
    particle_profile = waveguide_line_profile_particle_velocity(point, system, "wg1", points=29)

    area_const = model.waveguides[0].area_start_m2
    np.testing.assert_allclose(flow_profile.x_m, particle_profile.x_m)
    np.testing.assert_allclose(particle_profile.values, flow_profile.values / area_const)


def test_waveguide_line_profiles_reversal_semantics_remain_jointly_consistent() -> None:
    model_forward = _minimal_waveguide_model()
    system_forward = assemble_system(model_forward)
    point_forward = solve_frequency_point(model_forward, system_forward, 100.0)
    pressure_forward = waveguide_line_profile_pressure(point_forward, system_forward, "wg1", points=19)
    flow_forward = waveguide_line_profile_volume_velocity(point_forward, system_forward, "wg1", points=19)
    particle_forward = waveguide_line_profile_particle_velocity(point_forward, system_forward, "wg1", points=19)

    model_reverse = _minimal_waveguide_model_reversed()
    system_reverse = assemble_system(model_reverse)
    point_reverse = solve_frequency_point(model_reverse, system_reverse, 100.0)
    pressure_reverse = waveguide_line_profile_pressure(point_reverse, system_reverse, "wg1", points=19)
    flow_reverse = waveguide_line_profile_volume_velocity(point_reverse, system_reverse, "wg1", points=19)
    particle_reverse = waveguide_line_profile_particle_velocity(point_reverse, system_reverse, "wg1", points=19)

    reversed_x = model_reverse.waveguides[0].length_m - pressure_forward.x_m[::-1]
    np.testing.assert_allclose(pressure_reverse.x_m, reversed_x)
    np.testing.assert_allclose(flow_reverse.x_m, reversed_x)
    np.testing.assert_allclose(particle_reverse.x_m, reversed_x)
    np.testing.assert_allclose(pressure_reverse.values, pressure_forward.values[::-1])
    np.testing.assert_allclose(flow_reverse.values, -flow_forward.values[::-1])
    np.testing.assert_allclose(particle_reverse.values, -particle_forward.values[::-1])
