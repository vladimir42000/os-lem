# Next patch

## Recommended next branch

- `chore/post-v0.2.0-next-milestone-seed`

## Purpose

Do one bounded planning patch after the branch-review plan is landed.
This patch should seed the next milestone explicitly instead of letting technical work restart implicitly.

## Scope

Allowed:
- define the next milestone name and release intent
- decide the next active integration branch name
- write the first patch-pack outline for the next milestone
- state what is in scope and out of scope for that next milestone
- align handover docs so future sessions start from the right branch and planning surface

Not allowed:
- solver changes
- API changes
- observation-contract changes
- branch deletion as part of the patch itself
- mixing archived debug analysis into the new milestone without explicit justification

## Acceptance criteria

The patch is complete if:
1. the next milestone name is explicit
2. the next active branch recommendation is explicit
3. the next milestone scope is bounded and conservative
4. startup docs tell the next session where to begin
5. `pytest -q` stays green on `main`

## Immediate follow-up after this patch

Only after the milestone-seed patch lands should the next technical feature branch be opened.
