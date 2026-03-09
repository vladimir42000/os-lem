# Input format

## Goal
The input format should be:

- human-readable
- diff-friendly in Git
- easy to parse
- explicit rather than magical
- suitable for scripting and automation

Preferred initial format:
- YAML

JSON support may be added later if useful.

---

## Design principles

### 1. Clear object definitions
Each object should have:
- an `id`
- a `type`
- its parameters
- its connections / nodes where relevant

### 2. Explicit units
Units should be documented and consistent.

Initial convention:
- SI units internally
- user input in SI unless stated otherwise

### 3. Stable schema
The schema should evolve carefully to avoid breaking example files.

### 4. Separate model and run settings
A model definition should be distinct from simulation settings and output requests.

---

## Top-level file structure

Proposed sections:

- `meta`
- `simulation`
- `driver`
- `elements`
- `observations`
- `output`

---

## Example skeleton

```yaml
meta:
  name: "basic_tqwp"
  author: "user"
  version: 1

simulation:
  f_start_hz: 10
  f_stop_hz: 2000
  points: 500
  spacing: log

driver:
  id: drv1
  model: ts_basic
  Re: 5.8
  Le: 0.0004
  Bl: 6.2
  Mms: 0.012
  Cms: 0.0011
  Rms: 0.9
  Sd: 0.013

elements:
  - id: rear_volume
    type: volume
    node_a: rear_chamber
    value_m3: 0.008

  - id: line_1
    type: tapered_line
    node_a: rear_chamber
    node_b: mouth
    length_m: 1.45
    area_start_m2: 0.012
    area_end_m2: 0.032

  - id: mouth_rad
    type: radiator
    node_a: mouth
    radiation: unflanged_piston

observations:
  - id: zin
    type: input_impedance
    target: drv1

  - id: spl_main
    type: spl
    target: mouth_rad
    distance_m: 1.0

output:
  folder: "results/basic_tqwp"
  write_csv: true
  write_plots: true
```

---

## First supported object classes for v1

### Driver
Initial modes:
- `ts_basic`
- later `electromechanical_explicit`
- later `measured`

Required fields for initial driver mode:
- `Re`
- `Le`
- `Bl`
- `Mms`
- `Cms`
- `Rms`
- `Sd`

Optional later convenience input:
- classical T/S conversion helpers

---

### Acoustic elements
Initial target set:
- `volume`
- `duct`
- `tapered_line`
- `side_branch`
- `radiator`

Possible later additions:
- `conical_section`
- `exponential_section`
- `acoustic_resistance`
- `acoustic_mass`
- `acoustic_compliance`

---

## Connection philosophy
Connections should be explicit.

Two possible approaches exist:

### A. Node-based
Each element declares:
- `node_a`
- `node_b`

This is flexible and consistent with network solvers.

### B. Containment/path-based
Useful for simple line definitions but less general.

Initial recommendation:
- use **node-based connections**

This supports future arbitrary topologies.

---

## Observation requests
The user should explicitly request outputs.

Initial observation types:
- `input_impedance`
- `spl`
- `phase`
- `cone_displacement`
- `cone_velocity`
- `group_delay`

Later:
- `pressure_profile`
- `velocity_profile`

---

## Output control
The user should be able to request:
- CSV export
- plot export
- frequency-response metadata

Later:
- JSON structured result bundles
- GUI project save files

---

## Validation requirements for the input format
Before freezing the schema, it must be tested on:
- sealed box
- vented box
- simple TL
- tapered TQWP
- side-branch resonator example

---

## Open questions
These will be resolved later and logged in `decision_log.md`:

1. exact driver schema for v1
2. whether `tapered_line` is a true primitive or always expanded internally
3. whether radiation models are object types or options on endpoints
4. naming conventions for nodes and observations
5. whether optional units syntax should be supported later
