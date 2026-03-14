"""Primitive waveguide_1d helpers for segmented conical lines."""

from __future__ import annotations

import math

import numpy as np

from ..constants import C0, RHO0


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


def segment_endpoint_positions(length_m: float, segments: int) -> np.ndarray:
    if segments <= 0:
        raise ValueError("segments must be > 0")
    return np.linspace(0.0, length_m, segments + 1, dtype=float)


def uniform_segment_transfer(omega: float, length_m: float, area_m2: float) -> np.ndarray:
    k = omega / C0
    zc_a = RHO0 * C0 / area_m2
    c = math.cos(k * length_m)
    s = math.sin(k * length_m)
    return np.array(
        [
            [c, 1j * zc_a * s],
            [1j * (1.0 / zc_a) * s, c],
        ],
        dtype=complex,
    )


def uniform_segment_admittance(omega: float, length_m: float, area_m2: float) -> np.ndarray:
    k = omega / C0
    zc_a = RHO0 * C0 / area_m2
    s = math.sin(k * length_m)
    c = math.cos(k * length_m)
    if abs(s) < 1e-15:
        raise ZeroDivisionError("sin(k*L) too small for stable csc/cot evaluation at this frequency")
    cot = c / s
    csc = 1.0 / s
    return np.array(
        [
            [-1j * (1.0 / zc_a) * cot, 1j * (1.0 / zc_a) * csc],
            [1j * (1.0 / zc_a) * csc, -1j * (1.0 / zc_a) * cot],
        ],
        dtype=complex,
    )


def segment_sample_state(
    omega: float,
    x_m: float,
    area_m2: float,
    pressure_left: complex,
    flow_left: complex,
) -> np.ndarray:
    if x_m < 0.0:
        raise ValueError("x_m must be >= 0")
    transfer = uniform_segment_transfer(omega, x_m, area_m2)
    return transfer @ np.array([pressure_left, flow_left], dtype=complex)
