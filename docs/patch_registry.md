# Patch registry

This registry tracks the current patch pack at a human scale.

---

## Completed `v0.2.0` patch pack

1. `chore/v0.2.0-docs-reset` — landed
2. `fix/v0.2.0-mouth-directivity-only` — landed
3. `fix/v0.2.0-mouth-observable-normalization-check` — landed
4. `fix/v0.2.0-offset-line-compare-harness` — landed
5. `chore/v0.2.0-release-notes-draft` — landed
6. `chore/v0.2.0-release-candidate-close` — landed

Result:
- `v0.2.0` released on `main`
- green suite on the release line: `118 passed`

---

## Completed post-release patches

1. `chore/post-v0.2.0-housekeeping` — landed
2. `chore/post-v0.2.0-branch-review-plan` — landed
3. `chore/post-v0.2.0-next-milestone-seed` — landed

---

## Active `v0.3.0` milestone

### `v0.3.0` — `waveguide observability and API maturity`
**Status:** active

Integration branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Observed green suite on the active milestone line after the landed regression-hardened patch set:
- `128 passed`

### Completed so far

1. `feat/v0.3.0-element-observable-api-surface` — landed
2. `chore/v0.3.0-first-patch-bookkeeping` — landed
3. `test/v0.3.0-element-observable-facade-error-contract` — landed

Result so far:
- active milestone line exposes promoted element observables through the supported API/output surface
- parser-side contract hardening for the promoted observable surface is present on the milestone line
- facade negative-path regression coverage now hardens the promoted observable contract end to end
- milestone governance docs are aligned to the active milestone state through the landed regression patch set
- active milestone line remains conservative in scope
- active milestone line is green at `128 passed`

### Current planned next patch

#### `chore/v0.3.0-post-regression-bookkeeping`
**Status:** planned

Purpose:
- align milestone governance docs, capability wording, and handover text to the landed regression-hardened milestone state
- prevent future sessions from treating the already-landed regression patch as still pending

Expected scope:
- bounded governance/docs updates only
- capability wording adjustments tied directly to current tested repo truth
- no solver or API behavior changes
- no unrelated cleanup mixed into the patch
