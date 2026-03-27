# Milestone charter

## Current release state

Latest completed release:
- `v0.3.0`

Release title:
- `waveguide observability and API maturity`

Status:
- released on `main`

---

## Most recent completed working-line milestone

Name:
- `v0.4.0`

Title:
- `capability expansion`

Milestone branch:
- `milestone/v0.4.0-capability-expansion`

Status:
- closed on the working line after post-reset revalidation
- decision base: `7e22c0e`
- observed suite at decision time: `140 passed`
- not a release claim by itself

### Intent carried by the milestone

Use `v0.4.0` to push os-lem from a narrow released waveguide baseline toward the first practically useful Akabak-like TL / horn workflow.

### Closed scope delivered on the working line

- waveguide physics maturity for practical TL / horn workflows within the milestone boundary
- lossy conical `waveguide_1d` support within a clearly documented boundary
- preserved observability on the new waveguide path
- focused validation for the new supported boundary
- one maintained hero/example path on the live repo line
- segmentation-refinement validation for the official conical example

### Still out of scope after milestone close

- passive radiator support
- true multi-driver active architecture
- electrical-network element graph work
- branching / recombination topology for tapped-horn-class graphs
- broad GUI/frontend work
- broad API redesign unrelated to the landed waveguide campaign

### Landed opening patch sequence retained as historical context

1. `chore/v0.4.0-seed-waveguide-maturity`
2. `feat/v0.4.0-conical-lossy-waveguide-mvp`
3. `test/v0.4.0-conical-lossy-waveguide-validation`
4. `chore/v0.4.0-waveguide-example-refresh`
5. `test/v0.4.0-conical-segmentation-refinement`
6. `chore/v0.4.0-post-waveguide-bookkeeping`
7. `chore/v0.4.0-close-prep`
8. `chore/v0.4.0-close-decision`
9. `chore/v0.4.0-dev-cycle-reset`
10. `chore/v0.4.0-post-reset-close-decision`

### Current milestone-control note

This file records the closed `v0.4.0` milestone state only.
It does not open a successor milestone and does not own the next live action.
