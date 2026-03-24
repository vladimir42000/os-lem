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

Observed green suite on the active milestone line after the first landed patch:
- `123 passed`

### Completed so far

1. `feat/v0.3.0-element-observable-api-surface` — landed

Result so far:
- active milestone line exposes promoted element observables through the supported API/output surface
- active milestone line remains conservative in scope
- active milestone line is green at `123 passed`

### Current planned next patch

#### `chore/v0.3.0-first-patch-bookkeeping`
**Status:** planned

Purpose:
- align milestone docs, release planning, and handover text to the actual landed first `v0.3.0` patch
- prevent future sessions from treating `v0.3.0` as only a seed state

Expected scope:
- bounded governance/docs updates only
- no solver or API behavior changes
- no unrelated cleanup mixed into the patch
