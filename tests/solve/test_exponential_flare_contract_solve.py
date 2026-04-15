from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.elements.waveguide_1d import area_at_position, segment_midpoint_areas, uniform_segment_admittance
from os_lem.parser import normalize_model
from os_lem.solve import (
    _waveguide_internal_nodal_pressures,
    solve_frequency_point,
    waveguide_line_profile_particle_velocity,
    waveguide_line_profile_pressure,
    waveguide_line_profile_volume_velocity,
)


def _exponential_model_dict() -> dict:
    return {
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "front",
            "node_rear": "rear",
        },
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "infinite_baffle_piston",
                "area": "132 cm2",
            },
            {"id": "rear_vol", "type": "volume", "node": "rear", "value": "18 l"},
            {
                "id": "wg1",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "mouth",
                "length": "40 cm",
                "area_start": "10 cm2",
                "area_end": "50 cm2",
                "profile": "exponential",
                "segments": 12,
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "unflanged_piston",
                "area": "50 cm2",
            },
        ],
        "observations": [{"id": "zin", "type": "input_impedance", "target": "drv1"}],
    }


def test_exponential_waveguide_path_remains_finite_and_endpoint_profile_consistent() -> None:
    model, _ = normalize_model(_exponential_model_dict())
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 120.0)

    pressure = waveguide_line_profile_pressure(point, system, "wg1", points=19)
    flow = waveguide_line_profile_volume_velocity(point, system, "wg1", points=19)
    particle = waveguide_line_profile_particle_velocity(point, system, "wg1", points=19)

    assert np.all(np.isfinite(pressure.values.real))
    assert np.all(np.isfinite(pressure.values.imag))
    assert np.all(np.isfinite(flow.values.real))
    assert np.all(np.isfinite(flow.values.imag))
    assert np.all(np.isfinite(particle.values.real))
    assert np.all(np.isfinite(particle.values.imag))

    idx = {name: i for i, name in enumerate(system.node_order)}
    np.testing.assert_allclose(pressure.values[0], point.pressures[idx["rear"]])
    np.testing.assert_allclose(pressure.values[-1], point.pressures[idx["mouth"]])
    np.testing.assert_allclose(flow.values[0], point.waveguide_endpoint_flow["wg1"].node_a)
    np.testing.assert_allclose(flow.values[-1], -point.waveguide_endpoint_flow["wg1"].node_b)
    np.testing.assert_allclose(particle.values[0], point.waveguide_endpoint_velocity["wg1"].node_a)
    np.testing.assert_allclose(particle.values[-1], -point.waveguide_endpoint_velocity["wg1"].node_b)

    areas = np.array(
        [
            area_at_position(
                model.waveguides[0].length_m,
                model.waveguides[0].area_start_m2,
                model.waveguides[0].area_end_m2,
                float(x_m),
                profile="exponential",
            )
            for x_m in particle.x_m
        ],
        dtype=float,
    )
    np.testing.assert_allclose(particle.values, flow.values / areas)


def test_exponential_internal_segment_boundary_flows_match_discrete_segment_semantics() -> None:
    model, _ = normalize_model(_exponential_model_dict())
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 120.0)
    waveguide = model.waveguides[0]

    profile = waveguide_line_profile_volume_velocity(point, system, "wg1", points=waveguide.segments + 1)
    idx = {name: i for i, name in enumerate(system.node_order)}
    nodal_pressures = _waveguide_internal_nodal_pressures(
        point.omega_rad_s,
        waveguide,
        point.pressures[idx["rear"]],
        point.pressures[idx["mouth"]],
    )

    expected_internal = np.empty(waveguide.segments - 1, dtype=np.complex128)
    dx = waveguide.length_m / waveguide.segments
    areas = segment_midpoint_areas(
        waveguide.length_m,
        waveguide.area_start_m2,
        waveguide.area_end_m2,
        waveguide.segments,
        profile="exponential",
    )
    for seg_idx, area_m2 in enumerate(areas[:-1]):
        Y_seg = uniform_segment_admittance(point.omega_rad_s, dx, float(area_m2))
        q_seg = Y_seg @ np.array([nodal_pressures[seg_idx], nodal_pressures[seg_idx + 1]], dtype=np.complex128)
        expected_internal[seg_idx] = -q_seg[1]

    np.testing.assert_allclose(profile.values[0], point.waveguide_endpoint_flow["wg1"].node_a)
    np.testing.assert_allclose(profile.values[-1], -point.waveguide_endpoint_flow["wg1"].node_b)
    np.testing.assert_allclose(profile.values[1:-1], expected_internal)
