# Documentation index

This file is the navigation map for the repository documentation.

Use it to distinguish:
- operational truth
- stable technical reference
- historical/debug archive
- the parallel book companion

The repository remains the source of truth.

---

## Priority order of truth

1. current tested repository state
2. current branch and commit history
3. current milestone branch, if one exists
4. governance docs in this repo
5. stable technical docs in this repo
6. debug archive docs in this repo
7. parallel book / external commentary
8. old chat memory

---

## Layer 1 — governance and operational truth

Read these first in a new development session:

- `docs/start_here.md`
- `docs/current_scope.md`
- `docs/status.md`
- `docs/milestone_charter.md`
- `docs/release_strategy.md`
- `docs/release_plan.md`
- `docs/patch_registry.md`
- `docs/next_patch.md`
- `docs/session_handover.md`
- `docs/decision_log.md`
- `docs/change_log.md`
- `docs/development_policy.md`
- `docs/constitution.md`

Use these to answer:
- what is released
- what is planned
- what branch discipline applies
- what the next patch is
- what must not be changed casually

---

## Layer 2 — stable technical reference

Use these for implementation truth and architecture context:

- `docs/project_vision.md`
- `docs/vision.md`
- `docs/architecture.md`
- `docs/architecture_invariants.md`
- `docs/solver_math.md`
- `docs/input_format.md`
- `docs/frontend_api.md`
- `docs/radiator_models.md`
- `docs/capability_matrix.md`
- `docs/validation_plan.md`
- `docs/target_capabilities.md`
- `docs/the-lem-trinity-comparison-matrix.md`
- `docs/v0_1_0_release_notes.md`

These should change only when the underlying contract or validated capability changes.

---

## Layer 3 — debug and investigation archive

These preserve historical reasoning, isolated discrepancy studies, and proof/candidate branches.

Primary entry points:
- `docs/debug/README.md`
- `docs/experiment_registry.md`

Current archived debug notes:
- `docs/debug/closed_box_checkpoint.md`
- `docs/debug/handover.md`
- `docs/debug/observation_phase_reference_candidate.md`
- `docs/debug/offset_line_checkpoint.md`
- `docs/debug/offset_line_convention_scan.md`
- `docs/debug/radiator_observation_sd_ucone_no_expjkr_proof.md`

These files are valuable, but they are not the first startup control surface.

---

## Layer 4 — parallel book companion

The os-lem book is a parallel Quarto/GMD project.

Its role is defined in:
- `docs/book_contract.md`

Use the book for:
- design rationale
- implementation lessons
- observation-layer explanations
- debugging narratives
- validation philosophy

Do not use the book to override repo truth.

---

## Current active release story

Latest release:
- `v0.1.0` on `main`

Current planned milestone:
- `v0.2.0` — offset-line observation-contract stabilization

Immediate next technical patch after the docs reset:
- `fix/v0.2.0-mouth-directivity-only`
