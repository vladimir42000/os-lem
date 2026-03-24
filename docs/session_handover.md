# Session handover

## Current repo truth

- latest release: `v0.2.0`
- released on: `main`
- release title: `offset-line observation-contract stabilization`
- observed green suite on the release line: `118 passed`

Completed milestone branch:
- `v0.3.0` — `waveguide observability and API maturity`
- milestone branch: `milestone/v0.3.0-waveguide-observability-and-api-maturity`
- observed green suite on the milestone close-decision line: `128 passed`

## What just finished

The `v0.3.0` milestone patch pack has been completed on the milestone branch.
The branch is green, the promoted observable surface is regression-hardened, and the milestone governance/docs layer is aligned to that state.
Future sessions should not reopen `v0.3.0` milestone scope by default.

## Startup protocol for the next session

1. decide first whether the session is about release-promotion work or unrelated new work
2. if the session is about `v0.3.0` release-promotion work, start from `milestone/v0.3.0-waveguide-observability-and-api-maturity`
3. run:
   - `git branch --show-current`
   - `git status --short`
   - `git log --oneline --decorate -n 8`
   - `pytest -q`
4. confirm the tree is clean and the milestone branch is green
5. read:
   - `docs/status.md`
   - `docs/next_patch.md`
   - `docs/patch_registry.md`
   - `docs/session_handover.md`
   - `docs/release_plan.md`
   - `docs/change_log.md`
   - `docs/doc_index.md`
6. do **not** resume old debug work by default
7. do **not** reopen closed `v0.3.0` scope by default

## Recommended immediate next branches

Current completed milestone branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Default next patch:
- none inside closed `v0.3.0`

If explicit continuation is requested:
- choose a bounded release-promotion planning branch rather than another `v0.3.0` feature/regression patch
