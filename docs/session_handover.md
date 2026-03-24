# Session handover

## Current repo truth

- latest release: `v0.2.0`
- released on: `main`
- release title: `offset-line observation-contract stabilization`
- expected green suite on the release line: `118 passed`

## What just finished

Post-release housekeeping and branch-review planning have been carried far enough that the next milestone is now seeded explicitly.
Future sessions should no longer improvise the next milestone from old `v0.2.0` branches or debug notes.

## Startup protocol for the next session

1. start from `main`
2. run:
   - `git status`
   - `git log --oneline --decorate -n 8`
   - `pytest -q`
3. confirm the tree is clean and the release line is green
4. read:
   - `docs/v0_3_0_seed_plan.md`
   - `docs/next_patch.md`
   - `docs/post_v0_2_0_branch_review.md`
5. create the recommended integration branch from `main`
6. open the first bounded `v0.3.0` feature patch
7. do **not** resume old debug work by default

## Recommended immediate next branches

Integration branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

First feature branch:
- `feat/v0.3.0-element-observable-api-surface`
