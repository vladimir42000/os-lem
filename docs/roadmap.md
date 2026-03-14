# os-lem roadmap

## Project intent

`os-lem` is an open, scriptable lumped-element loudspeaker / enclosure simulator
with a development style inspired by Akabak 2.1-era workflows, but with a clean,
testable, modern Python implementation.

The roadmap is phase-based. Each phase has a clear goal, scope boundary, and
completion criterion.

---

## Phase 0 — recovery and primitive stabilization
**Status:** completed

### Goal
Recover a clean, testable baseline and freeze the first validated primitive set.

### Included
- repository repair
- parser / normalization scaffold
- frozen v1 input subset
- primitive formulas and tests for:
  - volume
  - duct
  - waveguide_1d
  - radiator

### Exit criteria
- stable baseline recovered
- repaired tests passing
- primitive behavior frozen sufficiently for coupled development

---

## Phase 1 — first coupled one-frequency solver
**Status:** completed

### Goal
Build the first minimal electromechano-acoustic coupled solver for one driver at
one frequency point.

### Included
- deterministic topology assembly
- acoustic nodal matrix assembly for:
  - volume
  - duct
  - radiator
- driver electrical + mechanical coupling
- one-frequency complex solve
- first solved internal state:
  - node pressures
  - voice-coil current
  - cone velocity
  - cone displacement

### Excluded
- frequency sweep helper
- observation framework expansion
- waveguide assembly
- broad architecture refactor
- multi-driver support

### Exit criteria
- one-frequency coupled solve works
- tests cover assembly, matrix build, and coupled solve
- stable checkpoint committed and tagged

### Result
Completed at milestone tag: `phase1-first-coupled-solve`

---

## Phase 2 — sweep and first observables
**Status:** completed

### Goal
Extend the one-frequency solver into a frequency sweep and expose the first
user-relevant outputs.

### Delivered outputs
- input impedance
- cone velocity
- cone displacement
- one-radiator far-field pressure
- one-radiator SPL

### Delivered work
- frequency sweep helper implemented
- solved sweep result container implemented
- first output helpers implemented
- frozen numerical reference tests added for the first outputs

### Exit criteria
- frequency sweep implemented
- outputs available from solved sweep
- first frozen numerical reference tests added

### Result
Phase 2 completed on the current branch state now handed into Phase 3.

---

## Phase 3 — validation of the current solver path
**Status:** closed

### Result
Phase 3 closed at commit `15b499f`.

Delivered:
- documentation alignment with actual assembled subset
- internal validation sanity tests for the current solver path

Not delivered as frozen validation:
- external Hornresp parity for the BR comparison

### Closure interpretation
Phase 3 increased trust in the current narrow solver path, but external comparison remains diagnostically unresolved.

---

## Phase 4 — diagnostic fault isolation before topology expansion
**Status:** closed

### Goal
Localize the source of the Hornresp bass-reflex mismatch before any new feature development.

### Result
Phase 4 closed at a corrective checkpoint.

Delivered:
- diagnostic work isolated a real solver sign-convention bug
- driver front / rear acoustic coupling signs were corrected
- frozen numerical reference outputs were refreshed to the corrected solver
- affected validation tests were updated to remain meaningful on the corrected baseline
- the repository returned to a green baseline with `54 passed`

### Explicit non-claim
Phase 4 does not freeze a broad external-parity claim. It closes the specific
diagnostic cycle that identified and corrected one real implementation bug.

### Exit criteria
- mismatch investigation reached a concrete implementation-level correction
- corrected baseline re-frozen with passing tests
- project ready to resume bounded topology expansion

---

## Phase 5 — extended acoustic topology support
**Status:** current

### Goal
Resume topology growth after the Phase 4 corrective checkpoint.

### Delivered so far
- `waveguide_1d` now assembles as a topology-resolved branch element
- the acoustic matrix accepts reduced two-port `waveguide_1d` stamping
- focused assembly and solve tests were added for the first minimal waveguide path
- stronger internal validation now covers:
  - constant-area segmentation-invariance sanity
  - conical segmentation-refinement sanity
- first waveguide-specific observability is now delivered:
  - endpoint flow export
  - endpoint particle-velocity export
  - minimal `line_profile` export for `pressure`
  - minimal `line_profile` export for `volume_velocity`
  - minimal `line_profile` export for `particle_velocity`
- stronger cross-profile internal validation now covers:
  - `particle_velocity = volume_velocity / local_area(x)` consistency
  - joint endpoint/profile agreement for all three profile quantities
  - cylindrical special-case consistency for constant area
- the existing `volume` / `duct` / `radiator` solver path remains green
- repository suite is green at `83 passed` in the local patched state

### Remaining likely items inside Phase 5
- limited external overlap checks once internal waveguide confidence is stronger

### Explicitly not yet delivered in Phase 5
- limited external overlap checks for current `waveguide_1d` cases
- distributed losses
- broad external parity claims

### Exit criteria
- first extended topology path implemented and tested
- at least one bounded follow-up validation or observability step completed
- no regression of earlier validated phases
- docs updated to reflect the new assembled capability

---

## Phase 6 — user-facing maturation
**Status:** planned

### Goal
Improve usability, examples, and result inspection after the next topology
extension is stable.

### Possible items
- richer examples
- clearer result objects
- plotting helpers
- better reporting / documentation

### Exit criteria
- examples align with implemented scope
- docs match actual solver capability
