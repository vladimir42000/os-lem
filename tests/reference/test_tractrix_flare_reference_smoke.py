from __future__ import annotations

import numpy as np

from os_lem.reference_tractrix_flare_smoke import (
    _relative_l2_change,
    _relative_scalar_change,
    build_tractrix_model_with_segments,
    downsample_boundary_profile,
    evaluate_tractrix_reference_smoke,
)


def test_tractrix_reference_smoke_remains_finite_endpoint_consistent_and_refinement_bounded() -> None:
    report = evaluate_tractrix_reference_smoke(
        build_tractrix_model_with_segments,
        refinement_levels=(6, 12, 24),
        frequency_hz=120.0,
        waveguide_id="wg1",
        node_a="rear",
        node_b="mouth",
    )

    coarse, medium, fine = report.observations
    assert coarse.segments == 6
    assert medium.segments == 12
    assert fine.segments == 24

    for obs in report.observations:
        assert obs.all_finite
        np.testing.assert_allclose(obs.pressure_values[0], obs.node_a_pressure)
        np.testing.assert_allclose(obs.pressure_values[-1], obs.node_b_pressure)
        np.testing.assert_allclose(obs.flow_values[0], obs.endpoint_flow_a)
        np.testing.assert_allclose(obs.flow_values[-1], -obs.endpoint_flow_b)
        np.testing.assert_allclose(obs.particle_values[0], obs.endpoint_velocity_a)
        np.testing.assert_allclose(obs.particle_values[-1], -obs.endpoint_velocity_b)
        np.testing.assert_allclose(obs.particle_values, obs.flow_values / obs.boundary_areas_m2)

    coarse_to_medium_flow = _relative_l2_change(
        coarse.flow_values,
        downsample_boundary_profile(medium.flow_values, coarse.segments, medium.segments),
    )
    medium_to_fine_flow = _relative_l2_change(
        medium.flow_values,
        downsample_boundary_profile(fine.flow_values, medium.segments, fine.segments),
    )
    medium_to_fine_pressure = _relative_l2_change(
        medium.pressure_values,
        downsample_boundary_profile(fine.pressure_values, medium.segments, fine.segments),
    )
    medium_to_fine_mouth = _relative_scalar_change(medium.mouth_pressure_abs, fine.mouth_pressure_abs)
    medium_to_fine_endpoint_flow = _relative_scalar_change(medium.endpoint_flow_abs, fine.endpoint_flow_abs)

    assert coarse_to_medium_flow <= 0.10
    assert medium_to_fine_flow <= 0.05
    assert medium_to_fine_flow <= coarse_to_medium_flow + 0.02
    assert medium_to_fine_pressure <= 0.02
    assert medium_to_fine_mouth <= 0.02
    assert medium_to_fine_endpoint_flow <= 0.02
