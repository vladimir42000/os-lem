# Milestone charter

## Milestone

- Name: `v0.2.0`
- Branch: `milestone/v0.2.0-offset-line-observation`

## Milestone definition

`v0.2.0` is a bounded milestone for:

**offset-line observation-contract stabilization**

## In-scope deliverables

- bounded observation-layer improvement for mouth/port handling
- explicit candidate contract for `mouth_directivity_only`
- normalization guard for the candidate path
- narrow compare harness supporting offset-line review
- coherent milestone docs and release-note draft

## Out of scope

- broad transmission-line feature expansion
- general topology growth
- solver architecture refactor
- multi-driver and passive-radiator roadmap growth
- frontend/productization work

## Current milestone state

The intended bounded milestone work is complete enough to move to
**release-candidate review**.

## Exit criteria

The milestone exits when all of the following are true:

- docs accurately describe the bounded `v0.2.0` claim
- release notes are ready with only minimal wording edits, if any
- compare harness and test suite are green on the milestone branch
- no remaining issue requires more than a tiny close patch

## Next action

The default next action is now a **release decision**, not another default patch.
