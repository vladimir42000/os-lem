# Decision log

This file records important project decisions so that the repository, not the chat, becomes the long-term memory of the project.

Format:

- Date
- Decision
- Status
- Reason

---

## 2026-03-09
**Decision:** Create an open command-line loudspeaker simulator inspired by Akabak 2.1 LEM.  
**Status:** accepted  
**Reason:** A scriptable and transparent LEM-style solver is feasible and useful for enclosure design, optimization, and later GUI work.

## 2026-03-09
**Decision:** v1 will focus on linear frequency-domain lumped / 1D acoustic simulation only.  
**Status:** accepted  
**Reason:** This is the most realistic path to a working kernel and matches the strongest immediate use cases.

## 2026-03-09
**Decision:** Do not target BEM or full Akabak 3 equivalence in v1.  
**Status:** accepted  
**Reason:** BEM and 3D acoustics would greatly increase complexity and slow progress before a validated core exists.

## 2026-03-09
**Decision:** Use Python as the main implementation language.  
**Status:** accepted  
**Reason:** Python gives the best balance of development speed, numerical tooling, plotting ecosystem, optimization compatibility, and future GUI options.

## 2026-03-09
**Decision:** CLI first, GUI later.  
**Status:** accepted  
**Reason:** Command-line workflows are easier to validate, automate, test, and integrate with optimization loops.

## 2026-03-09
**Decision:** Repository files are the project memory; chats are workspaces only.  
**Status:** accepted  
**Reason:** Long development cannot rely on chat history alone. Stable specs and logs are required.

## 2026-03-09
**Decision:** Organize development into a small number of focused threads.  
**Status:** accepted  
**Reason:** This keeps discussions manageable and reduces drift:
- master / roadmap
- solver physics
- implementation
- validation

## 2026-03-09
**Decision:** Prefer a general network philosophy rather than a Hornresp-like fixed topology.  
**Status:** accepted  
**Reason:** The software should remain flexible for arbitrary practical enclosure structures.

## 2026-03-09
**Decision:** Allow high-level horn / line shapes in user input, even if internally discretized.  
**Status:** accepted  
**Reason:** User convenience should not be sacrificed to internal solver simplicity.

## 2026-03-09
**Decision:** Pressure and volume-velocity inspection along 1D paths is a roadmap feature.  
**Status:** accepted  
**Reason:** This is highly valuable for resonator placement, line understanding, and future damping strategy work.

## 2026-03-09
**Decision:** Measured driver support is important but postponed until after the base kernel is stable.  
**Status:** accepted  
**Reason:** A trustworthy parametric kernel must exist before hybrid measured/parametric models are added.

## 2026-03-09
**Decision:** Advanced stuffing / porous-fill modeling is deferred.  
**Status:** accepted  
**Reason:** It is important but model-sensitive and should not block the first useful release.

---

## Pending decisions

### P-001
**Decision:** Exact v1 driver input schema  
**Status:** pending  
**Reason:** Need to choose between direct electromechanical parameters, classical T/S entry with internal conversion, or both.

### P-002
**Decision:** Final top-level YAML schema  
**Status:** pending  
**Reason:** Need a stable but not overcomplicated input format.

### P-003
**Decision:** Exact internal unknown formulation for the solver  
**Status:** pending  
**Reason:** To be finalized in solver math design.

### P-004
**Decision:** Initial radiation models to support  
**Status:** pending  
**Reason:** Need to balance realism and implementation simplicity.

### P-005
**Decision:** Method for group delay computation  
**Status:** pending  
**Reason:** Must define output conventions clearly and consistently.
