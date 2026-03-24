# os-lem status

## Released baseline

- latest released version: `v0.2.0`
- released branch of record: `main`
- observed green suite on the release line: `118 passed`

---

## Current project posture

The `v0.2.0` milestone is complete and released.
The post-release transition is sufficiently complete to open the next milestone intentionally.
The repo now has:
- release-aligned docs
- a housekeeping checklist
- a branch review / retention plan
- an explicit `v0.3.0` seed plan

Current recommended work type:
- create the seeded `v0.3.0` integration branch from `main`
- begin the first bounded `v0.3.0` feature patch
- keep the next milestone conservative until the promoted observable surface is stable

---

## What `v0.2.0` established

- `front/raw` kept unchanged
- opt-in `observable_contract: mouth_directivity_only`
- connected-aperture normalization guard for the bounded mouth path
- maintained offset-line compare harness
- conservative release-story wording aligned to tested repo truth

---

## Seeded next milestone

- `v0.3.0`
- title: `waveguide observability and API maturity`
- recommended integration branch: `milestone/v0.3.0-waveguide-observability-and-api-maturity`
- recommended first feature patch: `feat/v0.3.0-element-observable-api-surface`
