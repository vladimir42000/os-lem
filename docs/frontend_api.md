# Frontend API contract v1

This document freezes the first frontend-facing integration contract on top of `os_lem.api`.
It is intentionally narrower than the full kernel.

## Stable entry points

- `os_lem.api.run_simulation(model_dict, frequencies_hz)`
- `os_lem.api.get_frontend_contract_v1()`

`run_simulation` remains the execution entry point.
`get_frontend_contract_v1()` is the machine-readable contract manifest that frontend code can inspect during integration tests or startup validation.

## Stable input subset

Driver models declared stable for frontend use:

- `ts_classic`
- `em_explicit`

Element types declared stable for frontend use:

- `volume`
- `duct`
- `waveguide_1d` with `profile: conical`
- `radiator`

Radiator models declared stable:

- `infinite_baffle_piston`
- `unflanged_piston`
- `flanged_piston`

Stable observation types:

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

## Stable result surface

`run_simulation()` returns `SimulationResult` with stable frontend fields:

- `model`
- `system`
- `sweep`
- `warnings`
- `series`
- `units`
- `observation_types`

Stable convenience properties:

- `frequencies_hz`
- `zin_complex_ohm`
- `zin_mag_ohm`
- `cone_velocity_m_per_s`
- `cone_displacement_m`
- `cone_excursion_mm`

Stable `LineProfileResult` fields:

- `frequency_hz`
- `quantity`
- `x_m`
- `values`

## Stable workflows

The frozen v1 frontend contract only treats these workflows as stable:

1. closed box with one front radiator and one rear volume
2. one rear conical line ending in one mouth radiator

The canonical examples for those workflows live in `examples/frontend_contract_v1/`.

## Experimental openings

The following kernel capabilities are explicitly **not** part of frontend contract v1:

- parallel split/recombine bundles between the same two nodes
- true interior acoustic junctions with more than two incident branches
- branched horn skeletons with multiple leaf mouth radiators
- shared-exit recombination after multiple upstream branch legs
- dual-junction split/merge horn skeletons

Those features may remain available for internal or experimental use, but frontend code must not rely on them as frozen behavior.

## Future update rule

If a future patch changes any of the following:

- supported element types
- supported observation types
- result surface
- example-worthy workflows
- parser fields used by the facade

then that patch must do exactly one of these:

1. update the manifest returned by `get_frontend_contract_v1()`, update this document, update `docs/input_format.md`, update `docs/frontend_handoff.md`, and update frontend-contract tests
2. explicitly declare: `No frontend contract change`
