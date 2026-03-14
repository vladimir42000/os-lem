# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session.

## Current checkpoint to verify at startup

Expected branch:
`feature/p5-patch02-minimal-waveguide-assembly`

Expected current checkpoint:
latest committed Phase 5 waveguide validation checkpoint after the first cylindrical and conical reference-overlap checks

Expected suite:
green

## Candidate next patch after startup verification

**Next bounded waveguide loss-boundary step after the cylindrical and conical checkpoints**

## Purpose

Freeze one bounded waveguide loss-boundary decision on top of the already assembled,
validated, and now internally cross-checked `waveguide_1d` path.

## Preferred scope

Choose exactly one of:
- freeze the minimal distributed-loss boundary for `waveguide_1d` before any lossy implementation work

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
- freeze the exact loss-boundary scope and keep the current validated lossless path unchanged
- avoid changing corrected solver conventions
- avoid broadening beyond one validation step

## Must-not-change list

- driver coupling sign conventions
- validated earlier solver behavior
- current assembled representation discipline
- already-landed waveguide pressure-profile behavior
- already-landed waveguide volume-velocity-profile behavior
- already-landed waveguide particle-velocity-profile behavior
