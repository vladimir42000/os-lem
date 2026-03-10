import math

from os_lem.constants import C0, RHO0
from os_lem.elements.volume import volume_admittance, volume_compliance


def test_volume_compliance_formula():
    V = 18e-3
    expected = V / (RHO0 * C0 * C0)
    assert volume_compliance(V) == expected


def test_volume_admittance_formula():
    f = 100.0
    w = 2.0 * math.pi * f
    V = 18e-3
    Ca = V / (RHO0 * C0 * C0)
    assert volume_admittance(w, V) == 1j * w * Ca
