# v0.3.0 seed plan

## Milestone

- Name: `v0.3.0`
- Planned title: `waveguide observability and API maturity`
- Recommended integration branch: `milestone/v0.3.0-waveguide-observability-and-api-maturity`

## Why this is the right successor to `v0.2.0`

`v0.2.0` intentionally solved a bounded observation-contract problem without reopening broad solver development.
The most conservative honest next step is therefore not new physics first, but promotion of already-existing observability capabilities into a cleaner supported user-facing contract.

## Planned release intent

Use `v0.3.0` to make waveguide and element observability more usable from the supported API/output surface, with stronger regression coverage and clearer examples.

## In scope

- promote existing element observables to the supported API/output layer
- tighten output-contract wording and regression tests around line and element observability
- refresh examples and handover docs to show the supported path
- keep milestone claims conservative and tied to tested repo truth

## Out of scope

- new solver-core physics
- conical lossy waveguide maturity work
- passive radiator roadmap growth
- multi-driver support
- frontend productization
- broad API redesign unrelated to the promoted observable surface

## First bounded patch recommendation

### Branch
- `feat/v0.3.0-element-observable-api-surface`

### Goal
Expose already-existing element observables such as volume velocity and particle velocity through the supported API/output surface without changing default existing behaviors.

### Patch boundary
Allowed:
- bounded API/output-surface changes
- narrow regression coverage
- small example/doc refresh tied directly to the promoted observable surface

Not allowed:
- new acoustical models
- topology growth
- broad refactors
- branch cleanup mixed into the feature patch

## Suggested first patch pack

1. `feat/v0.3.0-element-observable-api-surface`
2. `test/v0.3.0-element-observable-regressions`
3. `chore/v0.3.0-example-and-doc-refresh`

## Exit idea for `v0.3.0`

The milestone should close only if the promoted observability surface is:
- reachable through the supported API/output path
- covered by regression tests
- documented without requiring debug-only scripts to understand normal usage
