# Session handover

## Released baseline

The repository now has a real released baseline:

- latest released version: `v0.1.0`
- released branch of record: `main`

That release was cut after:

- governance docs were introduced
- milestone structure was formalized
- milestone docs were aligned to repo truth
- validation/example assets were preserved
- release metadata and release notes were prepared

Current known green suite on the released baseline:
- `104 passed`

---

## Branch posture after the first release

- `main` is now the stable/released branch
- `milestone/v0.1.0-foundation` remains as historical integration lineage
- new work should not continue on the old `v0.1.0` milestone branch
- the next release cycle should start from `main`

---

## Current planning direction

The next planned target is:

- `v0.2.0`

That target should begin conservatively.

Recommended opening move:
- create a `v0.2.0` milestone branch
- run one bounded line / offset-line truth-finding investigation
- decide from evidence whether the next claim is:
  - support already present
  - partial support
  - unsupported

Do not jump directly to broad transmission-line implementation claims.

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

- current released baseline
- whether the user is working from `main` or a child branch
- whether `docs/next_patch.md` still matches reality
- one bounded next patch only

---

## Important cautions

- do not continue normal development on `milestone/v0.1.0-foundation`
- do not broaden post-release claims impulsively
- do not mix new capability work with broad cleanup
- preserve the release discipline that produced `v0.1.0`
