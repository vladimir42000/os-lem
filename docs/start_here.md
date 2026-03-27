# os-lem start here

This file is a procedural bootstrap only.
It is not the authoritative source for the current next action.

## Startup rule

Every new session must first decide which role it is acting in:
- `DIRECTOR`
- `AUDIT`
- `DEV`

Do not start coding before the role is explicit.

---

## Required startup protocol

1. Inspect the live repo first:
   - `git branch --show-current`
   - `git status --short`
   - `git log --oneline --decorate -n 12`
   - `pytest -q`

2. Then read the live control docs:
   - `docs/status.md`
   - `docs/next_patch.md`
   - `docs/session_handover.md`

3. Then read milestone context if needed:
   - `docs/milestone_charter.md`
   - `docs/current_scope.md`

4. Only then read wider reference docs if the task actually requires them.

---

## Authority rule

Live next-action authority is:
1. current tested repo state
2. current branch / commit graph
3. latest valid AUDIT handover
4. `docs/status.md`
5. `docs/next_patch.md`
6. `docs/session_handover.md`

Historical/reference docs do not override this.

---

## Mode-specific rule

### If acting as AUDIT
- decide `READY` or `NOT READY`
- name exactly one next action
- write the handover

### If acting as DEV
- implement only the next action frozen by the latest valid AUDIT
- do not re-plan the milestone

### If acting as DIRECTOR
- change only the control plane that is actually broken
- do not casually rewrite technical truth

---

## Current procedural note

After the director reset lands, the first required action is an `AUDIT`.
No routine DEV patch should start before that post-reset audit exists.
