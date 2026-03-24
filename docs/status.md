# os-lem status

## Released baseline

- latest released version: `v0.2.0`
- released branch of record: `main`
- observed green suite on the release line: `118 passed`

---

## Active development milestone

- milestone: `v0.3.0`
- title: `waveguide observability and API maturity`
- active integration branch: `milestone/v0.3.0-waveguide-observability-and-api-maturity`
- observed green suite on the active milestone line after the landed regression-hardened patch set: `128 passed`

Current milestone state:
- the seeded `v0.3.0` integration branch is open and active
- the first bounded `v0.3.0` feature patch has landed on the milestone line
- the first bounded `v0.3.0` bookkeeping patch has landed on the milestone line
- the bounded facade error-contract regression patch has also landed on the milestone line
- the milestone should remain intentionally conservative while docs, capability wording, and handover state are aligned to the current regression-hardened repo truth

Current recommended work type:
- do a bounded bookkeeping/docs patch that records the landed regression patch honestly
- reassess from the active milestone branch whether `v0.3.0` now needs only a final close-prep patch
- do not reopen broad solver debugging or broad API redesign

---

## What `v0.2.0` established

- `front/raw` kept unchanged
- opt-in `observable_contract: mouth_directivity_only`
- connected-aperture normalization guard for the bounded mouth path
- maintained offset-line compare harness
- conservative release-story wording aligned to tested repo truth

---

## What the current `v0.3.0` patch set established

- supported API/output surface now exposes `element_volume_velocity`
- supported API/output surface now exposes `element_particle_velocity`
- promoted contract covers `duct`, `radiator`, and `waveguide_1d` endpoint targets
- parser validation now rejects incomplete promoted observable requests early
- docs and examples now show the promoted supported path
- milestone governance docs now record `v0.3.0` as active rather than merely seeded
- end-to-end facade regression coverage now covers invalid promoted element-observable requests

---

## Current recommended next patch

- `chore/v0.3.0-post-regression-bookkeeping`
- purpose: align milestone governance docs, capability wording, and handover text to the landed regression-hardened milestone state before deciding whether close-prep is next
