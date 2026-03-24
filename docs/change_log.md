# Change log

This is the human-readable release and milestone history.
It complements Git history; it does not replace it.

---

## Post-`v0.2.0` housekeeping
**Status:** completed

Completed summary:
- release-aligned housekeeping docs landed on `main`
- companion-book linkage made explicit
- post-release housekeeping checklist added
- post-release branch review and retention plan added
- next milestone seeded explicitly as `v0.3.0`
- recommended `v0.3.0` integration branch opened
- first bounded `v0.3.0` feature patch landed on the milestone line
- first bounded `v0.3.0` bookkeeping patch landed on the milestone line

Outcome:
- `v0.3.0` is no longer only a seeded plan; it progressed to a completed milestone branch

---

## `v0.3.0`
**Status:** complete on milestone branch

Title:
- `waveguide observability and API maturity`

Milestone summary:
- opened integration branch `milestone/v0.3.0-waveguide-observability-and-api-maturity`
- landed `feat/v0.3.0-element-observable-api-surface`
- landed `chore/v0.3.0-first-patch-bookkeeping`
- landed `test/v0.3.0-element-observable-facade-error-contract`
- landed `chore/v0.3.0-post-regression-bookkeeping`
- landed `chore/v0.3.0-close-prep`
- exposed promoted element observables through the supported API/output surface
- kept parser-side promoted-observable validation aligned with the supported contract
- added end-to-end negative-path facade regression coverage for promoted element observables
- aligned milestone governance docs, capability wording, and handover text to the current regression-hardened state
- kept milestone scope conservative throughout the patch pack
- observed milestone line green at `128 passed`

Current decision:
- `v0.3.0` is complete on its milestone branch
- no further `v0.3.0` patch is recommended by default
- any continuation should be explicit release-promotion planning rather than reopened milestone growth

Milestone reference:
- `docs/v0_3_0_seed_plan.md`

---

## `v0.2.0`
**Status:** released

Release title:
- `offset-line observation-contract stabilization`

Released summary:
- completed the bounded observation-layer milestone without broad solver refactoring
- kept `front/raw` behavior unchanged while introducing an opt-in mouth/port candidate path
- added `observable_contract: mouth_directivity_only`
- added a connected-aperture normalization guard for that bounded candidate
- added a maintained offset-line compare harness with regression coverage
- aligned release docs, release notes, and release checklist around conservative claims

Reference docs:
- `docs/v0_2_0_release_notes_draft.md`
- `docs/v0_2_0_release_checklist.md`

---

## `v0.1.0`
**Status:** released

Summary:
- first honest foundation release on `main`
- one-driver coupled sweep kernel
- released `volume`, `duct`, `radiator`, minimal `waveguide_1d`
- released classical outputs and minimal waveguide observability subset
- released cylindrical-loss support inside the frozen cylindrical boundary
- released provisional `os_lem.api` facade
- conservative capability boundaries made explicit
