"""Future global matrix assembly lives here.

Session 4 scaffold note:
this module is intentionally not yet implemented.
The current milestone is parser/normalizer + primitive evaluators.
"""

from __future__ import annotations

from .errors import NotImplementedKernelError


def assemble_system(*args, **kwargs):
    raise NotImplementedKernelError(
        "Global coupled assembly is not implemented in this Session 4 scaffold yet."
    )
