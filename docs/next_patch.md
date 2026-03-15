# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session after the current docs-alignment work is merged.

---

## Current checkpoint to verify at startup

Expected integration branch:
`milestone/v0.1.0-foundation`

Expected current posture:
- release governance docs landed
- milestone branch created
- docs aligned to current repo truth
- suite green

Expected suite:
`104 passed` or newer green equivalent

---

## Candidate next patch after startup verification

**Preserve maintained validation/example assets for the `v0.1.0` milestone**

Suggested patch branch:
`chore/v0.1.0-preserve-validation-examples`

---

## Purpose

Preserve useful Streamlit / validation example assets in tracked form and document their role honestly.

The goal is to support validation and demonstration workflows without broadening kernel, API, or product claims.

---

## Required scope

Do exactly these things:

- inspect the current tracked example state in `examples/streamlit_frontend/`
- compare it against preserved local/example branch assets
- restore only genuinely useful example files needed for validation/demo workflows
- add a minimal README or note if needed
- keep example/prototype status explicit
- prefer the provisional `os_lem.api` facade over raw internal pipeline imports where practical within the bounded patch

---

## Out of scope

- solver/kernel changes
- parser changes
- API redesign
- broad frontend expansion
- transmission-line feature work
- broad docs rewrite beyond directly affected example notes
- broad productization claims

---

## Acceptance requirement

The chosen patch must:

- preserve useful example assets in tracked form
- keep their status explicitly prototype/example/validation-oriented
- avoid reintroducing brittle direct coupling to unstable internal modules where the facade is the intended integration surface
- preserve the current green suite
- avoid broadening external claims

---

## Must-not-change list

- current solver conventions
- corrected sealed-box and bass-reflex checkpoints
- current validated waveguide subset
- current release governance structure
- current narrow public-claim posture
