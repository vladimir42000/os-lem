"""Primitive waveguide_1d helpers for segmented conical lines."""

from __future__ import annotations

import math

import numpy as np

from ..constants import C0, RHO0


def _propagation_constant(omega: float, loss_np_per_m: float = 0.0) -> complex:
    return complex(loss_np_per_m, omega / C0)


def _characteristic_impedance_acoustic(area_m2: float) -> float:
    return RHO0 * C0 / area_m2


def segment_midpoint_areas(length_m: float, area_start_m2: float, area_end_m2: float, segments: int) -> np.ndarray:
    if segments <= 0:
        raise ValueError("segments must be > 0")
    r0 = math.sqrt(area_start_m2 / math.pi)
    rL = math.sqrt(area_end_m2 / math.pi)
    dx = length_m / segments
    areas = []
    for i in range(segments):
        x_mid = (i + 0.5) * dx
        r_mid = r0 + (rL - r0) * (x_mid / length_m)
        areas.append(math.pi * r_mid * r_mid)
    return np.asarray(areas, dtype=float)




def area_at_position(length_m: float, area_start_m2: float, area_end_m2: float, x_m: float) -> float:
    if length_m <= 0.0:
        raise ValueError("length_m must be > 0")
    if x_m < 0.0 or x_m > length_m:
        raise ValueError("x_m must be inside [0, length_m]")
    r0 = math.sqrt(area_start_m2 / math.pi)
    rL = math.sqrt(area_end_m2 / math.pi)
    r_x = r0 + (rL - r0) * (x_m / length_m)
    return float(math.pi * r_x * r_x)

def segment_endpoint_positions(length_m: float, segments: int) -> np.ndarray:
    if segments <= 0:
        raise ValueError("segments must be > 0")
    return np.linspace(0.0, length_m, segments + 1, dtype=float)


def uniform_segment_transfer(
    omega: float,
    length_m: float,
    area_m2: float,
    loss_np_per_m: float = 0.0,
) -> np.ndarray:
    gamma = _propagation_constant(omega, loss_np_per_m)
    zc_a = _characteristic_impedance_acoustic(area_m2)
    gl = gamma * length_m
    c = np.cosh(gl)
    s = np.sinh(gl)
    return np.array(
        [
            [c, zc_a * s],
            [s / zc_a, c],
        ],
        dtype=complex,
    )


def uniform_segment_admittance(
    omega: float,
    length_m: float,
    area_m2: float,
    loss_np_per_m: float = 0.0,
) -> np.ndarray:
    gamma = _propagation_constant(omega, loss_np_per_m)
    zc_a = _characteristic_impedance_acoustic(area_m2)
    gl = gamma * length_m
    s = np.sinh(gl)
    c = np.cosh(gl)
    if abs(s) < 1e-15:
        raise ZeroDivisionError("sinh(gamma*L) too small for stable csch/coth evaluation at this frequency")
    coth = c / s
    csch = 1.0 / s
    return np.array(
        [
            [(1.0 / zc_a) * coth, -(1.0 / zc_a) * csch],
            [-(1.0 / zc_a) * csch, (1.0 / zc_a) * coth],
        ],
        dtype=complex,
    )


def segment_sample_state(
    omega: float,
    x_m: float,
    area_m2: float,
    pressure_left: complex,
    flow_left: complex,
    loss_np_per_m: float = 0.0,
) -> np.ndarray:
    if x_m < 0.0:
        raise ValueError("x_m must be >= 0")
    transfer = uniform_segment_transfer(omega, x_m, area_m2, loss_np_per_m=loss_np_per_m)
    return transfer @ np.array([pressure_left, flow_left], dtype=complex)


# --- v0.7.0 exponential named-flare contract override ---
import math as _math
import numpy as _np


def _validate_named_flare_profile(profile: str) -> str:
    if not isinstance(profile, str):
        raise ValueError("waveguide_1d profile must be a string")
    if profile not in {"conical", "exponential", "tractrix"}:
        raise ValueError(f"unsupported waveguide_1d named flare profile {profile!r}")
    return profile


def _tractrix_monotone_coordinate(u: float) -> float:
    return u - _math.tanh(u)


def _tractrix_radius_at_fraction(radius_start_m: float, radius_end_m: float, fraction: float) -> float:
    if radius_start_m <= 0.0 or radius_end_m <= 0.0:
        raise ValueError("tractrix radii must be > 0")
    if radius_end_m < radius_start_m:
        raise ValueError("tractrix profile requires nondecreasing area from node_a to node_b")
    if _math.isclose(radius_start_m, radius_end_m, rel_tol=0.0, abs_tol=0.0):
        return float(radius_start_m)

    a = float(radius_end_m)
    u_start = _math.acosh(a / float(radius_start_m))
    coordinate_start = _tractrix_monotone_coordinate(u_start)
    target_coordinate = (1.0 - float(fraction)) * coordinate_start
    if target_coordinate <= 0.0:
        return float(radius_end_m)
    if target_coordinate >= coordinate_start:
        return float(radius_start_m)

    lo = 0.0
    hi = u_start
    for _ in range(64):
        mid = 0.5 * (lo + hi)
        if _tractrix_monotone_coordinate(mid) < target_coordinate:
            lo = mid
        else:
            hi = mid
    u = 0.5 * (lo + hi)
    return float(a / _math.cosh(u))


def area_at_position(
    length_m: float,
    area_start_m2: float,
    area_end_m2: float,
    x_m: float,
    profile: str = "conical",
) -> float:
    profile = _validate_named_flare_profile(profile)
    if length_m <= 0.0:
        raise ValueError("length_m must be > 0")
    if area_start_m2 <= 0.0 or area_end_m2 <= 0.0:
        raise ValueError("areas must be > 0")

    x = float(x_m)
    if x <= 0.0:
        return float(area_start_m2)
    if x >= float(length_m):
        return float(area_end_m2)
    if profile == "conical":
        return float(area_start_m2 + (area_end_m2 - area_start_m2) * (x / float(length_m)))
    if _math.isclose(area_start_m2, area_end_m2, rel_tol=0.0, abs_tol=0.0):
        return float(area_start_m2)
    if profile == "exponential":
        flare_rate = _math.log(area_end_m2 / area_start_m2) / float(length_m)
        return float(area_start_m2 * _math.exp(flare_rate * x))

    if area_end_m2 < area_start_m2:
        raise ValueError("tractrix profile requires area_end_m2 >= area_start_m2")
    radius = _tractrix_radius_at_fraction(
        _math.sqrt(area_start_m2 / _math.pi),
        _math.sqrt(area_end_m2 / _math.pi),
        x / float(length_m),
    )
    return float(_math.pi * radius * radius)


def segment_midpoint_areas(
    length_m: float,
    area_start_m2: float,
    area_end_m2: float,
    segments: int,
    profile: str = "conical",
) -> _np.ndarray:
    if segments <= 0:
        raise ValueError("segments must be > 0")
    dx = float(length_m) / int(segments)
    x_mid = (_np.arange(int(segments), dtype=float) + 0.5) * dx
    return _np.array(
        [
            area_at_position(length_m, area_start_m2, area_end_m2, float(x), profile)
            for x in x_mid
        ],
        dtype=float,
    )
