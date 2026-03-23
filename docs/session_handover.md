# Session handover

## Released baseline

The repository has a real released baseline:

- latest released version: `v0.1.0`
- released branch of record: `main`

That release remains the public floor.

---

## Current working snapshot

Observed current working branch in the uploaded repo:
- `debug/v0.2.0-hf-rolloff-fit-study`

Observed green suite on that snapshot:
- `108 passed`

Observed caveat:
- the working tree contains untracked debug/docs/frontend support files

This means the next healthy move is governance alignment plus a clean milestone restart, not broad new debugging.

---

## Current planning direction

The next intended milestone is:
- `v0.2.0`

Recommended release story:
- `offset-line observation-contract stabilization`

Current best-supported technical interpretation:
- `front/raw` is broadly credible
- the remaining mismatch is localized to `mouth/port` observable semantics
- best next move is a bounded observation-layer patch
- preferred first candidate is `mouth_directivity_only`
- `front` must remain unchanged during that patch

---

## Startup protocol for the next AI session

Read in this order:

1. `docs/doc_index.md`
2. `docs/start_here.md`
3. `docs/current_scope.md`
4. `docs/status.md`
5. `docs/milestone_charter.md`
6. `docs/release_strategy.md`
7. `docs/release_plan.md`
8. `docs/patch_registry.md`
9. `docs/next_patch.md`
10. `docs/capability_matrix.md`
11. `docs/book_contract.md`
12. `docs/frontend_api.md`

Then run:

```bash
git status
git branch --show-current
git log --oneline --decorate -n 10
pytest -q
```

Before proposing changes, reconstruct:
- released truth
- current working-line truth
- whether the user is on a debug, patch, milestone, or release branch
- whether `docs/next_patch.md` still matches reality
- exactly one bounded next patch only

---

## Important cautions

- do not restart broad debugging
- do not continue normal development directly on the long debug branch
- do not broaden post-release claims impulsively
- do not mix new capability work with broad cleanup
- preserve the discipline that produced `v0.1.0`
- treat the book as companion material, not repo truth
