# Radiator Padé contradiction note

## Status
Open issue identified during Session 4 scaffold testing.

## Observation
The primitive radiator passivity test for the frozen Padé pipe-end models fails with a significantly negative real part at the upper tested range point (`ka = 2.0`).

Observed failing value from pytest:
- `z.real ≈ -220.306`
- `z.imag ≈ 7238.556`

This is not consistent with a passive radiation impedance and is far larger than ordinary floating-point roundoff.

## Current implementation status
The current implementation in `src/os_lem/elements/radiator.py` appears to match the formula currently frozen in `docs/radiator_models.md`.

## Consequence
At present, there is a contradiction between:
- the frozen formula as implemented, and
- the frozen validation expectation that the real part remain non-negative within the tested range.

## Rule going forward
Do not weaken the radiator passivity test to hide this issue.
Do not change the formula without verifying the authoritative source basis first.

## Next action
Verify the Padé formula transcription and normalization against the intended reference source before proceeding to rely on these radiator models in the coupled solver.
