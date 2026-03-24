# Next patch

## Recommended integration branch

- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Use this already-open milestone branch as the source for the next bounded patch.

## Recommended next patch branch

- `test/v0.3.0-element-observable-facade-error-contract`

## Purpose

Do one bounded regression-led patch that hardens the promoted element-observable contract at the provisional facade boundary.

## Scope

Allowed:
- add end-to-end API tests for invalid promoted element-observable requests
- verify parser-side validation failures surface cleanly through `run_simulation`
- cover unsupported target kinds, missing waveguide `location`, invalid waveguide `location`, and forbidden `location` on non-waveguide targets
- update docs only where needed to describe the regression purpose honestly

Not allowed:
- new solver physics
- new topology classes
- changes to the supported observable contract itself
- broad API redesign
- unrelated cleanup mixed into the regression patch

## Acceptance criteria

The patch is complete if:
1. `run_simulation` is regression-covered for invalid promoted element-observable requests
2. missing/invalid `location` behavior for `waveguide_1d` targets is covered end-to-end
3. forbidden `location` on `duct` and `radiator` targets is covered end-to-end
4. the active milestone line remains green
5. `pytest -q` stays green

## Immediate follow-up after this patch

After this regression patch lands, reassess the active milestone branch and choose the next bounded follow-up from repo truth rather than from old seed-state assumptions.
