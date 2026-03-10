# Roadmap

## v0.1 - Project foundation
Goal: establish the project structure and technical direction.

Deliverables:
- repository structure
- documentation skeleton
- frozen input-file philosophy
- solver architecture draft
- validation-plan draft

## v0.2 - Minimal solver kernel
Goal: solve simple linear frequency-domain electromechanical-acoustic networks.

Deliverables:
- complex frequency sweep engine
- driver normalization (`ts_classic` and `em_explicit` to one canonical form)
- basic acoustic compliance / mass / resistance primitives internally
- node-based assembly
- electrical impedance output
- basic single-radiator SPL output

## v0.3 - First usable enclosure models
Goal: simulate the first practical box alignments.

Deliverables:
- sealed-box support
- vented-box support
- `volume`, `duct`, and `radiator` support
- first radiator models:
  - `infinite_baffle_piston`
  - `unflanged_piston`
  - `flanged_piston`
- plots:
  - impedance
  - SPL
  - phase
  - cone displacement
  - group delay

## v0.4 - Waveguide / TQWP support
Goal: support 1D line-based enclosures.

Deliverables:
- `waveguide_1d` support
- `profile: conical`
- internal segmentation support
- examples:
  - straight cylindrical line
  - conical TQWP
  - resonator-assisted line built by topology

## v0.5 - Field inspection and summation
Goal: make the solver more useful for resonator placement and source-combination work.

Deliverables:
- separate driver / port / mouth SPL observation
- complex SPL summation
- node-pressure output
- line-profile output at chosen frequency:
  - pressure
  - volume velocity
  - particle velocity
- export of sampled field data

## v0.6 - High-level geometry growth
Goal: improve user input while keeping solver internals simple.

Deliverables:
- additional `waveguide_1d` profile families, possibly:
  - exponential
  - parabolic
  - tractrix
  - Le Cléac'h
- automatic internal segmentation controls
- more examples and reference validations

## v0.7 - Optimization interface
Goal: enable automated search of parameters.

Deliverables:
- parameter sweep framework
- objective-function framework
- hooks for SciPy optimization
- support for batch runs and machine-readable result export

## v0.8 - Measured driver support
Goal: move beyond idealized parametric drivers.

Deliverables:
- import complex impedance data
- import infinite-baffle SPL / phase data
- define hybrid measured/parametric driver modes
- validation on real measured drivers

## v0.9 - Interactive desktop interface
Goal: provide real-time engineering workflow.

Deliverables:
- GUI shell
- live parameter editing
- live curve refresh
- comparison overlays
- saved projects

## v1.0 - Stable engineering release
Goal: dependable open tool for Akabak-2.1-style command-line simulation.

Deliverables:
- stable CLI
- documented input format
- validated examples
- regression test suite
- reproducible output files
- installation instructions

---

## Deferred / research topics
These are intentionally postponed until the kernel is strong:

- detailed porous stuffing / fibrous fill physics
- finite-baffle diffraction improvements
- mutual radiation refinement
- structural coupling
- nonlinear behavior
- BEM / 3D acoustics
- crossover library expansion
- machine-learning surrogate models

---

## Guiding principle
At every stage, we prefer:

- small validated steps
- working examples
- test coverage
- reproducible reference comparisons

over ambitious but unverified feature growth.
