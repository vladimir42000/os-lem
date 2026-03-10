"""Driver normalization helpers."""

from __future__ import annotations

import math
from dataclasses import asdict

from .constants import C0, PARSER_ABS_TOL, PARSER_REL_TOL, RHO0
from .errors import ValidationError
from .model import Driver
from .units import parse_value

_TS_REQUIRED = {
    "id",
    "model",
    "Re",
    "Le",
    "Fs",
    "Qes",
    "Qms",
    "Vas",
    "Sd",
    "node_front",
    "node_rear",
}

_EXPLICIT_REQUIRED = {
    "id",
    "model",
    "Re",
    "Le",
    "Bl",
    "Mms",
    "Cms",
    "Rms",
    "Sd",
    "node_front",
    "node_rear",
}

_ALLOWED_KEYS = _TS_REQUIRED | _EXPLICIT_REQUIRED | {"source_voltage", "source_voltage_rms"}


def _close_enough(a: float, b: float) -> bool:
    return abs(a - b) <= max(PARSER_ABS_TOL, PARSER_REL_TOL * abs(b))


def _require_positive(name: str, value: float) -> None:
    if value <= 0.0:
        raise ValidationError(f"Driver parameter {name!r} must be > 0, got {value!r}")


def canonical_from_ts_classic(raw: dict) -> Driver:
    missing = sorted(_TS_REQUIRED - raw.keys())
    if missing:
        raise ValidationError(f"Missing required ts_classic fields: {missing}")

    Re = parse_value(raw["Re"])
    Le = parse_value(raw["Le"])
    Fs = parse_value(raw["Fs"])
    Qes = float(raw["Qes"])
    Qms = float(raw["Qms"])
    Vas = parse_value(raw["Vas"])
    Sd = parse_value(raw["Sd"])

    for name, value in {
        "Re": Re,
        "Le": Le,
        "Fs": Fs,
        "Qes": Qes,
        "Qms": Qms,
        "Vas": Vas,
        "Sd": Sd,
    }.items():
        _require_positive(name, value)

    w_s = 2.0 * math.pi * Fs
    Cms = Vas / (RHO0 * C0 * C0 * Sd * Sd)
    Mms = 1.0 / (w_s * w_s * Cms)
    Rms = w_s * Mms / Qms
    Bl = math.sqrt(Re * Rms / Qes)

    return Driver(
        id=str(raw["id"]),
        Re=Re,
        Le=Le,
        Bl=Bl,
        Mms=Mms,
        Cms=Cms,
        Rms=Rms,
        Sd=Sd,
        node_front=str(raw["node_front"]),
        node_rear=str(raw["node_rear"]),
        source_voltage_rms=parse_value(raw.get("source_voltage_rms", raw.get("source_voltage", 2.83))),
    )


def canonical_from_explicit(raw: dict) -> Driver:
    missing = sorted(_EXPLICIT_REQUIRED - raw.keys())
    if missing:
        raise ValidationError(f"Missing required em_explicit fields: {missing}")

    driver = Driver(
        id=str(raw["id"]),
        Re=parse_value(raw["Re"]),
        Le=parse_value(raw["Le"]),
        Bl=parse_value(raw["Bl"]),
        Mms=parse_value(raw["Mms"]),
        Cms=parse_value(raw["Cms"]),
        Rms=parse_value(raw["Rms"]),
        Sd=parse_value(raw["Sd"]),
        node_front=str(raw["node_front"]),
        node_rear=str(raw["node_rear"]),
        source_voltage_rms=parse_value(raw.get("source_voltage_rms", raw.get("source_voltage", 2.83))),
    )

    for key, value in asdict(driver).items():
        if key in {"id", "node_front", "node_rear"}:
            continue
        _require_positive(key, float(value))
    return driver


def normalize_driver(raw: dict) -> tuple[Driver, list[str]]:
    unknown = sorted(set(raw.keys()) - _ALLOWED_KEYS)
    if unknown:
        raise ValidationError(f"Unknown driver fields: {unknown}")

    model = raw.get("model")
    if model not in {"ts_classic", "em_explicit"}:
        raise ValidationError(f"Unsupported driver model: {model!r}")

    warnings: list[str] = []

    if model == "ts_classic":
        canonical = canonical_from_ts_classic(raw)
        explicit_fields_present = {"Bl", "Mms", "Cms", "Rms"} & raw.keys()
        if explicit_fields_present:
            explicit = canonical_from_explicit(raw)
            for key in ("Re", "Le", "Bl", "Mms", "Cms", "Rms", "Sd"):
                a = getattr(canonical, key)
                b = getattr(explicit, key)
                if not _close_enough(a, b):
                    raise ValidationError(
                        f"Mixed driver data inconsistent for {key}: derived={a!r}, explicit={b!r}"
                    )
            warnings.append("Mixed ts_classic + explicit driver data accepted: values consistent within tolerance.")
        return canonical, warnings

    return canonical_from_explicit(raw), warnings
