# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Active development milestone

- milestone: `v0.4.0`
- title: `capability expansion`
- active integration branch: `milestone/v0.4.0-capability-expansion`
- milestone focus: practical waveguide physics maturity for TL / horn workflows

Current milestone state:
- `v0.3.0` is released on `main`
- the next major work track is now `v0.4.0`, not reopened `v0.3.0`
- the first `v0.4.0` move should be a bounded seed/charter patch followed by a real waveguide-physics code campaign

Current recommended work type:
- seed `v0.4.0` explicitly in the governance/docs layer
- then open one coherent capability campaign rather than many scattered micro-patches
- keep the first code target bounded to lossy conical `waveguide_1d` maturity

---

## What `v0.3.0` established

- supported API/output surface now exposes `element_volume_velocity`
- supported API/output surface now exposes `element_particle_velocity`
- promoted contract covers `duct`, `radiator`, and `waveguide_1d` endpoint targets
- parser validation rejects incomplete promoted observable requests early
- end-to-end facade regression coverage now covers invalid promoted element-observable requests
- governance docs, handover text, release posture, and capability wording were aligned to the released `v0.3.0` repo truth

---

## Current recommended next patch

- `chore/v0.4.0-seed-waveguide-maturity`
- purpose: update the repo governance/docs layer from closed `v0.3.0` posture to active `v0.4.0` waveguide-maturity posture
