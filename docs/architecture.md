# Architecture

## Overview
The software is organized as a layered system:

1. input parsing
2. model object creation
3. normalization to canonical internal representation
4. solver-element expansion
5. frequency-domain system assembly
6. numerical solve
7. post-processing
8. export / plotting

The architecture should separate:

- **user-facing model description**
- **internal computational representation**
- **numerical solver**
- **post-processing and plotting**

This separation is essential for future growth.

---

## Layer 1 - User model
The user writes a high-level model file describing:

- one driver
- acoustic volumes
- ducts
- 1D waveguide sections
- radiation terminations
- observation requests

This layer should be human-readable and stable.

Examples of user-level objects in frozen v1:
- `driver`
- `volume`
- `duct`
- `waveguide_1d`
- `radiator`

Important rules:
- user-level objects do **not** have to match one-to-one with solver primitives
- resonators and side branches are represented by topology, not by separate primitive object types
- user-facing driver entry may be classical T/S style or explicit electromechanical style, but both normalize to one internal canonical representation

---

## Layer 2 - Internal model representation
The parser converts input into a structured internal model.

Responsibilities:
- validate syntax
- validate required fields
- parse supported units and normalize to SI
- resolve references
- assign nodes
- normalize driver parameters
- expand convenience objects if necessary

This layer is still symbolic / structural, not yet numerical.

Examples:
- a user-defined `ts_classic` driver becomes a normalized explicit electromechanical driver description
- a user-defined `waveguide_1d` may become a set of smaller internal line segments

---

## Layer 3 - Canonical internal representation
Before numerical expansion, the model is normalized to a controlled internal representation.

For drivers, the canonical internal form is:
- `Re`
- `Le`
- `Bl`
- `Mms`
- `Cms`
- `Rms`
- `Sd`

For acoustics, all user inputs are normalized to SI before numerical evaluation.

This layer is important because it lets the solver work with one clean representation even if the user entered parameters in different accepted schemas.

---

## Layer 4 - Solver primitives
The internal model is converted into numerical solver elements.

Typical primitive categories:
- electrical impedance element
- electro-mechanical transducer element
- acoustic compliance
- acoustic inertance
- acoustic resistance
- transmission-line / two-port segment
- radiation termination
- source / observation definitions

These primitives are what actually contribute to the system matrix.

---

## Layer 5 - Frequency-domain assembly
For each frequency point:

1. compute each primitive's complex parameters
2. assemble contributions into the global system
3. apply sources and boundary conditions
4. solve for unknown state variables

The exact unknown set will be defined later in `solver_math.md`, but it will follow a node-based linear frequency-domain formulation with acoustic node pressures as primary acoustic unknowns and auxiliary unknowns added as needed.

---

## Layer 6 - Numerical solve
Solve the assembled complex linear system at each frequency.

Requirements:
- deterministic
- numerically stable for typical loudspeaker problems
- easy to debug
- easy to instrument for regression tests

The solver layer should not know anything about plotting or GUI.

---

## Layer 7 - Post-processing
Convert solved state variables into engineering outputs such as:
- SPL
- phase
- impedance
- excursion
- cone velocity
- port / element velocity
- node pressure
- group delay
- line pressure / volume-velocity / particle-velocity profiles at chosen frequencies

Post-processing is also responsible for:
- complex summation of multiple radiator contributions
- phase unwrapping where required
- group-delay derivation from referenced observations

---

## Layer 8 - Export and plotting
Output should be available in machine-readable and human-readable forms.

Machine-readable:
- CSV
- metadata / summaries

Human-readable:
- static plots
- later GUI plots

This layer must remain separate from the core solver.

---

## Proposed Python package layout

```text
src/os_lem/
  __init__.py
  cli.py
  parser/
  model/
  elements/
  solver/
  postprocess/
  plots/
  io/
```

## Responsibilities

### `parser/`
- load YAML / JSON later if added
- schema validation
- units parsing and SI normalization
- convert to internal model objects
- driver normalization and consistency checks

### `model/`
- definitions of user-level and internal model objects
- node and connection logic
- model validation helpers

### `elements/`
- primitive element definitions
- parameter evaluation functions
- matrix contribution methods

### `solver/`
- frequency grid
- matrix assembly
- linear solves
- result containers

### `postprocess/`
- impedance extraction
- SPL / phase
- group delay
- excursion
- node pressure
- internal line-profile reconstruction

### `plots/`
- static curve generation
- later interactive plotting hooks

### `io/`
- writing CSV and metadata outputs
- later measured-data import

---

## Core design decisions

### 1. CLI-first
The command-line interface is the primary interface in early development.

Reason:
- reproducibility
- scriptability
- testability
- optimization compatibility

### 2. High-level input, simple internals
The user should define natural objects, but the solver should operate on a controlled set of primitives.

### 3. Linear first
The initial engine is strictly linear and frequency-domain.

### 4. Validation-driven development
Every major new object type must arrive with:
- at least one example
- at least one regression test
- at least one reference comparison

### 5. Extensible but not over-generalized
Architecture should allow future growth without overengineering v1.

---

## Non-goals of the architecture
The following are intentionally not first-class architecture targets in v1:
- full multiphysics coupling
- BEM mesh handling
- nonlinear time-domain simulation
- advanced porous-media solvers
- distributed structural FEM
- measured driver import
