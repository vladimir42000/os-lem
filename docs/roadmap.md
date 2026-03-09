# Roadmap

## v0.1 - Project foundation
Goal: establish the project structure and technical direction.

Deliverables:
- repository structure
- documentation skeleton
- input-file philosophy
- solver architecture draft
- validation plan draft

## v0.2 - Minimal solver kernel
Goal: solve simple frequency-domain electromechanical-acoustic networks.

Deliverables:
- complex frequency sweep engine
- driver electromechanical model
- basic acoustic compliance / mass / resistance elements
- node / branch assembly
- electrical impedance output
- basic SPL output for simple radiator case

## v0.3 - First usable enclosure models
Goal: simulate basic loudspeaker boxes.

Deliverables:
- sealed-box support
- vented-box support
- simple duct / tube element
- radiation termination approximation
- plots:
  - impedance
  - SPL
  - phase
  - cone displacement
  - group delay

## v0.4 - Transmission-line / TQWP support
Goal: support 1D line-based enclosures.

Deliverables:
- line section / duct chain support
- taper by start/end area
- side-branch resonator support
- examples:
  - straight TL
  - tapered TQWP
  - resonator-assisted line

## v0.5 - High-level geometry convenience
Goal: improve user input while keeping solver internals simple.

Deliverables:
- direct user-level shape objects:
  - straight duct
  - conical section
  - exponential section
  - tapered line
- automatic internal segmentation
- segmentation controls

## v0.6 - Internal field inspection
Goal: make the solver more useful for resonator and stuffing placement.

Deliverables:
- pressure distribution along 1D path at chosen frequency
- volume-velocity distribution along 1D path at chosen frequency
- plots for selected frequencies
- export of sampled field data

## v0.7 - Optimization interface
Goal: enable automated search of parameters.

Deliverables:
- parameter sweep framework
- objective-function framework
- hooks for SciPy optimization
- support for batch runs and machine-readable result export

## v0.8 - Measured driver support
Goal: move beyond idealized T/S-only drivers.

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
