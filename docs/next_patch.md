# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session.

## Current checkpoint to verify at startup

Expected branch:
`feature/p5-patch02-minimal-waveguide-assembly`

Expected current checkpoint:
latest committed Phase 5 waveguide validation checkpoint after the first cylindrical and conical reference-overlap checks and the frozen loss-boundary docs patch

Expected suite:
green

## Candidate next patch after startup verification

**Next bounded waveguide lossy implementation step after the frozen loss-boundary checkpoint**

## Purpose

Implement one bounded lossy waveguide step on top of the already assembled,
validated, and now loss-boundary-frozen `waveguide_1d` path.

## Preferred scope

Choose exactly one of:
- implement the first minimal distributed-loss extension for cylindrical `waveguide_1d` only

Do not do more than one in a single patch.

## Out of scope

- distributed losses beyond the first cylindrical `waveguide_1d` boundary
- passive radiator
- multi-driver support
- broad output framework rewrite
- broad refactor
- GUI work
- broad external parity claims

## Acceptance requirement

The chosen patch must:
- preserve current green tests
- preserve current green tests
- keep the current validated lossless path intact outside the new bounded lossy cylindrical step
- avoid changing corrected solver conventions
- avoid broadening beyond one lossy implementation step
- avoid changing corrected solver conventions
- avoid broadening beyond one validation step

## Must-not-change list

- driver coupling sign conventions
- validated earlier solver behavior
- current assembled representation discipline
- already-landed waveguide pressure-profile behavior
- already-landed waveguide volume-velocity-profile behavior
- already-landed waveguide particle-velocity-profile behavior
