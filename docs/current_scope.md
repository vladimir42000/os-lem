# os-lem current scope

## Released public baseline

- latest released version: `v0.1.0`
- released branch of record: `main`

The current public baseline is the tagged `v0.1.0` foundation release.

---

## Current implemented kernel subset

At the current working checkpoint, the implemented assembled subset is:

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

## Released / validated confidence scope

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

## Current working-line conclusion beyond the released baseline

The working repo has advanced beyond the `v0.1.0` release story through the later debug lineage.

Current best-supported interpretation:

- `front/raw` is broadly credible on the current observation debug line
- the remaining mismatch is localized to `mouth/port` observable semantics
- the best next patch is a bounded observation-layer change
- current preferred candidate: `mouth_directivity_only`
- `front` must remain unchanged during that patch

This section describes current working-line truth, not an already released capability claim.

---

## Current deferred capabilities

Not yet released or still intentionally deferred:

- broad transmission-line workflow claims
- broad Hornresp parity claims
- broad AkAbak parity claims
- conical lossy `waveguide_1d`
- thermo-viscous auto-derived losses
- passive radiator support
- multi-driver support
- stable long-term public API
- product-grade frontend

---

## Scope rule for the next patch

The next technical patch must not reopen broad debugging.
It must stay at the observation layer and preserve the already-credible `front` path.
