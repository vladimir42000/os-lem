# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session.

## Current checkpoint to verify at startup

Expected branch:
`feature/p5-patch02-minimal-waveguide-assembly`

Expected current checkpoint:
latest committed Phase 5 observability checkpoint with pressure and volume-velocity line profiles aligned in docs

Expected suite:
green

## Candidate next patch after startup verification

**Next minimal waveguide-specific observability step**

## Purpose

Add one bounded waveguide observability capability on top of the already assembled,
validated, and partially observable `waveguide_1d` path.

## Preferred scope

Choose exactly one of:
- minimal `waveguide_1d` `line_profile` export for `particle_velocity`

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
- add focused tests for the new observable
- avoid changing corrected solver conventions
- avoid broadening beyond one observable step

## Must-not-change list

- driver coupling sign conventions
- validated earlier solver behavior
- current assembled representation discipline
- already-landed waveguide pressure-profile behavior
- already-landed waveguide volume-velocity-profile behavior
