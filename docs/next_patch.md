# Next patch

## Recommended integration branch

- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Use this already-open milestone branch as the source for the next bounded patch.

## Recommended next patch branch

- `chore/v0.3.0-close-prep`

## Purpose

Do one bounded final close-prep patch that freezes milestone planning, handover wording, and release posture around the current regression-hardened `v0.3.0` state.

## Scope

Allowed:
- record that `chore/v0.3.0-post-regression-bookkeeping` landed on the milestone line
- confirm the active milestone line and its observed `128 passed` validation as the current decision basis
- align milestone planning and handover docs so they point to close-prep rather than to already-landed bookkeeping work
- prepare an explicit next-step decision about whether to close `v0.3.0` without widening technical scope

Not allowed:
- new solver physics
- new topology classes
- changes to the supported observable contract itself
- broad API redesign
- unrelated cleanup mixed into the close-prep patch

## Acceptance criteria

The patch is complete if:
1. milestone governance docs no longer point at the already-landed post-regression bookkeeping patch as the next step
2. the active milestone branch and its observed `128 passed` validation remain the stated basis for the close decision
3. the landed post-regression bookkeeping patch is recorded honestly
4. the next action is framed as an explicit close-prep / close-decision step rather than more unbounded milestone growth
5. `pytest -q` stays green

## Immediate follow-up after this patch

After this close-prep patch lands, decide from the active milestone branch whether `v0.3.0` should be closed as complete or whether one more clearly-bounded patch is still required.
