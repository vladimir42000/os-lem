# Session handover

## Branches of record

Integration branch:
- `milestone/v0.1.0-foundation`

Current docs-alignment patch branch at the time of this handover:
- `chore/v0.1.0-docs-alignment`

Recent governance patch branch already integrated into the milestone:
- `chore/release-governance`

Important historical debug lineage:
- `debug/closed-box-mismatch`
- `debug/closed-box-radiator-fix`
- `debug/bassreflex-radiation-space`

---

## Current repo truth

The project now has an explicit release spine:

- `main` is reserved for released/stable history
- `milestone/v0.1.0-foundation` is the integration branch for the first real release
- short-lived patch branches should branch from the current milestone
- release planning is now defined by:
  - `docs/release_strategy.md`
  - `docs/release_plan.md`
  - `docs/capability_matrix.md`

Current known green suite on the development line:
- `104 passed`

---

## Current validated foundation

The current milestone already includes:

- corrected sealed-box baffled-radiator Struve behavior
- corrected bass-reflex SPL observation `radiation_space` behavior
- corrected `ts_classic` canonical `Bl` normalization
- minimal assembled `waveguide_1d`
- current minimal waveguide endpoint/profile observability subset
- minimal cylindrical distributed loss for `waveguide_1d` within the frozen cylindrical-loss boundary
- provisional `os_lem.api` facade

This is enough to justify a first honest release target, but not enough to justify broad external parity or broad product claims.

---

## Immediate next patch after this docs patch

After the current docs-alignment patch is merged, the next bounded patch should be:

- preserve maintained validation/example assets cleanly
- keep their status explicit as example/prototype/validation-oriented
- avoid broadening kernel/API/product claims

Suggested next patch branch:
- `chore/v0.1.0-preserve-validation-examples`

---

## Startup protocol for the next AI session

Read in this order:

1. `docs/start_here.md`
2. `docs/current_scope.md`
3. `docs/release_strategy.md`
4. `docs/release_plan.md`
5. `docs/capability_matrix.md`
6. `docs/next_patch.md`
7. `docs/frontend_api.md`

Then run:

```bash
git status
git branch --show-current
git log --oneline --decorate -n 10
pytest -q
```

Before proposing changes, reconstruct:

- current repo truth
- current milestone posture
- whether `docs/next_patch.md` still matches reality
- one bounded next patch only

---

## Important cautions

- do not develop directly on `main`
- do not confuse implemented subset with released subset
- do not overstate Hornresp/AkAbak parity
- do not freeze broad transmission-line claims prematurely
- do not mix example preservation with kernel redesign
- keep patches small and reviewable
