# Milestone charter

## Current release state

Latest completed release:
- `v0.3.0`

Release title:
- `waveguide observability and API maturity`

Status:
- released on `main`

---

## Current active milestone

Name:
- `v0.4.0`

Title:
- `capability expansion`

Milestone branch:
- `milestone/v0.4.0-capability-expansion`

Status:
- active
- opened from the released `v0.3.0` line on `main`
- opening waveguide campaign technically landed on the current working line

### Intent

Use `v0.4.0` to push os-lem from a narrow released waveguide baseline toward the first practically useful Akabak-like TL / horn workflow.

### In scope

- waveguide physics maturity for practical TL / horn workflows
- lossy conical `waveguide_1d` support within a clearly documented boundary
- preserved observability on the new waveguide path
- focused validation for the new supported boundary
- one maintained hero example tied directly to the new capability
- segmentation-refinement validation for the official conical example

### Out of scope for the opening milestone patch pack

- passive radiator support
- true multi-driver active architecture
- electrical-network element graph work
- branching / recombination topology for tapped-horn-class graphs
- broad GUI/frontend work
- broad API redesign unrelated to the waveguide campaign

### Landed opening patch sequence on the working line

1. `chore/v0.4.0-seed-waveguide-maturity`
2. `feat/v0.4.0-conical-lossy-waveguide-mvp`
3. `test/v0.4.0-conical-lossy-waveguide-validation`
4. `chore/v0.4.0-waveguide-example-refresh`
5. `test/v0.4.0-conical-segmentation-refinement`
6. `chore/v0.4.0-post-waveguide-bookkeeping`

### Remaining bounded close sequence

1. `chore/v0.4.0-close-prep`
2. `chore/v0.4.0-close-decision`
3. `chore/v0.4.0-release-promotion-plan`

### Exit idea for the milestone

`v0.4.0` should close only if os-lem can honestly claim a first practically useful lossy conical waveguide workflow with preserved observability, bounded validation, at least one maintained example, and completed segmentation-refinement validation for the official reference case.
