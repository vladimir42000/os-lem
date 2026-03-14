# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session.

## Current checkpoint to verify at startup

Expected branch:
`feature/p5-patch02-minimal-waveguide-assembly`

Expected current checkpoint:
latest committed Phase 5 waveguide validation checkpoint after the first cylindrical reference-overlap check

Expected suite:
green

## Candidate next patch after startup verification

**Next bounded waveguide validation step after the cylindrical checkpoint**

## Purpose

Add one bounded waveguide validation capability on top of the already assembled,
validated, and now internally cross-checked `waveguide_1d` path.

## Preferred scope

Choose exactly one of:
- first limited conical reference-overlap check for a simple `waveguide_1d` case

Do not do more than one in a single patch.

## Out of scope

- distributed losses
- passive radiator
- multi-driver support
- broad output framework rewrite
- broad refactor
- GUI work
- broad external parity claims

## Acceptance requirement

The chosen patch must:
- preserve current green tests
- add focused tests or reference checks for the chosen overlap case
- avoid changing corrected solver conventions
- avoid broadening beyond one validation step

## Must-not-change list

- driver coupling sign conventions
- validated earlier solver behavior
- current assembled representation discipline
- already-landed waveguide pressure-profile behavior
- already-landed waveguide volume-velocity-profile behavior
- already-landed waveguide particle-velocity-profile behavior
