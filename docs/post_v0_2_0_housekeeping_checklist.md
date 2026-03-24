# Post-v0.2.0 housekeeping checklist

Use this after the `v0.2.0` release to leave the repo in a clean state.

## Documentation

- [ ] verify README states `v0.2.0` as the latest release
- [ ] verify `docs/status.md` no longer treats `v0.2.0` as in-progress
- [ ] verify repo/book reciprocal links are present and correct

## Branch review

- [ ] decide when to retire `milestone/v0.2.0-offset-line-observation`
- [ ] review whether stale `milestone/v0.2.0-line-truth` should be deleted or archived
- [ ] review old `debug/*` branches and keep only those still worth preserving as historical evidence

## Tag review

- [ ] keep `v0.2.0`
- [ ] review whether older local-only safety tags should remain only locally or be documented elsewhere
- [ ] avoid bulk tag cleanup mixed into technical development patches

## Handover

- [ ] confirm future sessions start from `main`
- [ ] confirm next-milestone planning happens only after housekeeping is landed
