# v0.3.0 seed plan

## Milestone

- Name: `v0.3.0`
- Planned title: `waveguide observability and API maturity`
- Recommended integration branch: `milestone/v0.3.0-waveguide-observability-and-api-maturity`

## Current state

- Status: active
- Integration branch is open
- First bounded patch landed: `feat/v0.3.0-element-observable-api-surface`
- Observed green suite on the active milestone line after the first landed patch: `123 passed`

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

## First bounded patch

### Branch
- `feat/v0.3.0-element-observable-api-surface`

### Status
- landed on the active milestone line

### Delivered intent
- exposed already-existing element observables such as volume velocity and particle velocity through the supported API/output surface without changing default existing behaviors

## Suggested next bounded patch

1. `chore/v0.3.0-first-patch-bookkeeping`
2. next bounded milestone follow-up to be chosen after bookkeeping lands

## Exit idea for `v0.3.0`

The milestone should close only if the promoted observability surface is:
- reachable through the supported API/output path
- covered by regression tests
- documented without requiring debug-only scripts to understand normal usage
