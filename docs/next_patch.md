# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session.

## Current checkpoint to verify at startup

Expected branch:
`feature/p5-patch02-minimal-waveguide-assembly`

Expected current checkpoint:
latest committed Phase 5 cylindrical-loss implementation checkpoint plus bounded `ts_classic` motor-normalization bug-fix candidate

Expected suite:
green

## Candidate next patch after startup verification

**Fix `ts_classic` canonical `Bl` normalization**

## Purpose

Correct the `ts_classic` driver canonicalization bug that underestimates `Bl`. This patch is intentionally limited to the canonical normalization error; the remaining sealed-box impedance mismatch stays on the debug track until verified separately.

## Required scope

Do exactly these things:
- fix the `Bl` derivation in `src/os_lem/driver.py`
- update canonical driver normalization tests so expected `Bl` is computed from the correct T/S relation
- update only directly affected project docs to reflect the correction checkpoint

## Out of scope

- frontend work
- bass-reflex diagnosis expansion in the same patch
- passive radiator
- multi-driver support
- broad output framework rewrite
- broad refactor
- GUI work
- broad external parity claims

## Acceptance requirement

The chosen patch must:
- preserve current green tests
- correct `ts_classic` canonical `Bl` normalization
- add regression coverage that would have caught the prior canonical normalization bug
- avoid changing unrelated solver conventions
- avoid broadening beyond one correctness fix

## Must-not-change list

- driver coupling sign conventions
- validated earlier solver behavior outside the corrected `ts_classic` normalization
- current assembled representation discipline
- already-landed waveguide pressure-profile behavior
- already-landed waveguide volume-velocity-profile behavior
- already-landed waveguide particle-velocity-profile behavior
- already-landed cylindrical-loss behavior
