# Next patch

## Recommended integration branch

- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Use this already-open milestone branch as the source for the next bounded patch.

## Recommended next patch branch

- `chore/v0.3.0-post-regression-bookkeeping`

## Purpose

Do one bounded bookkeeping/docs patch that updates milestone planning, capability wording, and handover docs after the landed regression-hardening patch set.

## Scope

Allowed:
- update milestone status wording and observed validation from `123 passed` to `128 passed` where that is now repo truth
- record that `test/v0.3.0-element-observable-facade-error-contract` landed on the milestone line
- align capability wording for the promoted element-observable facade surface to the current tested milestone truth
- update startup / handover text so future sessions resume from the current active milestone state and reassess close-prep from repo truth

Not allowed:
- new solver physics
- new topology classes
- changes to the supported observable contract itself
- broad API redesign
- unrelated cleanup mixed into the bookkeeping patch

## Acceptance criteria

The patch is complete if:
1. milestone governance docs no longer point at the already-landed regression patch as the next step
2. the active milestone branch and its observed `128 passed` validation are recorded precisely
3. the landed regression-hardening patch is recorded honestly
4. capability wording is aligned to the current tested milestone truth where needed
5. `pytest -q` stays green

## Immediate follow-up after this patch

After this bookkeeping patch lands, reassess from the active milestone branch whether `v0.3.0` now needs only a final close-prep patch.
