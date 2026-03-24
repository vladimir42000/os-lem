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

## Completed `v0.3.0` milestone

### `v0.3.0` — `waveguide observability and API maturity`
**Status:** complete on milestone branch

Milestone branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Observed green suite on the milestone close-decision line:
- `128 passed`

### Completed patch pack

1. `feat/v0.3.0-element-observable-api-surface` — landed
2. `chore/v0.3.0-first-patch-bookkeeping` — landed
3. `test/v0.3.0-element-observable-facade-error-contract` — landed
4. `chore/v0.3.0-post-regression-bookkeeping` — landed
5. `chore/v0.3.0-close-prep` — landed

Result:
- milestone line exposes promoted element observables through the supported API/output surface
- parser-side contract hardening for the promoted observable surface is present on the milestone line
- facade negative-path regression coverage hardens the promoted observable contract end to end
- governance docs, handover text, release posture, and capability wording are aligned to the current regression-hardened state
- milestone line remained conservative in scope throughout the patch pack
- milestone line is green at `128 passed`

### Default next step

- no further `v0.3.0` patch is planned by default
- any continuation should be explicit release-promotion planning or later next-milestone seeding, not reopened `v0.3.0` scope
