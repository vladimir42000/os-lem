# os-lem decision log

This file records decisions that should not be casually changed during ongoing
development.

---

## D-0001 — recovered baseline is the development floor
**Status:** accepted

The recovered Session 5 baseline at commit `b31df3d` and tag
`baseline-session5-recovered` is the development floor for subsequent work.

### Consequence
New work should branch from this recovered baseline or from descendants that
preserve its repaired behavior.

---

## D-0002 — development proceeds in small, test-preserving patches
**Status:** accepted

Development is intentionally incremental. Large speculative rewrites are
avoided.

### Consequence
Each patch should be narrow in scope, locally reviewable, and accompanied by
tests or preservation of existing tests.

---

## D-0003 — repository state overrides stale planning prose
**Status:** accepted

When there is tension between older planning text and the actual current code,
the current tested repository state is the source of truth.

### Consequence
Thread handoffs should always include the current repo snapshot and current test
status.

---

## D-0004 — Session 6 starts with a minimal assembled subset
**Status:** accepted

The first assembled subset for coupled development is intentionally restricted
to:
- `volume`
- `duct`
- `radiator`

`waveguide_1d` is not assembled yet in the current phase.

### Consequence
Any attempt to assemble `waveguide_1d` during the current Phase 1 patch series
should fail explicitly rather than silently behave approximately.

---

## D-0005 — deterministic topology ordering is frozen
**Status:** accepted

Assembly produces a deterministic node ordering and topology-resolved element
representation before coupled solve logic is added.

### Consequence
Later solver code should consume the assembled representation rather than
re-deriving node order ad hoc.

---

## D-0006 — acoustic matrix is built before driver coupling
**Status:** accepted

The first frequency-dependent acoustic nodal admittance matrix is implemented
and tested before adding electromechanical driver coupling.

### Consequence
The coupled solver should build on the validated acoustic matrix path rather
than replacing it.

---

## D-0007 — current phase boundary
**Status:** accepted

The current active phase is:
**Phase 1 — first coupled one-frequency solver**

### In scope
- minimal coupled solve
- one driver
- one frequency
- minimal solved state

### Out of scope
- sweep helper
- observation expansion
- waveguide assembly
- broad refactor
- multi-driver support

---

## D-0008 — repository docs are the long-term project memory
**Status:** accepted

Chat threads are working spaces. The repository documentation should carry the
persistent operational state of the project.

### Consequence
`docs/status.md`, `docs/roadmap.md`, and `docs/decision_log.md` should be kept
aligned with meaningful project checkpoints.
