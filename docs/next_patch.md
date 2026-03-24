# Next patch

## Recommended integration branch

- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Use this already-open milestone branch as the source for the next bounded patch.

## Recommended next patch branch

- `chore/v0.3.0-first-patch-bookkeeping`

## Purpose

Do one bounded bookkeeping/docs patch that updates the milestone planning and handover docs after the first landed `v0.3.0` feature patch.

## Scope

Allowed:
- update milestone status wording from seeded/planned to active/landed where that is now repo truth
- record that `feat/v0.3.0-element-observable-api-surface` landed on the milestone line
- record the observed active milestone validation at `123 passed`
- update handover text so future sessions resume from the active milestone branch instead of reopening the milestone from `main`

Not allowed:
- new solver physics
- new topology classes
- changes to the supported observable contract itself
- broad API redesign
- unrelated cleanup mixed into the bookkeeping patch

## Acceptance criteria

The patch is complete if:
1. milestone governance docs no longer describe `v0.3.0` as merely seeded
2. the first landed `v0.3.0` feature patch is recorded honestly
3. the active milestone branch and its observed green validation are recorded precisely
4. the startup / handover instructions match the current milestone reality
5. `pytest -q` stays green

## Immediate follow-up after this patch

After this bookkeeping patch lands, choose the next bounded milestone follow-up from the active milestone branch without widening scope by default.
