import math

import numpy as np

from os_lem.elements.waveguide_1d import (
    segment_midpoint_areas,
    uniform_segment_admittance,
    uniform_segment_transfer,
)


def test_midpoint_areas_cylindrical_special_case():
    areas = segment_midpoint_areas(1.0, 0.01, 0.01, 8)
    assert np.allclose(areas, 0.01)


def test_uniform_segment_transfer_matches_admittance_form():
    f = 100.0
    w = 2 * math.pi * f
    L = 0.1
    S = 0.01

    T = uniform_segment_transfer(w, L, S)
    Y = uniform_segment_admittance(w, L, S)

    p2 = 0.7 + 0.1j
    q2 = -0.2 + 0.05j
    p1, q1 = T @ np.array([p2, q2], dtype=complex)

    lhs = np.array([q1, -q2], dtype=complex)
    rhs = Y @ np.array([p1, p2], dtype=complex)

    assert np.allclose(lhs, rhs, rtol=1e-10, atol=1e-12)
