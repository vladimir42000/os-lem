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
- `v0.2.0 restart / docs reset + first bounded observation patch`

### P-001 — docs reset and documentation restructuring
- status: planned
- branch: `chore/v0.2.0-docs-reset`
- purpose: align governance docs with current repo truth and create a clearer documentation hierarchy
- expected files:
  - `README.md`
  - governance docs under `docs/`
  - new documentation map / registry files
  - `docs/debug/` archive relocation
- validation:
  - `pytest -q`
  - manual doc-path sanity

### P-002 — open clean `v0.2.0` milestone branch
- status: planned
- branch: `milestone/v0.2.0-offset-line-observation`
- purpose: separate release-story integration from long debug lineage
- validation:
  - branch created from a green post-docs-reset state

### P-003 — mouth directivity helper / invariant prep
- status: planned
- branch: `fix/v0.2.0-mouth-directivity-only`
- purpose: isolate the helper or narrow contract needed for `mouth_directivity_only`
- validation:
  - focused tests added or updated
  - no change to `front`

### P-004 — implement `mouth_directivity_only`
- status: planned
- branch: `fix/v0.2.0-mouth-directivity-only`
- purpose: bounded observation-layer candidate implementation
- validation:
  - `pytest -q`
  - focused compare script / metric review

### P-005 — regression guard for `front` invariance
- status: planned
- branch: `fix/v0.2.0-mouth-directivity-only`
- purpose: freeze that the patch does not perturb the already-credible `front/raw` path
- validation:
  - dedicated regression test or frozen comparison support

### P-006 — observation-contract docs alignment
- status: planned
- branch: `chore/v0.2.0-observation-contract-docs`
- purpose: update current-scope and release docs after the bounded patch lands
- validation:
  - docs consistent with code and tests

### P-007 — `v0.2.0` release-note draft
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
