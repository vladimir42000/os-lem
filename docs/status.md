# os-lem status

## Released baseline

- latest released version: `v0.2.0`
- released branch of record: `main`
- observed green suite on the release line: `118 passed`

---

## Current milestone close decision

- milestone: `v0.3.0`
- title: `waveguide observability and API maturity`
- milestone branch of record: `milestone/v0.3.0-waveguide-observability-and-api-maturity`
- observed green suite on the milestone close-decision line: `128 passed`

Close decision:
- `v0.3.0` is complete on the milestone branch
- no further `v0.3.0` feature, regression, or bookkeeping patch is required by default
- `main` remains the released `v0.2.0` line until an explicit promotion / release action is chosen

Current recommended work type:
- if work continues from here, treat it as bounded release-promotion planning rather than additional `v0.3.0` scope growth
- do not reopen broad solver debugging or broad API redesign
- do not reopen closed milestone scope by default

---

## What `v0.2.0` established

- `front/raw` kept unchanged
- opt-in `observable_contract: mouth_directivity_only`
- connected-aperture normalization guard for the bounded mouth path
- maintained offset-line compare harness
- conservative release-story wording aligned to tested repo truth

---

## What `v0.3.0` established

- supported API/output surface now exposes `element_volume_velocity`
- supported API/output surface now exposes `element_particle_velocity`
- promoted contract covers `duct`, `radiator`, and `waveguide_1d` endpoint targets
- parser validation rejects incomplete promoted observable requests early
- docs and examples show the promoted supported path
- end-to-end facade regression coverage now covers invalid promoted element-observable requests
- capability wording reflects the promoted facade element-observable surface as validated on the milestone line
- milestone governance docs, handover text, and release posture are aligned to the current regression-hardened repo truth

---

## Current recommended next patch

- none by default inside closed `v0.3.0`
- if explicit continuation is requested, open a bounded release-promotion planning patch rather than reopening milestone scope
