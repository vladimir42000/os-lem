# os-lem current scope

## Current implemented kernel subset

At the current checkpoint, the implemented assembled subset is:

- `volume`
- `duct`
- `radiator`
- minimal assembled `waveguide_1d`

The solver currently supports:
- one driver
- coupled electro-mechano-acoustic solve
- frequency sweep

Current available outputs include:
- input impedance
- cone velocity
- cone displacement
- one-radiator far-field pressure
- one-radiator SPL
- waveguide endpoint flow export
- waveguide endpoint particle-velocity export
- minimal `waveguide_1d` `line_profile` export for `pressure`
- minimal `waveguide_1d` `line_profile` export for `volume_velocity`
- minimal `waveguide_1d` `line_profile` export for `particle_velocity`

## Current validated scope

Validated confidence currently covers:
- the corrected Phase 4 solver baseline
- simple assembled acoustic participation of `waveguide_1d`
- waveguide constant-area segmentation-invariance sanity
- waveguide conical refinement sanity
- minimal `waveguide_1d` pressure-profile endpoint consistency and reversal behavior
- minimal `waveguide_1d` volume-velocity profile endpoint consistency and reversal behavior
- minimal `waveguide_1d` particle-velocity profile endpoint consistency and reversal behavior

## Current deferred capabilities

Not yet implemented or not yet supported as project claims:

- distributed losses
- passive radiator
- multi-driver support
- crossover/electrical-network expansion
- broad AkAbak parity claims
- broad Hornresp parity claims
- GUI / interactive frontend

## Current interpretation

`os-lem` is currently a narrow but real loudspeaker LEM kernel.
It is not yet a broad product.
It should not be described as a Hornresp or AkAbak replacement at the current checkpoint.

## Current caution

Do not confuse:
- implemented subset
- internally validated subset
- externally validated subset
- future target capabilities
