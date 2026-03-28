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
- accepted post-reset close-decision commit: `068d9f1`
- retained technical decision base: `7e22c0e`
- alignment checkpoint above the close decision: `b6dfc75`
- successor-milestone decision checkpoint: `c548267`
- observed suite at decision time: `140 passed`
- milestone branch of record carries the accepted close-decision state
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
11. `chore/post-v0.4.0-milestone-branch-alignment`
12. `chore/post-v0.4.0-next-milestone-decision`

---

## Active working-line milestone

Name:
- `v0.5.0`

Title:
- `opening decision`

Milestone branch:
- `milestone/v0.5.0-opening`

Status:
- active on the working line
- opened from successor-milestone decision checkpoint: `c548267`
- no routine DEV patch is frozen by this patch
- this patch adds no solver or feature scope

### Decision boundary for the active milestone

Use this patch only to open the `v0.5.0` milestone on the working line and define one milestone branch of record.
The first bounded `v0.5.0` development patch, if any, must be frozen only after the next audit reads current repo truth.

### Current milestone-control note

This file records the closed `v0.4.0` state and the active `v0.5.0` milestone opening.
It does not own the next live action and does not freeze the first routine `v0.5.0` patch.
