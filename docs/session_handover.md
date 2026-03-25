# Session handover

## Current repo truth

- latest release: `v0.3.0`
- released on: `main`
- release title: `waveguide observability and API maturity`
- observed green suite on the release line: `128 passed`

Active development milestone:
- `v0.4.0` — `capability expansion`
- integration branch: `milestone/v0.4.0-capability-expansion`
- first intended capability campaign: waveguide physics maturity for practical TL / horn workflows

## What just changed

`v0.3.0` has been released and should not be reopened by default.
The next major work now belongs to `v0.4.0`.
The opening `v0.4.0` move should be a bounded seed/charter patch, followed immediately by the first real code campaign.

## Startup protocol for the next session

1. start from `milestone/v0.4.0-capability-expansion`
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
   - `docs/release_plan.md`
   - `docs/change_log.md`
   - `docs/doc_index.md`
   - `docs/milestone_charter.md`
5. open the next bounded patch from the active milestone branch
6. do **not** resume old `v0.3.0` work by default
7. do **not** broaden the opening `v0.4.0` patch beyond the waveguide campaign

## Recommended immediate next branches

Integration branch:
- `milestone/v0.4.0-capability-expansion`

Recommended next patch branch:
- `chore/v0.4.0-seed-waveguide-maturity`

Recommended first technical patch after that:
- `feat/v0.4.0-conical-lossy-waveguide-mvp`
