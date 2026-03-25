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
- an `id` where appropriate
- a `type` where appropriate
- its parameters
- its explicit node connections where relevant

### 2. Canonical internal form
The parser may accept a small number of user-facing schemas and engineering units, but it must normalize everything to one internal SI-based representation before numerical solving.

### 3. Stable schema
The schema should evolve carefully to avoid breaking example files.

### 4. Separate model and run settings
A model definition should be distinct from simulation settings and output requests.

---

## Frozen v1 top-level structure

The v1 top-level sections are:

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
  f_start: 10 Hz
  f_stop: 2000 Hz
  points: 500
  spacing: log

driver:
  id: drv1
  model: ts_classic
  Re: 5.8 ohm
  Le: 0.4 mH
  Fs: 45 Hz
  Qes: 0.42
  Qms: 3.8
  Vas: 18 l
  Sd: 132 cm2
  node_front: front
  node_rear: rear

elements:
  - id: front_rad
    type: radiator
    node: front
    model: infinite_baffle_piston
    area: 132 cm2

  - id: rear_volume
    type: volume
    node: rear
    value: 8 l

  - id: line_1
    type: waveguide_1d
    node_a: rear
    node_b: mouth
    length: 1.45 m
    area_start: 120 cm2
    area_end: 320 cm2
    profile: conical
    segments: 12

  - id: mouth_rad
    type: radiator
    node: mouth
    model: unflanged_piston
    area: 320 cm2

observations:
  - id: zin
    type: input_impedance
    target: drv1

  - id: spl_driver
    type: spl
    target: front_rad
    distance: 1 m

  - id: spl_mouth
    type: spl
    target: mouth_rad
    distance: 1 m

  - id: spl_total
    type: spl_sum
    terms:
      - target: front_rad
        distance: 1 m
      - target: mouth_rad
        distance: 1 m

  - id: xcone
    type: cone_displacement
    target: drv1

  - id: p_rear
    type: node_pressure
    target: rear

  - id: line_p_200
    type: line_profile
    target: line_1
    frequency: 200 Hz
    quantity: pressure
    points: 100

  - id: gd_total
    type: group_delay
    target: spl_total

output:
  folder: "results/basic_tqwp"
  write_csv: true
  write_plots: true
