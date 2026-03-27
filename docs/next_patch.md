# Next action

## Live rule

This file is a live sequencing document owned by `AUDIT`.
It must agree with `docs/session_handover.md`.

---

## Current state after director reset

No routine DEV patch is frozen yet.

Required next action:
- `AUDIT: post-reset readiness check for v0.4.0`

---

## What the first post-reset AUDIT must decide

The audit must read the real repo state and choose exactly one of these outcomes:

### READY
The repo is ready for exactly one next bounded DEV patch.
The audit must then name that patch explicitly.

### NOT READY
The repo still has a sequencing or milestone-control inconsistency.
The audit must then name exactly one bounded reset/decision patch first.

---

## Guard rail

Do not guess the next DEV patch from older close-sequence text.
After this reset, the next DEV patch must be re-frozen from current repo truth.
