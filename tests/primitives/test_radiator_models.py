import math

import numpy as np

from os_lem.constants import C0, PI, RHO0, Z0
from os_lem.elements.radiator import (
    on_axis_circular_piston_directivity,
    piston_radius_from_area,
    radiator_impedance,
    radiator_observation_transfer,
)


def _area_for_ka_target(ka: float, omega: float) -> float:
    a = ka * C0 / omega
    return PI * a * a


def test_radiator_observation_transfer_default_half_vs_full_space():
    f = 100.0
    w = 2 * math.pi * f
    r = 1.0
    h_half = radiator_observation_transfer("flanged_piston", w, r)
    h_full = radiator_observation_transfer("unflanged_piston", w, r)
    assert abs(h_half / h_full - 2.0) < 1e-12


def test_radiator_observation_transfer_explicit_radiation_space_ratios():
    f = 100.0
    w = 2 * math.pi * f
    r = 1.0
    h_4pi = radiator_observation_transfer("unflanged_piston", w, r, radiation_space="4pi")
    h_2pi = radiator_observation_transfer("unflanged_piston", w, r, radiation_space="2pi")
    h_pi = radiator_observation_transfer("unflanged_piston", w, r, radiation_space="pi")
    h_half_pi = radiator_observation_transfer("unflanged_piston", w, r, radiation_space="half_pi")
    assert abs(h_2pi / h_4pi - 2.0) < 1e-12
    assert abs(h_pi / h_2pi - 2.0) < 1e-12
    assert abs(h_half_pi / h_pi - 2.0) < 1e-12


def test_flanged_and_unflanged_passivity_and_inertive_low_frequency():
    f = 100.0
    w = 2 * math.pi * f
    for ka in [0.05, 0.2, 0.5, 1.0, 2.0]:
        area = _area_for_ka_target(ka, w)
        for model in ["flanged_piston", "unflanged_piston"]:
            z = radiator_impedance(model, w, area)
            assert z.real >= -1e-12
    area = _area_for_ka_target(0.05, w)
    assert radiator_impedance("flanged_piston", w, area).imag > 0.0
    assert radiator_impedance("unflanged_piston", w, area).imag > 0.0


def test_pipe_end_low_frequency_reactance_slopes_match_frozen_end_corrections():
    f = 100.0
    w = 2 * math.pi * f
    for eta, model in [(0.8216, "flanged_piston"), (0.6133, "unflanged_piston")]:
        area = _area_for_ka_target(0.05, w)
        a = piston_radius_from_area(area)
        z = radiator_impedance(model, w, area)
        expected_slope = Z0 * eta / area * (a / C0)
        measured_slope = z.imag / w
        assert math.isclose(measured_slope, expected_slope, rel_tol=0.06, abs_tol=0.0)


def test_baffled_piston_low_frequency_behavior_is_inertive():
    f = 50.0
    w = 2 * math.pi * f
    area = 132e-4
    z = radiator_impedance("infinite_baffle_piston", w, area)
    assert z.imag > 0.0
    assert z.real >= -1e-12



def test_baffled_piston_low_frequency_reactance_matches_small_ka_slope():
    f = 20.0
    w = 2 * math.pi * f
    area = 132e-4
    a = piston_radius_from_area(area)
    ka = (w / C0) * a
    z = radiator_impedance("infinite_baffle_piston", w, area)

    normalized_reactance = z.imag * area / Z0
    expected = 8.0 * ka / (3.0 * PI)

    assert normalized_reactance > 0.0
    assert math.isclose(normalized_reactance, expected, rel_tol=0.05, abs_tol=0.0)

def test_baffled_piston_formula_is_stable_at_small_ka():
    f = 20.0
    w = 2 * math.pi * f
    area = 1e-4
    z = radiator_impedance("infinite_baffle_piston", w, area)
    assert np.isfinite(z.real)
    assert np.isfinite(z.imag)


def test_on_axis_circular_piston_directivity_has_small_ka_limit_of_unity():
    directivity = on_axis_circular_piston_directivity(0.0, 132e-4)
    assert directivity == 1.0 + 0.0j


def test_on_axis_circular_piston_directivity_is_finite_and_not_greater_than_unity_on_axis():
    directivity = on_axis_circular_piston_directivity(2.0 * math.pi * 2000.0, 132e-4)
    assert np.isfinite(directivity.real)
    assert np.isfinite(directivity.imag)
    assert abs(directivity.imag) < 1e-12
    assert abs(directivity) <= 1.0 + 1e-12
