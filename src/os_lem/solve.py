"""Future frequency-by-frequency solve entrypoints."""

from __future__ import annotations

from .errors import NotImplementedKernelError


def solve_frequency_sweep(*args, **kwargs):
    raise NotImplementedKernelError(
        "Frequency sweep solve is not implemented in this Session 4 scaffold yet."
    )
