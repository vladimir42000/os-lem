"""Frozen v1 radiator formulas."""

from __future__ import annotations

import math

from scipy.special import j1, struve

from ..constants import C0, PI, RHO0, Z0

_FLANGED = {"n1": 0.182, "d1": 1.825, "d2": 0.649}
_UNFLANGED = {"n1": 0.167, "d1": 1.393, "d2": 0.457}


def piston_radius_from_area(area_m2: float) -> float:
    return math.sqrt(area_m2 / PI)


def _struve_h1_aarts_janssen(z: float) -> float:
    return float(struve(1, z))


def _z_baffled(ka: float) -> complex:
    x = 2.0 * ka
    if abs(x) < 1e-10:
        return 0.0j
    r1 = 1.0 - 2.0 * j1(x) / x
    x1 = 2.0 * _struve_h1_aarts_janssen(x) / x
    return complex(r1, x1)


def _z_pade(ka: float, *, n1: float, d1: float, d2: float) -> complex:
    x = ka
    num = 1j * (d1 - n1) * x + d2 * x * x
    den = 2.0 + 1j * (d1 + n1) * x - d2 * x * x
    return num / den


def radiator_impedance(model: str, omega: float, area_m2: float) -> complex:
    a = piston_radius_from_area(area_m2)
    ka = (omega / C0) * a

    if model == "infinite_baffle_piston":
        z = _z_baffled(ka)
    elif model == "flanged_piston":
        z = _z_pade(ka, **_FLANGED)
    elif model == "unflanged_piston":
        z = _z_pade(ka, **_UNFLANGED)
    else:
        raise ValueError(f"Unsupported radiator model: {model!r}")

    return (Z0 / area_m2) * z


def radiator_observation_transfer(model: str, omega: float, distance_m: float) -> complex:
    k = omega / C0
    if model in {"infinite_baffle_piston", "flanged_piston"}:
        coeff = 1j * omega * RHO0 / (2.0 * PI * distance_m)
    elif model == "unflanged_piston":
        coeff = 1j * omega * RHO0 / (4.0 * PI * distance_m)
    else:
        raise ValueError(f"Unsupported radiator model: {model!r}")
    return coeff * complex(math.cos(-k * distance_m), math.sin(-k * distance_m))
