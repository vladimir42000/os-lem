# Documentation constitution

This file defines the documentation control model for `os-lem`.

The goal is to keep future sessions restartable, resistant to drift, and explicit about which docs are allowed to decide "what happens next".

---

## 1. Authority hierarchy

### Layer A — live control docs
These are the only docs allowed to carry current sequencing truth.

Primary files:
- `docs/status.md`
- `docs/next_patch.md`
- `docs/session_handover.md`

Rules:
- these files must agree with each other
- if they do not agree, the repo is **not ready** for a routine DEV patch
- `docs/next_patch.md` and `docs/session_handover.md` must never point to different next actions

### Layer B — milestone context docs
These describe the current technical boundary, but they do not decide the next action by themselves.

Primary files:
- `docs/milestone_charter.md`
- `docs/current_scope.md`

### Layer C — stable technical reference
These define long-lived technical truth and should change only when the supported behavior or architecture contract really changes.

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
- `docs/decision_log.md`

### Layer D — procedure and navigation
These help sessions start correctly, but they are not live sequencing authority.

Primary files:
- `docs/start_here.md`
- `docs/development_policy.md`
- `docs/doc_index.md`
- `docs/constitution.md`

### Layer E — historical / reference docs
These may summarize history, release posture, or patch history, but they must not be treated as the deciding source for the next action.

Primary files:
- `docs/patch_registry.md`
- `docs/release_plan.md`
- `docs/change_log.md`
- `docs/release_strategy.md`

### Layer F — debug archive and book companion
Useful reference memory, not startup control.

Primary entry points:
- `docs/debug/README.md`
- `docs/experiment_registry.md`
- `docs/book_contract.md`

---

## 2. Role ownership

### DIRECTOR owns
- `docs/constitution.md`
- `docs/development_policy.md`
- `docs/start_here.md`
- milestone-control resets and rare sequencing redesign

### AUDIT owns
- `docs/status.md`
- `docs/next_patch.md`
- `docs/session_handover.md`
- readiness decisions and exact next-action freezing

### DEV owns
- code
- tests
- examples
- directly affected stable technical docs required by the patch contract

DEV does **not** own project sequencing.

---

## 3. Update policy

### Update on every accepted patch cycle
- `docs/status.md` when factual repo truth changed
- `docs/next_patch.md`
- `docs/session_handover.md`

### Update when technical contracts actually changed
- only the directly affected Layer C docs

### Update rarely and deliberately
- `docs/constitution.md`
- `docs/development_policy.md`
- `docs/start_here.md`
- milestone structure docs when the operating model itself changes

### Update only as historical summary
- `docs/patch_registry.md`
- `docs/release_plan.md`
- `docs/change_log.md`

---

## 4. Main rules

1. The repository is the primary source of truth.
2. Only Layer A decides the live next action.
3. If Layer E disagrees with Layer A, Layer E loses.
4. If Layer A disagrees internally, the repo is **not ready** for routine DEV work.
5. A routine technical patch must not edit stable docs or control-plane docs unless the patch contract explicitly requires it.
6. When in doubt, reduce the number of docs being edited, not increase it.
