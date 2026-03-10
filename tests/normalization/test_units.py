
---

## tests/normalization/test_units.py

```python
# tests/normalization/test_units.py

from os_lem.constants import VALIDATION_REL_TOL, VALIDATION_ABS_TOL
from os_lem.units import parse_value


def _close_enough(a: float, b: float) -> bool:
    """Use frozen validation tolerance."""
    return abs(a - b) <= max(VALIDATION_ABS_TOL, VALIDATION_REL_TOL * abs(b))


def test_parse_value_si_passthrough():
    assert _close_enough(parse_value(0.123), 0.123)


def test_parse_value_engineering_units():
    assert _close_enough(parse_value("100 cm"), 1.0)
    assert _close_enough(parse_value("132 cm2"), 132e-4)
    assert _close_enough(parse_value("18 l"), 18e-3)
    assert _close_enough(parse_value("0.35 mH"), 0.35e-3)