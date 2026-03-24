"""Frozen v1 radiator formulas."""

from __future__ import annotations

import math

from scipy.special import j1, struve

from ..constants import C0, PI, RHO0, Z0

_FLANGED = {"n1": 0.182, "d1": 1.825, "d2": 0.649}
_UNFLANGED = {"n1": 0.167, "d1": 1.393, "d2": 0.457}


def piston_radius_from_area(area_m2: float) -> float:
    return math.sqrt(area_m2 / PI)


def on_axis_circular_piston_directivity(omega: float, area_m2: float) -> complex:
    """Return the on-axis circular-piston directivity factor 2*J1(ka)/ka.

    This is a bounded observation-layer helper for expert-guided mouth/port
    observation candidates. The small-ka limit is exactly 1.
    """

    if area_m2 <= 0.0:
        raise ValueError("area_m2 must be > 0")

    a = piston_radius_from_area(area_m2)
    ka = (omega / C0) * a
    if abs(ka) < 1.0e-10:
        return 1.0 + 0.0j
    return complex(2.0 * j1(ka) / ka, 0.0)


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


_ALLOWED_RADIATION_SPACES = {"4pi", "2pi", "pi", "half_pi"}


def default_radiation_space_for_model(model: str) -> str:
    if model in {"infinite_baffle_piston", "flanged_piston"}:
        return "2pi"
    if model == "unflanged_piston":
        return "4pi"
    raise ValueError(f"Unsupported radiator model: {model!r}")


def normalize_radiation_space(space: str) -> str:
    token = str(space).strip()
    if token not in _ALLOWED_RADIATION_SPACES:
        raise ValueError(
            f"Unsupported radiation_space {space!r}; expected one of {sorted(_ALLOWED_RADIATION_SPACES)!r}"
        )
    return token


def solid_angle_for_radiation_space(space: str) -> float:
    token = normalize_radiation_space(space)
    if token == "4pi":
        return 4.0 * PI
    if token == "2pi":
        return 2.0 * PI
    if token == "pi":
        return PI
    return 0.5 * PI


def radiator_observation_transfer(
    model: str,
    omega: float,
    distance_m: float,
    *,
    radiation_space: str | None = None,
) -> complex:
    token = default_radiation_space_for_model(model) if radiation_space is None else normalize_radiation_space(radiation_space)
    coeff = 1j * omega * RHO0 / (solid_angle_for_radiation_space(token) * distance_m)
    return coeff
