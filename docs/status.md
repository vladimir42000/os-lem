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
- observed green suite on the current working line: `140 passed`

Current milestone state:
- `v0.3.0` remains the released public baseline on `main`
- the opening `v0.4.0` waveguide campaign is now technically landed on the working line
- the current working line now includes lossy conical `waveguide_1d` support within a bounded scope, preserved observability on that path, one maintained hero example, and segmentation-refinement validation for the official conical example
- remaining work is primarily milestone-close and release-promotion bookkeeping, not a new physics campaign

Current recommended work type:
- align the governance/docs layer to the actual landed `v0.4.0` waveguide campaign state
- then move through a bounded close-prep / close-decision / release-promotion sequence
- do not reopen the opening waveguide campaign with unrelated capability expansion

---

## What `v0.4.0` has established on the working line

- bounded lossy conical `waveguide_1d` support is implemented
- preserved endpoint observability exists for waveguide volume velocity and particle velocity
- preserved `line_profile` observability exists for `pressure`, `volume_velocity`, and `particle_velocity`
- focused validation exists for the conical lossy boundary
- one maintained conical-line hero example exists on the working line
- segmentation-refinement validation now exists for the official conical example

What this does **not** mean yet:
- this is not a broad horn-parity claim
- this is not tapped-horn or branching-topology support
- this is not passive-radiator or multi-driver support
- this is not a product-grade frontend claim

---

## Current recommended next patch

- `chore/v0.4.0-close-prep`
- purpose: prepare the `v0.4.0` milestone for bounded close review now that the opening waveguide campaign is landed and green
