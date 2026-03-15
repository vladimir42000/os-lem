# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session after the post-`v0.1.0` planning patch is merged.

---

## Current checkpoint to verify at startup

Expected base branch:
`main`

Expected current posture:
- `v0.1.0` is already released and tagged
- release docs and metadata reflect the released baseline
- suite green

Expected suite:
`104 passed` or newer green equivalent

---

## Candidate next patch after startup verification

**Open the `v0.2.0` cycle with a bounded minimal line/offset-line truth check**

Suggested milestone branch:
`milestone/v0.2.0-line-truth`

Suggested first technical patch branch:
`debug/v0.2.0-offset-line-truth-check`

---

## Purpose

Determine actual repository truth for one minimal transmission-line / offset-line case before any broader support claim is made.

---

## Required scope

Do exactly these things:

- define one minimal reproducible line / offset-line model
- inspect current kernel behavior on that case
- compare expected vs actual behavior
- classify current support as:
  - already supported
  - partially supported
  - unsupported
- document the result honestly

---

## Out of scope

- broad transmission-line implementation work
- API freeze for line workflows
- frontend expansion
- broad docs rewrite
- broad roadmap revision
- unrelated kernel work

---

## Acceptance requirement

The patch is complete only if:

- one bounded test/investigation case is defined
- current repo truth is stated clearly
- no broad unsupported claim is introduced
- the suite remains green

---

## Must-not-change list

- the released `v0.1.0` baseline
- current conservative release posture
- `main` as the stable released branch
