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
- the opening `v0.4.0` waveguide campaign is complete enough to close its execution phase on the current working line
- the current working line now includes lossy conical `waveguide_1d` support within a bounded scope, preserved observability on that path, one maintained hero example, and segmentation-refinement validation for the official conical example
- no further opening-pack physics work is required unless close review finds a concrete blocker
- remaining work is bounded release-promotion planning and later promotion execution, not another capability-expansion campaign

Current recommended work type:
- preserve the bounded `v0.4.0` working-line truth in milestone/release docs
- prepare the release-promotion plan from the current green line
- do not reopen the opening waveguide campaign without a concrete blocker

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

- `chore/v0.4.0-release-promotion-plan`
- purpose: prepare the bounded promotion/release-planning patch now that the opening `v0.4.0` waveguide campaign is closed on the working line
