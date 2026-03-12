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
Any attempt to assemble `waveguide_1d` during the current Phase 1/2 patch series
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

## D-0007 — Phase 1 scope boundary
**Status:** accepted

Phase 1 scope was:
**first coupled one-frequency solver**

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
`docs/status.md`, `docs/roadmap.md`, `docs/decision_log.md`, and
`docs/development_policy.md` should be kept aligned with meaningful project
checkpoints.

---

## D-0009 — first coupled one-frequency solve is now frozen as a milestone
**Status:** accepted

The first electromechano-acoustic coupled one-frequency solve is implemented and
covered by focused tests.

Milestone tag:
`phase1-first-coupled-solve`

### Consequence
Phase 2 should extend this solver path rather than replacing it with a new
architecture.

---

## D-0010 — Phase 2 begins with sweep and first observables
**Status:** accepted

The next active phase is:
**Phase 2 — sweep and first observables**

### In scope
- sweep helper over the current coupled one-frequency solve
- first output extraction
- focused tests for sweep/output behavior

### Out of scope
- waveguide assembly
- multi-driver support
- broad refactor
- speculative topology expansion


## D-0011 — Phase 2 sweep reuses the frozen one-frequency solve
**Status:** accepted

The first Phase 2 sweep helper is implemented by repeatedly calling the
existing one-frequency coupled solve and stacking results into sweep arrays.

### Consequence
Phase 2 extends the already tested Phase 1 path directly and avoids a
separate sweep-specific solve architecture at this stage.


## D-0012 — First radiator SPL follows the frozen radiator contract
**Status:** accepted

The first one-radiator SPL helper computes radiator branch flow from solved
radiator node pressure and radiator impedance, then applies the frozen
far-field transfer relation before converting to dB.

### Consequence
Early Phase 2 SPL behavior is explicitly tied to the current radiator model
contract and should not be changed casually.

---

## D-0013 — Phase 3 is validation-first, not feature-expansion-first
**Status:** accepted

The next active phase is:
**Phase 3 — validation of the current solver path**

### In scope
- validation of the already implemented assembled subset:
  - `volume`
  - `duct`
  - `radiator`
- internal physics sanity checks
- limited external comparison for simple overlapping cases
- documentation alignment with actual solver capability

### Out of scope
- `waveguide_1d` assembly
- multi-driver support
- broad refactor
- speculative capability growth

### Consequence
Phase 3 should increase trust in the current narrow solver path rather than
expand topology support.

---

## D-0014 — External comparison in Phase 3 is limited to overlapping simple cases
**Status:** accepted

External comparison is useful in Phase 3, but only where the current solver
scope clearly overlaps with the reference tool scope.

### Consequence
Acceptable Phase 3 external comparisons include simple cases such as:
- free-air-like sanity checks
- sealed-box-like cases
- simple vented-box-like cases

Phase 3 should not claim agreement for unsupported line / horn / broader
waveguide topologies.

---

## D-0015 — Phase 4 begins with `waveguide_1d` assembly
**Status:** superseded

This was the planned next step immediately after the initial Phase 3 framing:
begin topology expansion with `waveguide_1d` assembly.

### Superseded by
`D-0016`

### Historical note
After the first external Hornresp bass-reflex comparison exposed a large
unresolved mismatch, the project changed course: before adding new topology
support, Session 4 was redefined as a diagnostic fault-isolation phase.

### Consequence
`waveguide_1d` assembly remains an intended later topology-expansion step, but
it is no longer the immediate next phase after Phase 3 closure.

---

## D-0016 — Phase 4 is diagnostic fault isolation before topology expansion
**Status:** accepted

After Phase 3 closure, the first external Hornresp bass-reflex comparison
remained diagnostically unresolved. Therefore the immediate next phase is not
topology expansion, but focused fault isolation.

### In scope
- driver-only equivalence checks
- rear-volume loading checks
- staged reintroduction of duct and radiator
- focused diagnostic notes, probes, and tests
- localization of where mismatch first appears

### Out of scope
- `waveguide_1d` assembly
- broad topology expansion
- broad refactor
- unsupported horn / line parity claims
- forcing full Hornresp parity prematurely

### Consequence
The next accepted work should increase confidence about mismatch origin before
new topology complexity is introduced. `waveguide_1d` assembly moves to the
later extended-topology phase.

---

## D-0017 — driver front / rear acoustic coupling sign convention corrected
**Status:** accepted

Session 4 diagnostic work identified a sign-convention bug in the driver
acoustic coupling rows of the coupled solve in `src/os_lem/solve.py`.

The front / rear coupling signs were corrected so the solver baseline better
matches physically plausible loudspeaker behavior and the real vented-box
comparison used during the diagnostic cycle.

### Consequence
Previous frozen numerical reference outputs reflected the earlier incorrect
sign convention and are superseded.

The corrected solver is now the accepted baseline for subsequent development
and future regressions must be judged against the corrected sign convention,
not against the older frozen-reference outputs.


---

## D-0018 — Phase 5 begins with a planning freeze for minimal `waveguide_1d` assembly
**Status:** accepted

After the Phase 4 corrective checkpoint, the project resumes topology expansion in Phase 5, but the first step is not immediate broad implementation. The first accepted Phase 5 patch is a documentation freeze of the exact boundary for the initial `waveguide_1d` implementation slice.

### Consequence
The next implementation patch after this planning freeze must remain narrow.

### Frozen in scope for the first implementation slice
- first assembled `waveguide_1d` participation in the acoustic nodal matrix
- reuse of the frozen conical-guide internal segmentation contract
- preservation of the corrected `volume` / `duct` / `radiator` solver path
- focused non-regression and line-assembly tests

### Frozen out of scope for the first implementation slice
- `line_profile`
- waveguide-specific endpoint flow export
- waveguide-specific particle-velocity export
- distributed losses
- multi-driver support
- broad architecture refactor
- broad external parity claims

### Rationale
This keeps Phase 5 aligned with the repository discipline of one patch, one purpose, while allowing external comparison to continue later as a bounded validation stream rather than an implementation blocker.