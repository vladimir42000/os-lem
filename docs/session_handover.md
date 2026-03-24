# Session handover

## Released baseline

The repository has a real released baseline:

- latest released version: `v0.1.0`
- released branch of record: `main`

That release remains the public floor.

---

## Current working snapshot

Current active integration branch:
- `milestone/v0.2.0-offset-line-observation`

Current bounded development patch branch:
- `fix/v0.2.0-mouth-directivity-only`

Observed green suite on this patch snapshot:
- `114 passed`

Observed local-workflow caveat:
- unrelated scratch/debug/frontend files should remain stashed or untracked and must not be mixed into bounded patch branches

---

## Current planning direction

The current milestone is:
- `v0.2.0`

Current release story:
- `offset-line observation-contract stabilization`

Current best-supported technical interpretation:
- `front/raw` remains broadly credible
- the remaining mismatch is localized to `mouth/port` observable semantics
- the `mouth_directivity_only` candidate is now implemented as an opt-in observation-layer contract
- that contract is available for passive `spl` observations and term-level `spl_sum` usage
- the patch intentionally rejects driver-front use of `mouth_directivity_only`
- the likely remaining issue is now a narrow mouth-path amplitude / area / normalization residual

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
- current milestone truth
- whether the user is on the milestone branch or a bounded patch branch
- whether `docs/next_patch.md` still matches reality
- exactly one bounded next patch only

---

## Important cautions

- do not restart broad debugging
- do not merge to `main` before the milestone exit criteria are actually met
- do not broaden post-release claims impulsively
- do not mix new capability work with broad cleanup
- preserve the discipline that produced `v0.1.0`
- treat the book as companion material, not repo truth
