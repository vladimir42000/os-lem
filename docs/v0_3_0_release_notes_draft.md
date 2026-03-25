# os-lem v0.3.0 release notes (draft)

## Draft status

This file is a draft.

`v0.3.0` is not released yet.
The purpose of this draft is to freeze the wording early so the eventual merge to `main` stays honest and bounded.

Working release title:
- `waveguide observability and API maturity`

---

## Release character

`v0.3.0` is intended to be a bounded maturity follow-up to the `v0.2.0` release.

It does **not** attempt to turn `os-lem` into a broad transmission-line parity release or a broad solver-expansion release.
Instead, it packages one disciplined next step:

- promote already-existing element observables into the supported API/output surface
- harden parser-side contract validation around that promoted surface
- add end-to-end facade negative-path regression coverage
- keep milestone governance, handover text, and capability wording aligned to the tested repo truth

---

## Planned inclusions in v0.3.0

### Promoted supported observability surface
- `element_volume_velocity`
- `element_particle_velocity`
- supported targets:
  - `duct`
  - `radiator`
  - `waveguide_1d` endpoint exports via explicit `location: a|b`

### Contract hardening
- early parser rejection for incomplete or unsupported promoted element-observable requests
- explicit facade behavior around invalid promoted element-observable requests
- preserved default behavior outside the promoted bounded surface

### Regression hardening
- end-to-end facade regression coverage for valid promoted element observables
- end-to-end facade regression coverage for invalid promoted element-observable requests
- milestone validation observed green at `128 passed`

### Process significance
- disciplined patch-pack completion on a milestone branch
- explicit close decision before release-promotion planning
- clearer distinction between completed milestone truth and release-promotion work still pending

---

## Explicit non-claims

`v0.3.0` should **not** claim:

- broad Hornresp parity
- broad AkAbak parity
- broad transmission-line maturity beyond the currently documented supported surface
- new waveguide physics models
- passive radiator support as a general project capability
- multi-driver support
- conical lossy `waveguide_1d` maturity beyond the current bounded state
- stable long-term public API beyond the promoted documented facade surface
- product-grade frontend maturity

---

## Recommended release wording

Suggested short release summary:

> `v0.3.0` promotes bounded element observability into the supported API/output surface, hardens the contract around that surface, and closes the milestone with regression-backed documentation and governance aligned to the tested repo state.

Suggested one-sentence caveat:

> This is an observability/API maturity release, not a broad transmission-line or solver-physics expansion claim.

---

## Pre-release checklist

Before merging `v0.3.0` to `main`, confirm:

- milestone branch is green
- release wording still matches the tested repository state
- no unsupported parity or maturity language slipped into docs
- the promoted supported observable surface remains documented narrowly and honestly
- release-promotion work did not reopen closed milestone scope

---

## Follow-on direction after v0.3.0

Only after `v0.3.0` is either promoted or explicitly deferred should the project consider the next work family, such as:
- later milestone seeding for new capability work
- bounded release stabilization on top of `v0.3.0`
- a separately justified next maturity track
