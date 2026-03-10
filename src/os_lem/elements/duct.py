"""Duct element formulas."""

from __future__ import annotations

from ..constants import RHO0


def duct_mass(length_m: float, area_m2: float) -> float:
    return RHO0 * length_m / area_m2


def duct_impedance(omega: float, length_m: float, area_m2: float) -> complex:
    return 1j * omega * duct_mass(length_m, area_m2)


def duct_admittance(omega: float, length_m: float, area_m2: float) -> complex:
    return 1.0 / duct_impedance(omega, length_m, area_m2)
