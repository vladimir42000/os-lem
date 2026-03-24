# Session handover

## Current repo truth

- latest release: `v0.2.0`
- released on: `main`
- release title: `offset-line observation-contract stabilization`
- expected green suite on the release line: `118 passed`

## What just finished

The long observation/debug cycle was converted into a bounded release sequence and shipped.
The milestone branch is no longer the primary source of truth; `main` now is.

## Startup protocol for the next session

1. start from `main`
2. run:
   - `git status`
   - `git log --oneline --decorate -n 8`
   - `pytest -q`
3. confirm the tree is clean and the release line is green
4. do **not** resume old debug work by default
5. do **not** reopen `v0.2.0` technical scope unless a specific post-release issue is proven

## Recommended immediate next branch

- `chore/post-v0.2.0-housekeeping`

## After housekeeping

Only then define the next milestone branch and next technical patch pack.
