# Post-v0.2.0 housekeeping checklist

Use this after the `v0.2.0` release to leave the repo in a clean state.

## Documentation

- [x] verify README states `v0.2.0` as the latest release
- [x] verify `docs/status.md` no longer treats `v0.2.0` as in-progress
- [x] verify repo/book reciprocal links are present and correct

## Branch review

- [x] add an explicit branch review document: `docs/post_v0_2_0_branch_review.md`
- [ ] decide when to retire `milestone/v0.2.0-offset-line-observation`
- [ ] review whether stale `milestone/v0.2.0-line-truth` should be deleted or archived
- [ ] review old `debug/*` branches and keep only those still worth preserving as historical evidence

## Tag review

- [x] keep `v0.2.0`
- [ ] review whether older local-only safety tags should remain only locally or be documented elsewhere
- [ ] avoid bulk tag cleanup mixed into technical development patches

## Handover

- [x] confirm future sessions start from `main`
- [x] confirm the next milestone seed patch is prepared before opening a new technical milestone
- [x] document the seeded next milestone and first recommended feature branch

## Exit note

Housekeeping is complete enough to resume bounded next-milestone work.
Any further branch/tag pruning can happen in a dedicated later cleanup session.
