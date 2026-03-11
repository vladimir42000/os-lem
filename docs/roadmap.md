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
**Status:** in progress

### Goal
Extend the one-frequency solver into a frequency sweep and expose the first
user-relevant outputs.

### Planned outputs
- input impedance
- cone velocity
- cone displacement
- one-radiator SPL

### Current progress
- frequency sweep helper implemented
- first solved-sweep outputs available:
  - input impedance
  - cone velocity
  - cone displacement
  - one-radiator SPL

### Exit criteria
- frequency sweep implemented
- outputs available from solved sweep
- first frozen numerical reference tests added

---

## Phase 3 — validation cases
**Status:** planned

### Goal
Validate the first solver path against known analytical or trusted reference
cases.

### Candidate cases
- sealed-box-like topology
- simple vented-box-like topology
- low-frequency asymptotic checks
- sensitivity / sanity checks on element parameters

### Exit criteria
- reference validation cases documented
- acceptable agreement established for supported scope

---

## Phase 4 — extended acoustic topology support
**Status:** planned

### Goal
Broaden assembled topology support beyond the initial Session 6 subset.

### Planned candidates
- `waveguide_1d` assembly
- richer topologies
- additional element interoperability constraints

### Exit criteria
- first extended topology path implemented and tested
- no regression of earlier phases

---

## Phase 5 — user-facing maturation
**Status:** planned

### Goal
Improve usability, examples, and result inspection.

### Possible items
- richer examples
- clearer result objects
- plotting helpers
- better reporting / documentation

### Exit criteria
- examples align with implemented scope
- docs match actual solver capability
