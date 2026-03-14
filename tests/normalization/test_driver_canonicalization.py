# tests/normalization/test_driver_canonicalization.py

import math

from os_lem.constants import C0, PARSER_REL_TOL, PARSER_ABS_TOL, RHO0
from os_lem.driver import canonical_from_explicit, canonical_from_ts_classic, normalize_driver


def _close_enough(a: float, b: float) -> bool:
    """Use frozen parser tolerance."""
    return abs(a - b) <= max(PARSER_ABS_TOL, PARSER_REL_TOL * abs(b))


def test_ts_and_explicit_match():
    ts = {
        "id": "drv1",
        "model": "ts_classic",
        "Re": "6 ohm",
        "Le": "0.4 mH",
        "Fs": "40 Hz",
        "Qes": 0.5,
        "Qms": 5.0,
        "Vas": "20 l",
        "Sd": "130 cm2",
        "node_front": "front",
        "node_rear": "rear",
    }
    drv_ts = canonical_from_ts_classic(ts)

    w = 2 * math.pi * 40.0
    cms = 20e-3 / (RHO0 * C0 * C0 * (130e-4) ** 2)
    mms = 1.0 / (w * w * cms)
    rms = w * mms / 5.0
    bl = math.sqrt(w * mms * 6.0 / 0.5)

    ex = {
        "id": "drv1",
        "model": "em_explicit",
        "Re": "6 ohm",
        "Le": "0.4 mH",
        "Bl": bl,
        "Mms": mms,
        "Cms": cms,
        "Rms": rms,
        "Sd": "130 cm2",
        "node_front": "front",
        "node_rear": "rear",
    }
    drv_ex = canonical_from_explicit(ex)

    for key in ("Re", "Le", "Bl", "Mms", "Cms", "Rms", "Sd"):
        assert _close_enough(getattr(drv_ts, key), getattr(drv_ex, key)), \
            f"{key}: {getattr(drv_ts, key)} vs {getattr(drv_ex, key)}"


def test_mixed_driver_consistent_values_are_accepted_with_warning():
    raw = {
        "id": "drv1",
        "model": "ts_classic",
        "Re": "6 ohm",
        "Le": "0.4 mH",
        "Fs": "40 Hz",
        "Qes": 0.5,
        "Qms": 5.0,
        "Vas": "20 l",
        "Sd": "130 cm2",
        "node_front": "front",
        "node_rear": "rear",
    }
    drv = canonical_from_ts_classic(raw)
    raw.update(
        {
            "Bl": drv.Bl,
            "Mms": drv.Mms,
            "Cms": drv.Cms,
            "Rms": drv.Rms,
        }
    )
    _, warnings = normalize_driver(raw)
    assert warnings

def test_ts_classic_reference_driver_matches_expected_canonical_values():
    ts = {
        "id": "drv1",
        "model": "ts_classic",
        "Re": "5.8 ohm",
        "Le": "0.35 mH",
        "Fs": "34 Hz",
        "Qes": 0.42,
        "Qms": 4.1,
        "Vas": "55 l",
        "Sd": "132 cm2",
        "node_front": "front",
        "node_rear": "rear",
    }

    drv = canonical_from_ts_classic(ts)

    w = 2.0 * math.pi * 34.0
    cms = 55e-3 / (RHO0 * C0 * C0 * (132e-4) ** 2)
    mms = 1.0 / (w * w * cms)
    rms = w * mms / 4.1
    bl = math.sqrt(w * mms * 5.8 / 0.42)

    assert _close_enough(drv.Cms, cms)
    assert _close_enough(drv.Mms, mms)
    assert _close_enough(drv.Rms, rms)
    assert _close_enough(drv.Bl, bl)
