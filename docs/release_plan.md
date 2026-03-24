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

## Post-release transition

The post-release transition was intentionally split into:
1. housekeeping patch
2. branch review / retention plan
3. next-milestone seed patch

These transition steps are complete.

---

## Current completed milestone awaiting explicit release decision

- `v0.3.0`
- title: `waveguide observability and API maturity`
- milestone branch: `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Landed patch pack on the completed milestone branch:
- `feat/v0.3.0-element-observable-api-surface`
- `chore/v0.3.0-first-patch-bookkeeping`
- `test/v0.3.0-element-observable-facade-error-contract`
- `chore/v0.3.0-post-regression-bookkeeping`
- `chore/v0.3.0-close-prep`

Observed milestone validation on the close-decision line:
- `128 passed`

Current release posture:
- `v0.3.0` is complete on its milestone branch
- `main` remains the released `v0.2.0` line until an explicit promotion / release action is chosen
- no further `v0.3.0` milestone-scope patch is recommended by default

Planning principle from here:
- if work continues, treat it as bounded release-promotion planning rather than more `v0.3.0` scope growth
