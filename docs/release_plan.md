# os-lem release plan

## Planning principle

Releases are defined by capability maturity, not by raw patch count.

A release should answer:

- what the software can do
- how confident we are
- what is explicitly not yet claimed

Latest completed release:
- `v0.1.0`

Next planned release target:
- `v0.2.0`

---

## v0.1.0 — foundation release
**Status:** released

`v0.1.0` is the first honest external foundation release of `os-lem`.

It established:

- a narrow but real loudspeaker/enclosure kernel
- a tagged stable release on `main`
- a milestone-based release structure
- conservative capability/release claims

The exact release scope is documented in:
- `docs/v0_1_0_release_notes.md`

---

## v0.1.x — stabilization releases

### Intent

Post-`v0.1.0` patch releases may contain:

- bug fixes
- example hardening
- documentation correction
- narrow non-architectural cleanup
- regression-test strengthening

They should not redefine project scope.

At the current moment, no `v0.1.1` patch is planned.
The next active planning target is `v0.2.0`.

---

## v0.2.0 — offset-line observation-contract stabilization
**Status:** planned

### Intent

`v0.2.0` should introduce exactly one coherent next-level step beyond the `v0.1.0` foundation:

- turn the long observation/debug cycle into one bounded milestone outcome
- promote only a narrow observation-layer improvement
- document the result honestly

### Current repo truth supporting this plan

The working-line evidence now says:

- `front/raw` is broadly credible
- the remaining mismatch is localized to `mouth/port` observable semantics
- broad debugging restart is no longer the best opening move

### Planned opening sequence

1. docs/governance reset
2. open a clean `v0.2.0` milestone branch
3. land one bounded mouth-observable patch
4. validate narrowly
5. align docs and release notes

### Preferred first technical patch

- candidate: `mouth_directivity_only`
- constraint: keep `front` unchanged

### Rule

`v0.2.0` must preserve the small-patch philosophy.
It must not become a broad “everything after v0.1” bucket.

---

## v0.3.0 — observability and API maturity
**Status:** provisional planning only

Potential direction:
- strengthen user-facing observability around already delivered waveguide functionality
- expose currently-nearby outputs more cleanly
- harden the provisional API and maintained examples

This should only start after `v0.2.0` closes cleanly.

---

## v0.4.0 — waveguide physics maturity
**Status:** provisional planning only

Potential direction:
- conical-loss maturity
- stronger loss-model boundaries
- more disciplined line-workflow claims

---

## v0.5.0 and later

Choose one major capability family per milestone, for example:
- passive radiator support
- richer electrical network support
- multi-driver support

Do not mix several of these into one release.

---

## v1.0.0 — first intentionally supported release

`v1.0.0` should not be defined by time or patch count.

It should be defined by release quality:
- coherent supported core use-cases
- honest and stable capability boundaries
- strong enough regression confidence
- reproducible examples
- stable enough public-facing API surface for the claimed scope
- clear documentation of both supported and unsupported areas

Until then, all releases remain intentionally pre-1.0.
