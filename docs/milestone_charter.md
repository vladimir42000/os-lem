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
- `v0.5.0` opening checkpoint: `9766931`
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
13. `chore/v0.5.0-opening-decision`

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
- working-line opening checkpoint: `9766931`
- first routine patch frozen by this patch: `chore/v0.5.0-seed-branching-topology`
- first routine patch boundary: minimal branching / recombination topology opening for tapped-horn-class graphs
- this decision patch adds no solver or feature scope by itself

### Decision boundary for the active milestone

Use this patch only to freeze the first routine `v0.5.0` patch as a minimal branching / recombination topology opening.
Do not broaden that first routine patch into passive radiator work, multi-driver active architecture, electrical-network element graph work, or broad frontend / API work.

### Current milestone-control note

This file records the closed `v0.4.0` state, the active `v0.5.0` milestone opening, and the single frozen first routine patch.
It does not own the next live action beyond naming that single next patch.
