# os-lem next patch

## Status

This file defines the single immediate next patch target after the docs/governance reset is merged.

---

## Current checkpoint to verify at startup

Expected release baseline:
- `v0.1.0` on `main`

Expected working-line reality:
- recent observation debug work already happened
- `front/raw` is broadly credible
- remaining mismatch is localized to `mouth/port` observable semantics
- green suite is `108 passed` or newer green equivalent

---

## Immediate next patch target

**Land one bounded observation-layer development patch implementing the `mouth_directivity_only` candidate while keeping `front` unchanged.**

Recommended clean milestone branch:
- `milestone/v0.2.0-offset-line-observation`

Recommended patch branch:
- `fix/v0.2.0-mouth-directivity-only`

---

## Purpose

Turn the current best-supported debug conclusion into one disciplined development step without reopening broad debugging.

---

## Required scope

Do exactly these things:

- keep the current `front` semantics unchanged
- implement only the mouth-observable candidate path needed for `mouth_directivity_only`
- add or update focused regression protection for `front`
- validate narrowly on the existing offset-line case
- update only directly affected docs

---

## Out of scope

- broad transmission-line implementation work
- broad observation-layer redesign
- solver refactor
- frontend expansion
- broad docs rewrite beyond directly affected files
- unrelated kernel work

---

## Acceptance requirement

The patch is complete only if:

- the change is bounded to the observation layer
- `front` remains unchanged by evidence, not assumption
- the suite remains green
- the docs state the resulting contract honestly

---

## Must-not-change list

- the released `v0.1.0` baseline
- broad capability vocabulary
- unrelated waveguide or solver internals
- the small-patch discipline
