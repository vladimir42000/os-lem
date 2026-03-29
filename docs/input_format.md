# Frontend input format v1

This document describes the input subset that is stable for external frontend integration.
It does not attempt to describe every kernel-only or experimental topology opening.

## Top-level structure

A frontend-stable model dictionary contains:

- `meta`
- `driver`
- `elements`
- `observations`

`output` may exist in older internal material, but the frontend contract v1 does not require it.

## Driver block

Required frontend-stable fields for `model: ts_classic`:

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

Required frontend-stable fields for `model: em_explicit`:

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

Optional stable voltage field:

- `source_voltage` or `source_voltage_rms`

## Stable element blocks

### volume

Required fields:

- `id`
- `type: volume`
- `node`
- `value`

### duct

Required fields:

- `id`
- `type: duct`
- `node_a`
- `node_b`
- `length`
- `area`

### waveguide_1d

Required fields:

- `id`
- `type: waveguide_1d`
- `node_a`
- `node_b`
- `length`
- `area_start`
- `area_end`
- `profile: conical`

Optional stable fields:

- `segments`
- `loss`

### radiator

Required fields:

- `id`
- `type: radiator`
- `node`
- `model`
- `area`

Stable models:

- `infinite_baffle_piston`
- `unflanged_piston`
- `flanged_piston`

## Stable observation blocks

The stable frontend observation types are:

- `input_impedance`
- `cone_velocity`
- `cone_displacement`
- `node_pressure`
- `spl`
- `spl_sum`
- `element_volume_velocity`
- `element_particle_velocity`
- `line_profile`
- `group_delay`

For `line_profile`, stable quantities are:

- `pressure`
- `volume_velocity`
- `particle_velocity`

## Stable topology envelope

Frontend contract v1 freezes only these example-worthy topology envelopes:

- closed box with front radiator + rear volume
- one rear conical line with one mouth radiator

More advanced branching, recombination, or split/merge structures may exist in the kernel, but they are outside the stable frontend contract unless later promoted explicitly.
