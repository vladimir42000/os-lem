# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session.

## Current checkpoint to verify at startup

Expected branch:
`feature/p5-patch02-minimal-waveguide-assembly`

Expected current checkpoint:
latest committed Phase 5 cylindrical-loss implementation checkpoint

Expected suite:
green

## Candidate next patch after startup verification

**Next bounded lossy-boundary planning step**

## Purpose

Freeze one bounded lossy-scope decision on top of the already assembled,
validated, and now minimally cylindrical-lossy `waveguide_1d` path.

## Preferred scope

Choose exactly one of:
- freeze the minimal conical lossy boundary before any conical lossy implementation work

Do not do more than one in a single patch.

## Out of scope

- passive radiator
- multi-driver support
- broad output framework rewrite
- broad refactor
- GUI work
- broad external parity claims

## Acceptance requirement

The chosen patch must:
- preserve current green tests
- freeze one clear lossy-scope decision without implementing conical lossy code
- avoid changing corrected solver conventions
- avoid broadening beyond one planning step

## Must-not-change list

- driver coupling sign conventions
- validated earlier solver behavior
- current assembled representation discipline
- already-landed waveguide pressure-profile behavior
- already-landed waveguide volume-velocity-profile behavior
- already-landed waveguide particle-velocity-profile behavior
- already-landed cylindrical-loss behavior
