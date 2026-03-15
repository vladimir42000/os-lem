# os-lem current scope

## Current released baseline

- latest released version: `v0.1.0`
- released branch of record: `main`
- current known green suite on the released baseline: `104 passed`

The current public baseline is the tagged `v0.1.0` foundation release.

---

## Current implemented kernel subset

At the current released checkpoint, the implemented assembled subset is:

- `volume`
- `duct`
- `radiator`
- minimal assembled `waveguide_1d`

The solver currently supports:

- one driver
- coupled electro-mechano-acoustic solve
- frequency sweep

---

## Current available outputs

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

Current observation handling also includes:

- explicit observation `radiation_space` support for `spl` and `spl_sum`, decoupled from the radiator mechanical impedance model

Current integration support also includes:

- provisional `os_lem.api` frontend facade for dict-based runs and ready-to-plot common outputs

---

## Current validated/released scope

The released `v0.1.0` confidence scope covers:

- the corrected Phase 4 solver baseline
- corrected `ts_classic` canonical motor normalization (`Bl`) against the standard T/S relation
- corrected closed-box baffled-radiator low-frequency reactance behavior through the Struve-path fix
- corrected bass-reflex SPL observation behavior after decoupling observation `radiation_space` from the radiator impedance model
- simple assembled acoustic participation of `waveguide_1d`
- waveguide constant-area segmentation-invariance sanity
- waveguide conical refinement sanity
- minimal `waveguide_1d` pressure-profile endpoint consistency and reversal behavior
- minimal `waveguide_1d` volume-velocity-profile endpoint consistency and reversal behavior
- minimal `waveguide_1d` particle-velocity-profile endpoint consistency and reversal behavior
- cross-profile identity checks for `pressure`, `volume_velocity`, and `particle_velocity`
- cylindrical special-case consistency for `particle_velocity = volume_velocity / area_const`
- exact cylindrical lossy reference agreement for entrance behavior and sampled profiles within the frozen cylindrical-loss boundary
- provisional `os_lem.api` facade behavior for the currently exposed integration path

---

## Current deferred capabilities

Not yet implemented, not yet frozen, or not yet claimed as released project scope:

- passive radiator
- multi-driver support
- crossover / electrical-network expansion
- conical lossy `waveguide_1d`
- thermo-viscous auto-derived losses
- broad horn / transmission-line workflow claims
- broad AkAbak parity claims
- broad Hornresp parity claims
- frozen long-term public frontend/API contract
- broad GUI / interactive frontend product claims

---

## Current next-step caution

The current scope document describes the released `v0.1.0` baseline.

It does **not** claim that the next release target is already implemented.

The next release cycle must re-establish repo truth through a bounded investigation before widening claims.
