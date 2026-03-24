# Release plan

## Stable release line

- `main` is the stable release line
- releases are merged into `main` only when milestone exit criteria are satisfied

## Current release candidate

### Candidate

- milestone branch: `milestone/v0.2.0-offset-line-observation`
- release target: `v0.2.0`

### Intent

`v0.2.0` = **offset-line observation-contract stabilization**

### Current posture

This milestone is now in **release-candidate review** state.

## Release-candidate checklist

Before release, confirm that:

- milestone docs are aligned with actual repo truth
- release notes are accurate and bounded
- the compare harness remains usable for the intended offset-line evidence path
- no open milestone patch remains except a tiny justified close correction, if any
- `pytest -q` remains green on the milestone branch

## If release is approved

Planned release flow:

1. switch to `main`
2. pull fast-forward only
3. merge the milestone branch fast-forward only
4. tag `v0.2.0`
5. push `main` and the tag

## If release is not approved

Only one additional bounded close patch should be opened, and only for:

- a release-claim correction
- a release-note correction
- a tiny validation/doc correction
