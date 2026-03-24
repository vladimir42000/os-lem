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
- observed green suite on the active milestone line after the first landed patch: `123 passed`

Current milestone state:
- the seeded `v0.3.0` integration branch is now open
- the first bounded `v0.3.0` feature patch has landed on the milestone line
- the milestone should remain intentionally conservative until the promoted observable surface is fully documented and stabilized

Current recommended work type:
- do a bounded bookkeeping/docs patch that records the landed first patch honestly
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

## What the first `v0.3.0` patch established

- supported API/output surface now exposes `element_volume_velocity`
- supported API/output surface now exposes `element_particle_velocity`
- promoted contract covers `duct`, `radiator`, and `waveguide_1d` endpoint targets
- parser validation now rejects incomplete promoted observable requests early
- docs and examples now show the promoted supported path

---

## Current recommended next patch

- `chore/v0.3.0-first-patch-bookkeeping`
- purpose: align milestone docs, release planning, and handover text to the actual landed first `v0.3.0` patch
