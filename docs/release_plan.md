# Release plan

## Latest completed release

- `v0.2.0`
- title: `offset-line observation-contract stabilization`
- release branch of record: `main`

Observed release-line validation at close:
- `118 passed`

---

## What is complete

`v0.2.0` is released.
The release package includes:
- bounded mouth/port observation candidate support
- normalization guard
- compare harness
- release notes and release checklist
- conservative capability wording aligned to the tested repo state

---

## Post-release sequence

The post-release transition is intentionally split:
1. housekeeping patch
2. branch review / retention plan
3. next-milestone seed patch

Only after step 3 should new technical milestone work begin.

---

## Next milestone planning

Do **not** open the next major milestone implicitly.
After the branch-review plan is landed, do one explicit seed patch that defines:
- milestone name
- release intent
- active integration branch
- first bounded patch pack
