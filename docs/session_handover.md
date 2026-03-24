# Session handover

## Current repo truth

- latest release: `v0.2.0`
- released on: `main`
- release title: `offset-line observation-contract stabilization`
- expected green suite on the release line: `118 passed`

## What just finished

The first post-release housekeeping patch landed, and the branch-review plan is now documented.
The repo is not ready for arbitrary new technical work yet; it still needs one explicit next-milestone seed patch.

## Startup protocol for the next session

1. start from `main`
2. run:
   - `git status`
   - `git log --oneline --decorate -n 8`
   - `pytest -q`
3. confirm the tree is clean and the release line is green
4. read:
   - `docs/post_v0_2_0_housekeeping_checklist.md`
   - `docs/post_v0_2_0_branch_review.md`
   - `docs/next_patch.md`
5. do **not** resume old debug work by default
6. do **not** open new technical scope until the next-milestone seed patch is landed

## Recommended immediate next branch

- `chore/post-v0.2.0-next-milestone-seed`