```

---

## Driver

v1 supports one driver object and two accepted user-facing input modes:

- `model: ts_classic`
- `model: em_explicit`

Both normalize internally to the same canonical explicit representation:
- `Re`
- `Le`
- `Bl`
- `Mms`
- `Cms`
- `Rms`
- `Sd`

### `model: ts_classic`
Required fields:
- `id`
- `model`
- `Re`
- `Le`
- `Fs`
- `Qes`
- `Qms`
- `Vas`
- `Sd`
- `node_front`
- `node_rear`

### `model: em_explicit`
Required fields:
- `id`
- `model`
- `Re`
- `Le`
- `Bl`
- `Mms`
- `Cms`
- `Rms`
- `Sd`
- `node_front`
- `node_rear`

### Mixed classical and explicit fields
If both classical and explicit descriptions are present:
- the parser may accept the driver with a warning if the derived and declared values agree within tolerance
- the parser must reject the driver if they disagree beyond tolerance

### Notes
- exactly one logical driver object is supported in v1
- measured driver import is postponed
- all accepted inputs are normalized internally before solving

---

## Core acoustic element types in v1

The supported user-facing acoustic element types are:

- `volume`
- `duct`
- `waveguide_1d`
- `radiator`

`side_branch` and `resonator` are not primitive object types in v1. They are built by topology from the core elements.

---

## Connection philosophy

Connections are explicit and node-based.

Naming rules:

### 1-port elements
Use:
- `node`

Examples:
- `volume`
- `radiator`

### 2-port elements
Use:
- `node_a`
- `node_b`

Examples:
- `duct`
- `waveguide_1d`

### Driver
Use:
- `node_front`
- `node_rear`

This keeps the network model explicit and general.

---

## Element definitions

### `volume`
Required fields:
- `id`
- `type: volume`
- `node`
- `value`

### `duct`
Required fields:
- `id`
- `type: duct`
- `node_a`
- `node_b`
- `length`
- `area`

Optional fields:
- `loss` (reserved and unsupported in the current checkpoint)

### `waveguide_1d`
Required fields:
- `id`
- `type: waveguide_1d`
- `node_a`
- `node_b`
- `length`
- `area_start`
- `area_end`
- `profile: conical`

Optional fields:
- `segments`
- `loss`

Current MVP loss boundary:
- `waveguide_1d.loss` is user-specified distributed loss in nepers per meter
- loss is supported for the current segmented `profile: conical` implementation, including the cylindrical special case where `area_start == area_end`
- this is a bounded empirical segmented-waveguide model, not a broad exact conical-wave or horn-parity claim
- thermo-viscous auto-derived losses remain deferred

#### Definition of `profile: conical`
In v1, `conical` means the equivalent circular radius varies linearly with axial position.

Therefore:
- radius is linear in position
- diameter is linear in position
- cross-sectional area is generally not linear in position

Special case:
- if `area_start == area_end`, the section is cylindrical

Later profile families such as exponential, parabolic, tractrix, or Le Cléac'h may be added without changing the top-level `waveguide_1d` object type.

### `radiator`
Required fields:
- `id`
- `type: radiator`
- `node`
- `model`
- `area`

Allowed v1 radiator models:
- `infinite_baffle_piston`
- `unflanged_piston`
- `flanged_piston`

Radiators remain explicit separate elements rather than endpoint flags. This allows independent observation of driver, port, and line-mouth contributions.

---

## Observations

The user explicitly requests outputs.

Supported v1 observation types:
- `input_impedance`
- `spl`
- `spl_sum`
- `cone_displacement`
- `cone_velocity`
- `element_volume_velocity`
- `element_particle_velocity`
- `node_pressure`
- `line_profile`
- `group_delay`

### Important conventions
- `phase` is not a separate observation type
- phase is exported automatically for complex-valued observations where applicable
- `group_delay` references another named complex observation

### `spl`
Observe the contribution of one radiator.

Typical fields:
- `id`
- `type: spl`
- `target`
- `distance`
- optional `delay`

### `spl_sum`
Observe the complex sum of multiple radiator contributions.

Required fields:
- `id`
- `type: spl_sum`
- `terms`

Each term references a radiator contribution, typically with its own `distance` and optional `delay`.

This is important because driver and port must be observable independently and also combined with phase interaction.

### `node_pressure`
Observe pressure at a named acoustic node.

Typical fields:
- `id`
- `type: node_pressure`
- `target`

### `line_profile`
Observe a sampled distribution along one line object at one chosen frequency.

Required fields:
- `id`
- `type: line_profile`
- `target`
- `frequency`
- `quantity`
- `points`

Allowed v1 quantities:
- `pressure`
- `volume_velocity`
- `particle_velocity`

This observation exists specifically to support line understanding and resonator-placement work.

### `group_delay`
Observe group delay derived from another named complex observation.

Required fields:
- `id`
- `type: group_delay`
- `target`

Group delay is computed from the unwrapped phase of the referenced observation using numerical differentiation with respect to frequency.

---

## Units

### Internal rule
The solver kernel uses SI internally.

### User-facing v1 unit support
The parser may accept a small controlled whitelist of engineering units and normalize them to SI.

Recommended v1 whitelist:
- length: `m`, `cm`, `mm`
- area: `m2`, `cm2`
- volume: `m3`, `l`
- frequency: `Hz`
- time: `s`, `ms`
- inductance: `H`, `mH`
- resistance: `ohm`

Dimensionless quantities such as `Qes` and `Qms` remain unitless.

Examples:
- `Sd: 132 cm2`
- `Vas: 18 l`
- `distance: 100 cm`
- `delay: 0.6 ms`

This is a convenience for input only. Internally everything is normalized before solving.

---

## Validation requirements for the input format
Before implementation is considered stable, the schema must be exercised on at least:
- free-air driver
- sealed box
- vented box
- simple straight line
- tapered TQWP / conical line case
- resonator example built from core elements

---

## v1 strictness rules
- missing required fields are hard errors
- unknown fields are hard errors
- unsupported element or observation types are hard errors
- contradictory mixed driver data beyond tolerance is a hard error

These strict rules are intentional in v1 to make validation easier and avoid silent mistakes.
