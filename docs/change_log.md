# Change log

This is the human-readable release and milestone history.
It complements Git history; it does not replace it.

---

## `v0.4.0`
**Status:** active

Title:
- `capability expansion`

Opening milestone direction:
- start from the released `v0.3.0` line
- focus first on waveguide physics maturity for practical TL / horn workflows
- keep the opening campaign centered on lossy conical `waveguide_1d` maturity rather than on passive radiator, multi-driver, or electrical-network expansion

Immediate next action:
- land the bounded seed/charter patch for `v0.4.0`
- then open `feat/v0.4.0-conical-lossy-waveguide-mvp`

---

## `v0.3.0`
**Status:** released

Title:
- `waveguide observability and API maturity`

Release summary:
- promoted already-implemented element observables through the supported API/output surface
- kept parser-side promoted-observable validation aligned with the supported contract
- added end-to-end negative-path facade regression coverage for promoted element observables
- aligned milestone governance docs, capability wording, and handover text to the released regression-hardened state
- completed bounded release-promotion planning and promoted the line to `main`
- released and tagged `v0.3.0`

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
