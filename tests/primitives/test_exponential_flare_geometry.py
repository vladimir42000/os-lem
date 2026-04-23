from __future__ import annotations

import numpy as np

from os_lem.elements.waveguide_1d import area_at_position, segment_midpoint_areas


def test_exponential_area_progression_is_monotone_and_endpoint_preserving() -> None:
    length_m = 0.4
    a0 = 10e-4
    a1 = 50e-4
    xs = np.linspace(0.0, length_m, 11)
    areas = np.array([area_at_position(length_m, a0, a1, float(x), profile="exponential") for x in xs])
    np.testing.assert_allclose(areas[0], a0)
    np.testing.assert_allclose(areas[-1], a1)
    assert np.all(np.diff(areas) > 0.0)


def test_exponential_segment_midpoints_differ_from_conical_for_nonuniform_flare() -> None:
    length_m = 0.4
    a0 = 10e-4
    a1 = 50e-4
    exp_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="exponential")
    con_mid = segment_midpoint_areas(length_m, a0, a1, 8, profile="conical")
    assert np.max(np.abs(exp_mid - con_mid)) > 0.0
