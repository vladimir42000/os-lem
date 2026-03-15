# os-lem start here

> This file is the primary bootstrap for a new ChatGPT session.
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
- `docs/start_here.md`
- `docs/current_scope.md`
- `docs/release_strategy.md`
- `docs/release_plan.md`
- `docs/capability_matrix.md`
- `docs/next_patch.md`

2. Then ask the user to run and paste:
- `git status`
- `git branch --show-current`
- `git log --oneline --decorate -n 10`
- `pytest -q`

3. Reconstruct current repo truth from:
- those files
- git state
- current test result

4. Before proposing code:
- summarize current state
- identify the active milestone branch, if one exists
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
4. `docs/current_scope.md`
5. `docs/release_plan.md`
6. `docs/capability_matrix.md`
7. `docs/next_patch.md`
8. stable backbone docs
9. historical docs

## Current strategic posture

- project direction: open, scriptable loudspeaker LEM kernel
- current release target: `v0.1.0` foundation milestone
- immediate discipline: small validated steps
- UI ambitions are real, but deferred until kernel maturity justifies broader claims

## Current caution

Do not confuse:
- implemented subset
- validated subset
- released subset
- future target capabilities
