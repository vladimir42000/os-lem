# Session handover

## Current repo truth

- latest release: `v0.3.0`
- released on: `main`
- release title: `waveguide observability and API maturity`
- observed green suite on the release line: `128 passed`

Active development milestone:
- `v0.4.0` — `capability expansion`
- integration branch: `milestone/v0.4.0-capability-expansion`
- observed green suite on the current working line: `140 passed`

## What just changed

The opening `v0.4.0` waveguide campaign is now landed on the working line.
That working line now includes:
- bounded lossy conical `waveguide_1d` support
- preserved endpoint and line-profile observability on that path
- focused conical-loss validation
- one maintained conical-line hero example
- segmentation-refinement validation for the official conical example

## What not to do next

Do **not** reopen the opening waveguide campaign with unrelated capability work.
Do **not** mix passive radiator, multi-driver, branching topology, or broad frontend work into the next patch.
Do **not** treat working-line validation as a broad external parity claim.

## Required startup steps for the next session

1. start from `milestone/v0.4.0-capability-expansion`
2. inspect the live repo first with:
   - `git branch --show-current`
   - `git status --short`
   - `git log --oneline --decorate -n 12`
   - `pytest -q`
3. read:
   - `docs/start_here.md`
   - `docs/status.md`
   - `docs/milestone_charter.md`
   - `docs/release_plan.md`
   - `docs/next_patch.md`
   - `docs/patch_registry.md`
4. freeze exactly one bounded next patch before coding

## Recommended next patch

- `chore/v0.4.0-close-prep`

Purpose:
- prepare the `v0.4.0` milestone for bounded close review now that the opening waveguide campaign is landed and green

Immediate intended follow-up after that:
- `chore/v0.4.0-close-decision`
- `chore/v0.4.0-release-promotion-plan`
