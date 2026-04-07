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

## Most recently closed working-line milestone

Name:
- `v0.5.0`

Title:
- `direct+rear reusable graph convergence`

Milestone status:
- closed on the working line
- opening checkpoint: `9766931`
- close-control checkpoint: `ca9e346`
- retained validated technical close basis: `152c7d2`
- observed suite on the retained validated technical basis: `318 passed`
- frontend impact through the validated topology chain: `No frontend contract change`
- further bounded technical patch required before close: `no`

### Intent carried by the milestone

Use `v0.5.0` to converge a bounded reusable direct+rear graph family surface with explicit observability, bounded smoke/reference coverage, bounded contribution contracts, bounded regression locks, and bounded cross-family stability checks, while keeping the stable frontend contract frozen.

### Closed scope delivered on the working line

- back-loaded-horn-class direct+rear support with bounded smoke and regression coverage
- explicit front/rear radiation-sum observability
- explicit rear-delay/path observability
- explicit front/rear contribution observability
- direct-plus-branched rear-path family with seed, smoke, contract, and regression coverage
- direct-plus-split-merge rear-path family with seed, smoke, contract, and regression coverage
- direct-plus-branched-split-merge rear-path family with seed, smoke, contract, and regression coverage
- direct-plus-branched-split-merge rear-path front-chamber throat-side coupling variant with seed, smoke, contract, and regression coverage
- bounded multi-family consistency and observability probe coverage
- bounded stability-envelope and minimal-release-surface probe coverage

### Still out of scope after milestone close

- passive radiator work
- multi-driver active architecture
- electrical-network element graph work
- broad general graph framework rewrite
- frontend/API redesign
- broad Akabak-fidelity campaign beyond bounded smoke/reference checks

---

## Active working-line milestone

Name:
- `v0.6.0`

Title:
- `bounded successor-line continuation`

Milestone status:
- opened by post-v0.5.0 control-plane decision
- predecessor close-control checkpoint: `ca9e346`
- retained validated technical basis carried into the successor line: `152c7d2`
- observed suite on the carried basis at decision time: `318 passed`
- frontend impact at opening time: `No frontend contract change`

### Intent carried by the milestone

Use `v0.6.0` to continue from the validated `v0.5.0` surface only through one exact bounded technical patch at a time, after an explicit AUDIT names that patch, while preserving the frozen frontend contract and avoiding silent post-close scope drift.

### Guard rails carried by the milestone

- do not open technical growth blindly
- do not treat this decision as authorization for a new topology family by default
- do not broaden into passive radiator work, multi-driver active architecture, electrical-network element graph work, solver redesign, API/frontend redesign, or repo-wide cleanup unless a later control-plane decision opens that scope explicitly
- keep the single live next action in `docs/next_patch.md`
