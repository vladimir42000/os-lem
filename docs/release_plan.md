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

## v0.2.0 — next bounded capability milestone
**Status:** planned

### Intent

`v0.2.0` should introduce exactly one coherent next-level capability step beyond the `v0.1.0` foundation.

The first step in this cycle should be a bounded truth-finding investigation, not an immediate broad implementation promise.

### Planned opening move

Start by determining repository truth for a minimal transmission-line / offset-line case:

- define one minimal reproducible case
- compare expected versus actual behavior
- classify current support as:
  - already supported
  - partially supported
  - unsupported

### Why this is the right opening move

Because `v0.1.0` deliberately avoided broad line / transmission-line claims.

Before choosing the next implementation milestone, the project should first determine what the current kernel already does and does not support.

### Rule

`v0.2.0` must preserve the small-patch philosophy.
It must not become a broad “everything after v0.1” bucket.

---

## v0.3.0 and later

Further releases should continue capability-based growth, such as:

- stronger line / waveguide maturity
- broader validation
- cleaner examples
- more coherent user-facing workflows
- tighter API posture when warranted

These items must only be scheduled when validated maturity supports them.

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

---

## Current planning caution

The correct next move after a first release is not to broaden claims impulsively.

The correct next move is to preserve discipline:
- small bounded patches
- milestone integration
- evidence before claims
