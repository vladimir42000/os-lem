"""Frozen v1 numerical constants."""

from __future__ import annotations

import math

RHO0: float = 1.2041
C0: float = 343.2
Z0: float = RHO0 * C0
P_REF: float = 20e-6
DEFAULT_DRIVE_V_RMS: float = 2.83
PI: float = math.pi

VALIDATION_REL_TOL: float = 1e-6
VALIDATION_ABS_TOL: float = 1e-12

PARSER_REL_TOL: float = 5e-3
PARSER_ABS_TOL: float = 1e-12
