# Patch registry

This file tracks the current planned patch pack at a human-readable level.

Status legend:
- planned
- active
- merged
- blocked
- deferred

---

## Current patch pack

Pack name:
- `v0.2.0 observation-contract restart`

### P-001 — docs reset and documentation restructuring
- status: merged
- branch: `chore/v0.2.0-docs-reset`
- purpose: align governance docs with current repo truth and create a clearer documentation hierarchy
- validation:
  - `pytest -q`
  - manual doc-path sanity

### P-002 — open clean `v0.2.0` milestone branch
- status: merged
- branch: `milestone/v0.2.0-offset-line-observation`
- purpose: separate release-story integration from long debug lineage
- validation:
  - clean milestone branch created from a green post-docs-reset state

### P-003 — mouth directivity helper / invariant prep
- status: merged
- branch: `fix/v0.2.0-mouth-directivity-only`
- purpose: isolate the helper needed for `mouth_directivity_only`
- delivered:
  - on-axis circular piston directivity helper
  - explicit small-`ka` limit handling
  - focused primitive regression coverage

### P-004 — implement `mouth_directivity_only`
- status: merged
- branch: `fix/v0.2.0-mouth-directivity-only`
- purpose: bounded observation-layer candidate implementation
- delivered:
  - opt-in `observable_contract: mouth_directivity_only`
  - solve-layer support for passive mouth/port radiators
  - API support for `spl` and term-level `spl_sum`
- validation:
  - `pytest -q`
  - raw/default path preserved by regression coverage

### P-005 — regression guard for `front` invariance
- status: merged
- branch: `fix/v0.2.0-mouth-directivity-only`
- purpose: freeze that the patch does not perturb the already-credible `front/raw` path
- validation:
  - dedicated regression tests
  - contract rejects driver-front use of `mouth_directivity_only`

### P-006 — observation-contract docs alignment
- status: merged
- branch: `fix/v0.2.0-mouth-directivity-only`
- purpose: align patch-tracking docs with the landed candidate contract

### P-007 — mouth observable normalization check
- status: merged
- branch: `fix/v0.2.0-mouth-observable-normalization-check`
- purpose: freeze one narrow mouth-path amplitude / area invariant without changing raw behavior
- delivered:
  - explicit connected-aperture area helper for passive mouth/port radiators
  - bounded guard that `mouth_directivity_only` uses the same physical area for mouth flow semantics and `D(ka_mouth)`
  - regression protection for mismatched duct area and supported waveguide terminus use
  - API-level failure coverage for inconsistent candidate-contract models
- validation:
  - `pytest -q`
  - one focused invariant check only

### P-008 — offset-line compare harness refresh
- status: planned
- branch: `fix/v0.2.0-offset-line-compare-harness`
- purpose: add one maintained comparison fixture that exercises the bounded mouth observation contracts
- validation:
  - `pytest -q`
  - no broad solver changes

### P-009 — `v0.2.0` release-note draft
- status: planned
- branch: `chore/v0.2.0-release-notes-draft`
- purpose: prepare the final milestone wording early
- validation:
  - no unsupported claim language

---

## Registry maintenance rule

Keep this file brief.
Do not turn it into a full issue tracker.
Only track the current session/milestone patch pack here.
