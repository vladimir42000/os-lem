# os-lem status

## Current development status

- Active branch: `feature/session6-first-coupled-assembly`
- Stable baseline commit: `b31df3d`
- Stable baseline tag: `baseline-session5-recovered`
- Current test status: `51 passed`
- Active phase: **Phase 3 — validation of the current solver path**
- Most recent completed milestone: **Phase 2 — sweep and first observables**

## What is implemented

### Recovered foundation
- parser / normalization pipeline
- frozen v1 input subset
- primitive element evaluation for:
  - volume
  - duct
  - waveguide_1d
  - radiator

### Coupled solver path already implemented
- minimal assembly layer in `src/os_lem/assemble.py`
- deterministic topology-resolved assembled representation
- support in assembly for:
  - `volume`
  - `duct`
  - `radiator`
- explicit rejection of `waveguide_1d` in assembly for now
- acoustic nodal admittance matrix builder in `src/os_lem/solve.py`
- matrix stamping for:
  - volume shunt admittance
  - radiator shunt admittance
  - duct branch admittance
- coupled electromechano-acoustic one-frequency linear solve
- frequency sweep over the current coupled solver
- solved outputs:
  - node pressures
  - voice-coil current
  - cone velocity
  - cone displacement
  - input impedance
- first one-radiator observation helpers:
  - complex far-field pressure
  - SPL in dB

## Current scope boundary

### In scope now
- validation of the current assembled subset:
  - `volume`
  - `duct`
  - `radiator`
- internal physics sanity checks
- limited external comparison for simple cases that truly overlap current scope
- preservation of passing tests
- small, reviewable patches only

### Explicitly out of scope for the current patch series
- `waveguide_1d` assembly
- multi-driver support
- broad architecture rewrite
- speculative refactors
- Hornresp parity claims outside the overlapping simple subset
- broad external validation campaign over unsupported topologies

## Immediate next step

Start Phase 3 with focused validation patches:
- seal the validation contract in docs
- add internal physics validation cases for supported simple topologies
- add limited external reference comparison only where scope matches clearly
- keep docs aligned with exact implemented scope

## Known limitations

- `waveguide_1d` exists as an evaluated primitive but is not yet assembled
- active observation helpers remain in `src/os_lem/solve.py`
- no broader topology support yet beyond the current assembled subset
- current solver scope is intentionally narrow and should not yet be treated as Hornresp-equivalent

## Working method

- development proceeds in small patches
- each patch must preserve or intentionally extend tests
- code changes are applied locally by the operator
- repository docs act as the long-term project memory
