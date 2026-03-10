import math

from os_lem.constants import RHO0
from os_lem.elements.duct import duct_admittance, duct_impedance, duct_mass


def test_duct_mass_formula():
    L = 0.18
    S = 24e-4
    assert duct_mass(L, S) == RHO0 * L / S


def test_duct_impedance_formula():
    f = 50.0
    w = 2 * math.pi * f
    L = 0.18
    S = 24e-4
    expected = 1j * w * (RHO0 * L / S)
    assert duct_impedance(w, L, S) == expected


def test_parallel_duct_equivalence_at_admittance_level():
    f = 50.0
    w = 2 * math.pi * f
    L = 0.18
    S = 24e-4
    y_single = duct_admittance(w, L, S)
    y_parallel = y_single + y_single
    y_equiv = duct_admittance(w, L / 2.0, S)
    assert abs(y_parallel - y_equiv) < 1e-12
