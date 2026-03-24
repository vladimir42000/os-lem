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

These transition steps are complete, and the next milestone is active.

---

## Active next milestone

- `v0.3.0`
- planned title: `waveguide observability and API maturity`

Integration branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Landed patches on the active milestone line so far:
- `feat/v0.3.0-element-observable-api-surface`
- `chore/v0.3.0-first-patch-bookkeeping`

Observed active milestone validation after the landed patch set so far:
- `123 passed`

Recommended next regression patch:
- `test/v0.3.0-element-observable-facade-error-contract`

Planning principle for `v0.3.0`:
- promote and harden already-existing observable capabilities before adding new solver physics
- keep milestone expansion conservative until the promoted observable surface is regression-hardened end to end
