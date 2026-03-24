# Session handover

## Current branch of truth

- Active milestone branch: `milestone/v0.2.0-offset-line-observation`
- `main` remains untouched by the in-progress `v0.2.0` line

## Current milestone state

The `v0.2.0` line is now in **release-candidate** posture.

Landed milestone spine:

1. docs/governance reset
2. `mouth_directivity_only` observation contract
3. mouth observable normalization guard
4. offset-line compare harness
5. `v0.2.0` release-notes draft

## Validation state

- test suite expected state on the milestone line: `118 passed`
- compare harness exists for offset-line observation comparison
- release notes exist as a draft, not yet as a published release artifact

## Operator rule for next sessions

Start from the milestone branch and treat the repository as a **release-candidate**,
not as a free-form debug branch.

The next action is a release decision unless a very small, explicit close patch is
still justified.

## What not to do

- do not reopen broad debugging
- do not restore unrelated local scratch into milestone work
- do not merge to `main` casually
- do not broaden `v0.2.0` scope into general transmission-line development
