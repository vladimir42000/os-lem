"""Small frozen v1 engineering-unit parser."""

from __future__ import annotations

import re

from .errors import SchemaError

_UNIT_FACTORS = {
    "m": 1.0,
    "cm": 1e-2,
    "mm": 1e-3,
    "m2": 1.0,
    "cm2": 1e-4,
    "m3": 1.0,
    "l": 1e-3,
    "hz": 1.0,
    "s": 1.0,
    "ms": 1e-3,
    "h": 1.0,
    "mh": 1e-3,
    "ohm": 1.0,
}

_TOKEN_RE = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z0-9]+)?\s*$"
)


def parse_value(raw: float | int | str, expected_unit_group: str | None = None) -> float:
    """
    Parse a number or "number unit" string into SI.
    Numeric values without units are interpreted as already-SI.
    """
    if isinstance(raw, (int, float)):
        return float(raw)

    if not isinstance(raw, str):
        raise SchemaError(f"Unsupported value type: {type(raw)!r}")

    m = _TOKEN_RE.match(raw)
    if not m:
        raise SchemaError(f"Could not parse value with units: {raw!r}")

    value = float(m.group(1))
    unit = m.group(2)

    if unit is None:
        return value

    unit_key = unit.lower()
    if unit_key not in _UNIT_FACTORS:
        raise SchemaError(f"Unsupported unit: {unit}")

    return value * _UNIT_FACTORS[unit_key]
