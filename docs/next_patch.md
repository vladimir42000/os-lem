# Next patch

## Recommended next branch

- `chore/post-v0.2.0-housekeeping`

## Purpose

Do one bounded post-release housekeeping patch after the successful `v0.2.0` release.
This is **not** a new solver feature patch.

## Scope

Allowed:
- update repo docs from “release candidate” language to “released on main” language where still needed
- add reciprocal links between `os-lem` and `os-lem-book`
- add a housekeeping checklist for branch/tag cleanup and future handover
- record which old milestone/debug branches should be reviewed after the release
- prepare the handoff surface for next-milestone planning

Not allowed:
- solver changes
- API changes
- observation-contract changes
- branch deletion as part of the patch itself
- mixing unrelated scratch/debug files into the patch

## Acceptance criteria

The patch is complete if:
1. `pytest -q` stays green on `main`
2. docs clearly state that `v0.2.0` is released
3. the companion book link is explicit and correct
4. the housekeeping checklist exists and is usable by a future operator
5. the next work after housekeeping is framed as milestone planning, not another implicit `v0.2.0` patch

## Immediate follow-up after this patch

Do a separate release-hygiene review session for:
- stale milestone branch review
- old debug branch retention vs pruning
- next milestone definition (`v0.3.0` or equivalent)
