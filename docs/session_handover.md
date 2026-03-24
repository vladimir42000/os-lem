# Session handover

## Current repo truth

- latest release: `v0.2.0`
- released on: `main`
- release title: `offset-line observation-contract stabilization`
- observed green suite on the release line: `118 passed`

Active development milestone:
- `v0.3.0` — `waveguide observability and API maturity`
- integration branch: `milestone/v0.3.0-waveguide-observability-and-api-maturity`
- observed green suite on the active milestone line after the first landed patch: `123 passed`

## What just finished

The seeded `v0.3.0` milestone has now been opened intentionally.
The first bounded milestone patch, `feat/v0.3.0-element-observable-api-surface`, has landed on the milestone line.
Future sessions should continue from the active milestone branch rather than reopening the milestone from `main`.

## Startup protocol for the next session

1. start from `milestone/v0.3.0-waveguide-observability-and-api-maturity`
2. run:
   - `git branch --show-current`
   - `git status --short`
   - `git log --oneline --decorate -n 8`
   - `pytest -q`
3. confirm the tree is clean and the active milestone line is green
4. read:
   - `docs/status.md`
   - `docs/next_patch.md`
   - `docs/patch_registry.md`
   - `docs/session_handover.md`
   - `docs/v0_3_0_seed_plan.md`
   - `docs/release_plan.md`
   - `docs/doc_index.md`
5. open the next bounded patch from the active milestone branch
6. do **not** resume old debug work by default
7. do **not** widen milestone scope by default

## Recommended immediate next branches

Integration branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Current bookkeeping branch:
- `chore/v0.3.0-first-patch-bookkeeping`
