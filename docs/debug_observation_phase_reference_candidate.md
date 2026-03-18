# Candidate fix checkpoint — observation phase reference

Status: candidate branch only. This is **not** a release claim and **not** a `main` merge instruction.

## Purpose

Freeze one bounded candidate fix for the AkAbak front-only phase mismatch discovered during `v0.2.0` debug work.

## What this candidate changes

The observation transfer used by solver-side radiator pressure outputs no longer applies an explicit `exp(-j k r)` propagation phase term.

The same candidate semantic is applied to the lower-level `os_lem.elements.radiator.radiator_observation_transfer()` helper so the internal/private solver path and the public helper stay aligned on this branch.

## Why this candidate exists

On the recovered debug baseline, AkAbak front-only comparison against `examples/free_air/model.yaml` showed:

- pressure phase MAE ≈ 88.24° over the full band
- pressure phase MAE ≈ 85.14° for `<= 1 kHz`
- Zin phase MAE ≈ 8.94° overall

This candidate patch reduced the same comparison to approximately:

- pressure phase MAE ≈ 16.90° over the full band
- pressure phase MAE ≈ 14.66° for `<= 1 kHz`
- Zin phase MAE unchanged at ≈ 8.94° overall

That makes this a valid bounded fix candidate for live validation.

## Files touched by the candidate

- `src/os_lem/solve.py`
- `src/os_lem/elements/radiator.py`
- `tests/solve/test_radiator_outputs.py`
- `tests/solve/test_frozen_reference_outputs.py`

## What this candidate does **not** claim

- no broad AkAbak parity claim
- no Hornresp parity claim
- no offset-line / TL parity claim
- no release-ready API freeze
- no instruction to merge into `main`

## Promotion rule

Only promote this candidate after:

1. live `pytest -q` remains green
2. live AkAbak front-only comparison reproduces the pressure-phase collapse
3. plots are visually reviewed by the operator
4. the patch is committed on a narrow `fix/*` branch
5. any later merge goes to a `v0.2.0` integration path first, not directly to `main`
