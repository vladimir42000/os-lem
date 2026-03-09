# Architecture

## Overview
The software is organized as a layered system:

1. input parsing
2. model object creation
3. solver-element expansion
4. frequency-domain system assembly
5. numerical solve
6. post-processing
7. export / plotting

The architecture should separate:

- **user-facing model description**
- **internal computational representation**
- **numerical solver**
- **post-processing and plotting**

This separation is essential for future growth.

---

## Layer 1 - User model
The user writes a high-level model file describing:

- driver
- enclosure volumes
- ducts
- horn / line sections
- resonators
- radiation terminations
- observation requests

This layer should be human-readable and stable.

Examples of user-level objects:
- `driver`
- `volume`
- `duct`
- `tapered_line`
- `conical_section`
- `exponential_section`
- `side_branch`
- `radiator`

Important rule:  
User-level objects do **not** have to match one-to-one with solver primitives.

---

## Layer 2 - Internal model representation
The parser converts input into a structured internal model.

Responsibilities:
- validate syntax
- validate required fields
- resolve references
- assign nodes
- expand convenience objects if necessary

This layer is still symbolic / structural, not yet numerical.

Example:  
A user-defined exponential horn may become a set of smaller internal line segments.

---

## Layer 3 - Solver primitives
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

## Layer 4 - Frequency-domain assembly
For each frequency point:

1. compute each primitive's complex parameters
2. assemble contributions into the global system
3. apply sources and boundary conditions
4. solve for unknown state variables

The exact unknown set will be defined later in `solver_math.md`, but it will likely include nodal or branch-domain quantities such as:
- voltage / current
- force / velocity
- pressure / volume velocity

---

## Layer 5 - Numerical solve
Solve the assembled complex linear system at each frequency.

Requirements:
- deterministic
- numerically stable for typical loudspeaker problems
- easy to debug
- easy to instrument for regression tests

The solver layer should not know anything about plotting or GUI.

---

## Layer 6 - Post-processing
Convert solved state variables into engineering outputs such as:
- SPL
- phase
- impedance
- excursion
- cone velocity
- port velocity
- acoustic power estimates
- group delay

Later additions:
- pressure distribution along a line
- volume-velocity distribution along a line
- derived placement diagnostics for resonators / damping

---

## Layer 7 - Export and plotting
Output should be available in machine-readable and human-readable forms.

Machine-readable:
- CSV
- JSON metadata

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
- load YAML / JSON
- schema validation
- convert to internal model objects

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
- internal field reconstruction later

### `plots/`
- static curve generation
- later interactive plotting hooks

### `io/`
- reading data files
- writing CSV / JSON outputs
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
