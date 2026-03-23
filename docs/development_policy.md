# os-lem development policy

This file defines the working discipline for `os-lem` so development remains coherent across sessions, branches, and handoffs.

## 1. Source of truth

The repository is the primary source of truth.

Priority order:
1. current tested repository state
2. current branch and commit history
3. governance docs in the repo
4. stable technical docs in the repo
5. debug archive docs in the repo
6. book companion
7. older chat discussions

If older planning text disagrees with the current tested repo state, the repo wins.

---

## 2. Development philosophy

`os-lem` is developed in small, controlled, test-preserving increments.

Rules:
- no broad speculative rewrites
- no silent architecture changes
- no mixing unrelated fixes in one patch
- no casual modification of already-repaired files
- no assumption that an untested idea is an improvement

Every patch should have:
- a narrow purpose
- a clear acceptance criterion
- tests preserved or extended
- a meaningful commit message

---

## 3. Branch discipline

Branch roles:
- `main`: stable, released branch
- `milestone/*`: release integration branch
- `feature/*`: bounded feature branch
- `fix/*`: bounded corrective branch
- `debug/*`: fault-isolation / truth-finding branch
- `chore/*`: governance, docs, examples, maintenance

Rules:
- do not develop directly on `main`
- do not merge unfinished work into `main`
- keep patch branches focused on one purpose
- push meaningful checkpoints to GitHub

---

## 4. Patch workflow

Default workflow for every development step:

1. inspect current repo state
2. define the smallest useful next patch
3. apply the patch locally
4. run tests
5. if tests pass, commit
6. push at meaningful checkpoints

Do not stack many unverified edits before testing.

---

## 5. Test discipline

Tests are part of the design, not a final accessory.

Rules:
- existing passing tests must stay passing unless an intentional change is justified
- new behavior should come with focused tests
- do not weaken tests just to make the suite pass
- do not delete tests unless the deletion is explicitly justified and reviewed

When a test fails:
- first determine whether the code is wrong or the test is stale
- do not “fix” failures blindly

---

## 6. Milestone discipline

Development proceeds through explicit release stories, not just ad hoc patch sequences.

Each milestone must define:
- goal
- in-scope items
- out-of-scope items
- completion criteria

Do not expand milestone scope casually.
If a useful idea belongs to a later release, record it and postpone it.

---

## 7. Handoff discipline between sessions

A new session should start from the repo and current handoff docs, not from memory.

Preferred handoff bundle:
1. current repo tarball
2. handoff markdown
3. current branch name
4. current commit hash
5. current `pytest -q` result
6. exact next task

The handoff markdown should include:
- what was completed
- files touched
- known limitations
- frozen decisions
- immediate next step
- what must not be changed casually

---

## 8. Documentation discipline

Repository docs are the long-term project memory.

The main documentation layers are:
- governance / operational truth
- stable technical reference
- debug archive
- book companion

Use `docs/doc_index.md` to navigate them.

Update the smallest correct set of docs for each patch.
Do not let docs drift for several sessions.

---

## 9. Milestones and tags

Use commits for implementation history and tags for recovery anchors.

Tags should mark states that are known to be valuable recovery points.

---

## 10. Solver integrity rules

For solver development:
- freeze conventions once tested
- do not change sign conventions casually
- do not change matrix ordering casually
- do not bypass the assembled representation with ad hoc logic
- introduce new topology support only when explicitly in scope

Important design choices must be recorded in `docs/decision_log.md`.

---

## 11. Communication discipline for future sessions

When continuing development in a new session:
- inspect the actual repo before proposing code
- do not assume module names or structure without checking
- prefer exact file-level edits
- prefer copy-pasteable shell blocks for changes
- keep changes small enough to verify immediately

If context is missing, reconstruct it from the repo and docs first.

---

## 12. Practical rule

When in doubt:
- reduce scope
- preserve tests
- commit clean checkpoints
- document decisions
- keep `main` stable

---

## Session startup rule

Each new session must begin by reading:
- `docs/doc_index.md`
- `docs/start_here.md`
- `docs/current_scope.md`
- `docs/status.md`
- `docs/milestone_charter.md`
- `docs/next_patch.md`

Then inspect:
- `git status`
- current branch
- recent commits
- `pytest -q`

No implementation should begin before the next patch objective is frozen.
