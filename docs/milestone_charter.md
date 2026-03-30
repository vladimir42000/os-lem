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

---

## Active working-line milestone

Name:
- `v0.5.0`

Title:
- `tapped-horn topology seeding`

Milestone status:
- active on the working line
- opening checkpoint: `9766931`
- latest explicit frontend checkpoint: `81727af854207ccc94eeeede26988c688571cb30`
- current accepted working commit: `aa1a238c618f1f64fa4cc9f243b04f81d3ccf4db`
- observed suite on the current accepted working line: `193 passed`
- frontend impact through the current accepted topology chain: `No frontend contract change`

### Intent carried by the active milestone

Use `v0.5.0` to open bounded tapped-horn-class topology capabilities incrementally, validate them against bounded Akabak reference cases, and keep the stable frontend contract frozen unless a later patch explicitly updates it.

### Landed topology chain carried by the current accepted working line

1. `chore/v0.5.0-seed-branching-topology`
2. `chore/v0.5.0-seed-junction-topology`
3. `chore/v0.5.0-seed-branched-horn-skeleton`
4. `test/v0.5.0-branched-horn-akabak-reference-smoke`
5. `feat/v0.5.0-seed-recombination-topology`
6. `feat/v0.5.0-seed-split-merge-horn-skeleton`
7. `feat/v0.5.0-seed-tapped-driver-skeleton`
8. `feat/v0.5.0-seed-offset-tap-topology`
9. `feat/v0.5.0-freeze-frontend-contract-v1`
10. `feat/v0.5.0-seed-rear-chamber-tapped-skeleton`
11. `test/v0.5.0-rear-chamber-tapped-akabak-reference-smoke`
12. `feat/v0.5.0-seed-rear-chamber-port-injection-topology`
13. `feat/v0.5.0-seed-throat-chamber-topology`
14. `feat/v0.5.0-seed-blind-throat-side-segment`

### Delivered bounded capabilities so far within `v0.5.0`

- parallel split/recombine bundles between the same two acoustic nodes
- one true interior acoustic junction
- one minimal branched horn skeleton
- one bounded recombination case
- one dual-junction split/merge horn skeleton
- one bounded tapped-driver skeleton
- one bounded offset-tap topology
- one bounded rear-chamber tapped skeleton
- one bounded rear-chamber port-injection topology
- one bounded throat-chamber topology
- one bounded blind throat-side horn segment
- bounded Akabak smoke comparison paths for the currently supported branched and rear-chamber tapped structures

### Still explicitly out of scope within `v0.5.0`

- passive radiator work
- multi-driver active architecture
- electrical-network element graph work
- broad general graph framework rewrite
- frontend/API redesign
- broad Akabak-fidelity campaign beyond bounded smoke/reference checks

### Current milestone-control note

This file records the active `v0.5.0` milestone against the current accepted working line.
It does not own the next live action; that remains singularly tracked in `docs/next_patch.md`.
