# Change log

This is the human-readable release and milestone history.
It complements Git history; it does not replace it.

---

## Post-`v0.2.0` housekeeping
**Status:** seeded for close

Completed so far:
- release-aligned housekeeping docs landed on `main`
- companion-book linkage made explicit
- post-release housekeeping checklist added
- post-release branch review and retention plan added
- next milestone seeded explicitly as `v0.3.0`

Immediate next action:
- open the recommended `v0.3.0` integration branch
- start the first bounded `v0.3.0` feature patch from that branch

---

## `v0.3.0`
**Status:** seeded

Planned title:
- `waveguide observability and API maturity`

Seed summary:
- use `v0.3.0` to promote already-existing observability capabilities into a cleaner supported user-facing contract
- prefer API/output-surface hardening over new solver physics
- keep the first patch bounded to exposing existing element observables cleanly

Seed reference:
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
