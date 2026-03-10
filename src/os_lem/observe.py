"""Future observation extraction layer."""

from __future__ import annotations

from .errors import NotImplementedKernelError


def evaluate_observations(*args, **kwargs):
    raise NotImplementedKernelError(
        "Observation evaluation is not implemented in this Session 4 scaffold yet."
    )
