# Release plan

## Latest completed release

- `v0.2.0`
- title: `offset-line observation-contract stabilization`
- release branch of record: `main`

Observed release-line validation at close:
- `118 passed`

---

## What is complete

`v0.2.0` is released.
The release package includes:
- bounded mouth/port observation candidate support
- normalization guard
- compare harness
- release notes and release checklist
- conservative capability wording aligned to the tested repo state

---

## Post-release transition

The post-release transition was intentionally split into:
1. housekeeping patch
2. branch review / retention plan
3. next-milestone seed patch

These transition steps are now complete enough that the next milestone can begin intentionally.

---

## Seeded next milestone

- `v0.3.0`
- planned title: `waveguide observability and API maturity`

Recommended integration branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Recommended first feature patch:
- `feat/v0.3.0-element-observable-api-surface`

Planning principle for `v0.3.0`:
- promote and harden already-existing observable capabilities before adding new solver physics
