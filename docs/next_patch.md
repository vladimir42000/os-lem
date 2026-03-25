# Next patch

## Recommended integration branch

- `milestone/v0.4.0-capability-expansion`

Use this already-open milestone branch as the source for the next bounded patch.

## Recommended next patch branch

- `chore/v0.4.0-seed-waveguide-maturity`

## Purpose

Do one bounded governance/charter patch that updates the repo from closed `v0.3.0` posture to active `v0.4.0` waveguide-maturity posture.

## Scope

Allowed:
- update status / roadmap / milestone / handover docs from released `v0.3.0` truth to active `v0.4.0` truth
- freeze the first real `v0.4.0` capability campaign around lossy conical `waveguide_1d` maturity
- record what is explicitly not part of the opening `v0.4.0` patch pack

Not allowed:
- new solver physics in this patch
- new topology classes
- passive radiator or multi-driver work mixed into the seed patch
- broad API redesign
- unrelated cleanup mixed into the milestone seed patch

## Acceptance criteria

The patch is complete if:
1. the repo governance/docs layer no longer describes `v0.3.0` as the active target
2. `v0.3.0` is recorded as released on `main`
3. `v0.4.0` is recorded as the active milestone on `milestone/v0.4.0-capability-expansion`
4. the first real `v0.4.0` code patch is frozen as `feat/v0.4.0-conical-lossy-waveguide-mvp`
5. `pytest -q` stays green

## Immediate follow-up after this patch

After this seed patch lands, open the first real code campaign:
- `feat/v0.4.0-conical-lossy-waveguide-mvp`
