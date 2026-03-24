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
- observed green suite on the active milestone line after the first landed patch set: `123 passed`

Current milestone state:
- the seeded `v0.3.0` integration branch is open and active
- the first bounded `v0.3.0` feature patch has landed on the milestone line
- the first bounded `v0.3.0` bookkeeping patch has also landed on the milestone line
- the milestone should remain intentionally conservative until the promoted observable surface is regression-hardened and fully settled

Current recommended work type:
- choose the next technical step from the active milestone branch, not from old seed-state docs
- keep the next technical step narrow and regression-led
- do not reopen broad solver debugging or broad API redesign

---

## What `v0.2.0` established

- `front/raw` kept unchanged
- opt-in `observable_contract: mouth_directivity_only`
- connected-aperture normalization guard for the bounded mouth path
- maintained offset-line compare harness
- conservative release-story wording aligned to tested repo truth

---

## What the first `v0.3.0` patch set established

- supported API/output surface now exposes `element_volume_velocity`
- supported API/output surface now exposes `element_particle_velocity`
- promoted contract covers `duct`, `radiator`, and `waveguide_1d` endpoint targets
- parser validation now rejects incomplete promoted observable requests early
- docs and examples now show the promoted supported path
- milestone governance docs now record `v0.3.0` as active rather than merely seeded

---

## Current recommended next patch

- `test/v0.3.0-element-observable-facade-error-contract`
- purpose: add end-to-end negative-path regression coverage for the promoted element-observable facade contract without changing solver physics or broad API scope
