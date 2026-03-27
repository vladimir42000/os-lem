# os-lem development policy

This file defines the working discipline for `os-lem` so development remains coherent across sessions, branches, and handoffs.

## 1. Source of truth

Priority order:
1. current tested repository state
2. current branch and commit graph
3. latest valid AUDIT handover
4. live control docs in the repo
5. milestone context docs in the repo
6. stable technical docs in the repo
7. historical/reference docs in the repo
8. older chat discussions

If older planning text disagrees with the current tested repo state, the repo wins.

---

## 2. Three-role operating model

### DIRECTOR
Purpose:
- repair or redesign the control plane when normal sequencing is broken

When DIRECTOR is allowed:
- live control docs disagree
- milestone branch-of-record is stale relative to the accepted working line
- two consecutive patches fail to reduce a blocker
- milestone closure or reopening needs an explicit management decision

DIRECTOR is rare. DIRECTOR is not a routine coding role.

### AUDIT
Purpose:
- inspect the real repo state
- decide whether the repo is ready for one next bounded patch
- write the handover for DEV

AUDIT output must be exactly one of:
- `READY` — repo is ready for one exact next bounded DEV patch
- `NOT READY` — repo truth is inconsistent and one exact reset/decision patch is required first

AUDIT owns:
- `docs/status.md`
- `docs/next_patch.md`
- `docs/session_handover.md`

### DEV
Purpose:
- implement exactly one bounded patch named by the latest valid AUDIT handover

DEV rules:
- one patch = one purpose
- no governance detours unless the AUDIT handover explicitly names a reset/governance patch
- no guessing from old chat text
- no second patch in the same session
- produce a working repo-native patch archive when changes are required

DEV does not own project sequencing.

---

## 3. Branch discipline

Branch roles:
- `main`: stable released branch
- `milestone/*`: integration branch of record for the active milestone
- `feature/*` / `feat/*`: bounded feature branch
- `fix/*`: bounded corrective branch
- `debug/*`: fault-isolation / truth-finding branch
- `test/*`: validation / regression branch
- `chore/*`: governance, docs, examples, maintenance

Rules:
- do not develop directly on `main`
- keep patch branches focused on one purpose
- push meaningful checkpoints to GitHub
- after an accepted patch, the active milestone branch must be fast-forwarded to the latest accepted working-line commit

---

## 4. Patch workflow

### Routine cycle
1. operator produces repo probe
2. AUDIT reads repo truth and writes a handover
3. DEV reads repo truth + the latest valid AUDIT handover
4. DEV implements exactly one bounded patch
5. operator applies patch and runs tests
6. accepted patch is committed and pushed
7. milestone branch is fast-forwarded to the accepted line
8. AUDIT writes the next handover

### Exception cycle
If routine sequencing is broken, use DIRECTOR first.

---

## 5. Test discipline

Tests are part of the design, not a final accessory.

Rules:
- passing tests must stay passing unless an intentional contract change is justified
- new behavior should come with focused tests
- do not weaken tests just to make the suite pass
- do not delete tests unless the deletion is explicitly justified and reviewed

---

## 6. Documentation discipline

- Layer A live control docs are small on purpose
- Layer E historical docs are not allowed to decide the next action
- stable technical docs change only when the supported contract actually changed
- update the smallest correct set of docs for each accepted patch

---

## 7. Practical rule

When in doubt:
- reduce scope
- preserve tests
- keep the milestone branch truthful
- let AUDIT freeze the next action
- use DIRECTOR only when the control plane is broken
