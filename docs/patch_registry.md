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

## Seeded next milestone

### `v0.3.0` — `waveguide observability and API maturity`
**Status:** seeded

Recommended integration branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

### Current planned first feature patch

#### `feat/v0.3.0-element-observable-api-surface`
**Status:** planned

Purpose:
- begin `v0.3.0` with a conservative promotion of already-existing element observables
- expose them through the supported API/output surface
- avoid drifting immediately into broader physics expansion

Expected scope:
- bounded API/output-surface work
- narrow regression coverage
- small doc/example refresh only
