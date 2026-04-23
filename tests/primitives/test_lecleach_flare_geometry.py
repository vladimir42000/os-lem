from __future__ import annotations

import numpy as np

from os_lem.elements.waveguide_1d import area_at_position, segment_midpoint_areas


def test_lecleach_area_progression_is_monotone_and_endpoint_preserving() -> None:
    length_m = 0.4
    a0 = 10e-4
    a1 = 50e-4
    xs = np.linspace(0.0, length_m, 11)
    areas = np.array([area_at_position(length_m, a0, a1, float(x), profile="lecleach") for x in xs])
    np.testing.assert_allclose(areas[0], a0)
    np.testing.assert_allclose(areas[-1], a1)
    assert np.all(np.diff(areas) > 0.0)


def test_lecleach_midpoint_areas_differ_from_current_other_named_laws() -> None:
    length_m = 0.4
    a0 = 10e-4
    a1 = 50e-4
    lecleach_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="lecleach")
    conical_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="conical")
    exponential_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="exponential")
    tractrix_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="tractrix")
    hyperbolic_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="hyperbolic")
    parabolic_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="parabolic")
    assert np.max(np.abs(lecleach_mid - conical_mid)) > 0.0
    assert np.max(np.abs(lecleach_mid - exponential_mid)) > 0.0
    assert np.max(np.abs(lecleach_mid - tractrix_mid)) > 0.0
    assert np.max(np.abs(lecleach_mid - hyperbolic_mid)) > 0.0
    assert np.max(np.abs(lecleach_mid - parabolic_mid)) > 0.0
