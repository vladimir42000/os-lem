# Milestone charter

## Current release state

Latest completed milestone:
- `v0.2.0`

Release title:
- `offset-line observation-contract stabilization`

Status:
- released on `main`

---

## Seeded next milestone

Name:
- `v0.3.0`

Planned title:
- `waveguide observability and API maturity`

Recommended integration branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

### Intent

Use `v0.3.0` to promote already-existing observability capabilities into a cleaner supported user-facing contract, without reopening broad physics expansion.

### In scope

- expose already-available element observables through the supported API/output surface
- tighten regression coverage around line and element observability
- refresh examples and handover docs around the promoted observable set
- keep claims conservative and aligned to tested repo truth

### Out of scope

- new waveguide physics models
- conical lossy waveguide maturity work
- passive radiator roadmap growth
- multi-driver support
- frontend productization
- broad API redesign beyond the bounded observable surface

### Recommended first feature patch

- `feat/v0.3.0-element-observable-api-surface`

### Exit idea for the milestone

`v0.3.0` should close only if the promoted observability surface is documented, tested, and usable without relying on debug-only workflows.
