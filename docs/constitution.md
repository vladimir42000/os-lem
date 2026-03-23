# Documentation constitution

This file defines the documentation operating model for `os-lem`.

The goal is to keep future sessions disciplined, restartable, and resistant to drift after long debug periods.

---

## Layer model

### Layer 1 — governance and operational truth

Updated whenever the active project state changes.

Primary files:
- `docs/doc_index.md`
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
- `docs/development_policy.md`

Use these first in a new session.

### Layer 2 — stable technical reference

Updated only when technical contracts or supported behavior actually change.

Primary files:
- `docs/project_vision.md`
- `docs/architecture_invariants.md`
- `docs/solver_math.md`
- `docs/input_format.md`
- `docs/frontend_api.md`
- `docs/radiator_models.md`
- `docs/capability_matrix.md`
- `docs/validation_plan.md`
- `docs/target_capabilities.md`

### Layer 3 — debug archive

Historical diagnostic memory, not primary startup control.

Primary entry points:
- `docs/debug/README.md`
- `docs/experiment_registry.md`

### Layer 4 — parallel book companion

The book is explanatory and pedagogical.
Its contract is defined in:
- `docs/book_contract.md`

---

## Update policy

### Update on almost every meaningful patch
- `docs/next_patch.md`
- `docs/session_handover.md`
- directly affected docs only

### Update at milestone or strategy checkpoints
- `docs/status.md`
- `docs/milestone_charter.md`
- `docs/patch_registry.md`
- `docs/release_plan.md`
- `docs/change_log.md`

### Update rarely and deliberately
- `docs/project_vision.md`
- `docs/architecture_invariants.md`
- `docs/target_capabilities.md`

---

## Main rule

Do not mix these roles:
- release truth
- active milestone planning
- stable technical reference
- historical debug narrative
- book-style explanation

When in doubt, reduce scope and update the smallest correct doc set.
