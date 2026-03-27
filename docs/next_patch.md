# Next patch

## Recommended integration branch

- `milestone/v0.4.0-capability-expansion`

Use this already-open milestone branch as the source for the next bounded patch.

## Recommended next patch branch

- `chore/v0.4.0-close-prep`

## Purpose

Do one bounded close-prep patch that updates the governance/docs layer from "opening waveguide campaign in progress" to "opening waveguide campaign landed and ready for milestone close review".

## Scope

Allowed:
- update status / roadmap / milestone / handover docs to reflect the actually landed `v0.4.0` waveguide campaign
- freeze the remaining bounded close sequence after the landed waveguide campaign
- prepare the repo for a later close decision and release-promotion patch sequence

Not allowed:
- new solver physics in this patch
- new topology classes
- passive radiator or multi-driver work mixed into close prep
- broad API redesign
- unrelated cleanup mixed into the close-prep patch

## Acceptance criteria

The patch is complete if:
1. the repo governance/docs layer no longer describes the opening `v0.4.0` waveguide campaign as merely planned
2. the landed opening patch pack is recorded accurately
3. the next bounded follow-up is frozen as `chore/v0.4.0-close-decision`
4. the expected later promotion step is frozen as `chore/v0.4.0-release-promotion-plan`
5. `pytest -q` stays green

## Immediate follow-up after this patch

After this close-prep patch lands, open the bounded review/decision patch:
- `chore/v0.4.0-close-decision`
