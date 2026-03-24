# Next patch

## Recommended next integration branch

- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Create this branch from `main` before opening the next feature patch.

## Recommended next feature branch

- `feat/v0.3.0-element-observable-api-surface`

## Purpose

Do one bounded first `v0.3.0` feature patch that promotes already-existing element observability to the supported API/output surface.

## Scope

Allowed:
- expose existing element-level observables such as volume velocity and particle velocity through the supported API/output contract
- add narrow regression tests for the promoted observable surface
- update examples and docs only where needed to reflect the new supported contract

Not allowed:
- new solver physics
- new waveguide topology classes
- broad frontend work
- broad API redesign
- branch cleanup mixed into the feature patch

## Acceptance criteria

The patch is complete if:
1. the new integration branch is opened from `main`
2. the bounded element observable surface is exposed through the supported API/output layer
3. regression coverage proves default existing behaviors remain intact
4. docs and examples reflect the promoted observable surface honestly
5. `pytest -q` stays green

## Immediate follow-up after this patch

After the first `v0.3.0` feature patch lands, continue with a bounded regression/docs patch before considering wider milestone scope.
