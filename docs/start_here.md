# os-lem start here

> This file is the primary bootstrap for a new development session.
> Read this first.
> Do not start coding immediately.

## Session startup role

The assistant must begin as:
- project manager
- technical reviewer
- patch planner first

Not as immediate coder.

## Required startup protocol

1. Read:
- `docs/doc_index.md`
- `docs/start_here.md`
- `docs/current_scope.md`
- `docs/status.md`
- `docs/milestone_charter.md`
- `docs/release_strategy.md`
- `docs/release_plan.md`
- `docs/patch_registry.md`
- `docs/next_patch.md`
- `docs/capability_matrix.md`
- `docs/book_contract.md`

2. Then inspect the live repo with:
- `git status`
- `git branch --show-current`
- `git log --oneline --decorate -n 10`
- `pytest -q`

3. Reconstruct current repo truth from:
- those files
- git state
- current test result
- current branch lineage

4. Before proposing code:
- summarize current state
- separate released truth from working-line truth
- identify whether the current branch is a release branch, milestone branch, patch branch, or debug branch
- verify whether `docs/next_patch.md` still matches repo reality
- recommend exactly one bounded next patch only

## Rules

- repo is source of truth
- one patch = one purpose
- no broad refactor
- no speculative architecture changes
- no changes outside agreed scope
- tests must stay green
- docs must stay aligned with actual repo state
- no coding before the next patch objective is frozen

## Priority order of truth

1. current tested repo state
2. current branch and commits
3. current milestone branch, if one exists
4. governance docs
5. stable technical docs
6. debug archive docs
7. book companion
8. old chat memory

## Current strategic posture

- latest released version: `v0.1.0`
- current active planning target: `v0.2.0`
- current `v0.2.0` release story: `offset-line observation-contract stabilization`
- immediate discipline: small validated steps
- book is useful, but it is not repo truth

## Current caution

Do not confuse:
- implemented subset
- validated subset
- released subset
- debug conclusions on the working line
- future target capabilities

## Current best-supported next move

The current repo interpretation from the recent debug period is:
- `front/raw` is broadly credible
- remaining mismatch is localized to `mouth/port` observable semantics
- best next move is one bounded observation-layer development patch
- current preferred candidate is `mouth_directivity_only`
- `front` must remain unchanged during that patch
