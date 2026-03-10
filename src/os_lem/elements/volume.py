"""Volume element formulas."""

from __future__ import annotations

from ..constants import C0, RHO0


def volume_compliance(volume_m3: float) -> float:
    return volume_m3 / (RHO0 * C0 * C0)


def volume_admittance(omega: float, volume_m3: float) -> complex:
    return 1j * omega * volume_compliance(volume_m3)
