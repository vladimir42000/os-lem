# Next patch

## Recommended integration branch

- `milestone/v0.4.0-capability-expansion`

Use this already-open milestone branch as the source for the next bounded patch.

## Recommended next patch branch

- `chore/v0.4.0-release-promotion-plan`

## Purpose

Do one bounded release-promotion-planning patch that freezes how the current green `v0.4.0` line will be reviewed, documented, and prepared for promotion, without reopening technical scope.

## Scope

Allowed:
- update status / release / handover docs to reflect that the opening `v0.4.0` waveguide campaign is closed on the working line
- freeze the current green line (`140 passed`) as the evidence base for release-promotion planning
- record the bounded remaining work before any actual promotion step

Not allowed:
- new solver physics in this patch
- new topology classes
- new example refresh work mixed into release-promotion planning
- broad API redesign
- unrelated cleanup mixed into the release-promotion patch

## Acceptance criteria

The patch is complete if:
1. the repo governance/docs layer records that `chore/v0.4.0-close-decision` has landed
2. the next bounded follow-up is frozen as `chore/v0.4.0-release-promotion-plan`
3. the current green working line is recorded as `140 passed`
4. the remaining release-promotion work is stated explicitly and conservatively
5. `pytest -q` stays green

## Immediate follow-up after this patch

After this release-promotion planning patch lands, either execute the bounded promotion step or open one final checklist-only patch if the promotion review shows a concrete documentation gap.
