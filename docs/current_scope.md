# os-lem current scope

## Released public baseline

- latest released version: `v0.3.0`
- released branch of record: `main`

The current public baseline is the tagged `v0.3.0` release.

---

## Current implemented kernel subset on the working line

At the current working checkpoint, the implemented assembled subset is:

- `volume`
- `duct`
- `radiator`
- `waveguide_1d`

The solver currently supports:

- one driver
- coupled electro-mechano-acoustic solve
- frequency sweep

---

## Current available outputs on the working line

Current available outputs include:

- input impedance
- cone velocity
- cone displacement
- one-radiator far-field pressure
- one-radiator SPL
- waveguide endpoint flow export
- waveguide endpoint particle-velocity export
- element volume-velocity export for `duct`, `radiator`, and `waveguide_1d` endpoints
- element particle-velocity export for `duct`, `radiator`, and `waveguide_1d` endpoints
- `waveguide_1d` `line_profile` export for `pressure`
- `waveguide_1d` `line_profile` export for `volume_velocity`
- `waveguide_1d` `line_profile` export for `particle_velocity`

Current observation handling also includes:

- explicit observation `radiation_space` support for `spl` and `spl_sum`, decoupled from the radiator mechanical impedance model

Current integration support also includes:

- provisional `os_lem.api` frontend facade for dict-based runs and ready-to-plot common outputs

---

## Released confidence scope

The released `v0.3.0` confidence scope covers:

- the released `v0.1.0` kernel baseline and its conservative capability boundaries
- corrected `ts_classic` canonical motor normalization (`Bl`) against the standard T/S relation
- corrected closed-box baffled-radiator low-frequency reactance behavior through the Struve-path fix
- corrected bass-reflex SPL observation behavior after decoupling observation `radiation_space` from the radiator impedance model
- assembled `waveguide_1d`
- promoted element observables through the supported API/output surface
- parser validation for incomplete promoted observable requests
- end-to-end facade regression coverage for invalid promoted element-observable requests

---

## Current working-line confidence beyond the released baseline

The current `v0.4.0` working line additionally includes:

- bounded lossy conical `waveguide_1d`
- preserved endpoint flow and particle-velocity export on the lossy conical path
- preserved `line_profile` export for `pressure`, `volume_velocity`, and `particle_velocity` on the lossy conical path
- focused conical-loss validation
- one maintained conical-line hero example
- segmentation-refinement validation for the official conical example

This is working-line milestone truth, not yet a released public claim.

---

## Current deferred capabilities

Not yet released or still intentionally deferred:

- broad transmission-line workflow claims
- broad Hornresp parity claims
- broad AkAbak parity claims
- thermo-viscous auto-derived losses beyond the current bounded waveguide-loss support
- passive radiator support
- multi-driver support
- stable long-term public API
- product-grade frontend
- branching / recombination topology for tapped-horn-class graphs

---

## Scope rule for the next patch

The next patch must stay in milestone-close bookkeeping.
It must not reopen capability scope beyond the landed `v0.4.0` waveguide campaign.
