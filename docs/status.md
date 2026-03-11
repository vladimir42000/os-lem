# os-lem status

## Current development status

- Active branch: `feature/session6-first-coupled-assembly`
- Stable baseline commit: `b31df3d`
- Stable baseline tag: `baseline-session5-recovered`
- Current phase milestone tag: `phase1-first-coupled-solve`
- Current test status: `49 passed`
- Active phase: **Phase 2 — sweep and first observables**
- Most recent completed milestone: **Phase 1 — first coupled one-frequency solver**

## What is implemented

### Recovered foundation
- parser / normalization pipeline
- frozen v1 input subset
- primitive element evaluation for:
  - volume
  - duct
  - waveguide_1d
  - radiator
- recovered and passing baseline from Session 5

### Phase 1 completed
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
- first coupled electromechano-acoustic one-frequency linear system
- first one-frequency solve returning:
  - node pressures
  - voice-coil current
  - cone velocity
  - cone displacement
- first sweep helper over the one-frequency coupled solve
- first sweep result container returning arrays for:
  - node pressures
  - voice-coil current
  - cone velocity
  - cone displacement
  - input impedance
- first one-radiator observation helpers returning:
  - complex far-field pressure
  - SPL in dB


## Current scope boundary

### In scope now
- frequency sweep over the first coupled solver
- first user-facing outputs:
  - input impedance
  - cone velocity
  - cone displacement
  - one-radiator SPL
- preservation of passing tests
- small, reviewable patches only

### Explicitly out of scope for the current patch series
- `waveguide_1d` assembly
- multi-driver support
- broad architecture rewrite
- speculative refactors
- Akabak parity claims
- broad external validation campaign

## Immediate next step

Continue Phase 2 with the next small patch:
- add frozen numerical reference checks for first output values
- decide whether a minimal export/observation layer is needed now or later
- keep docs aligned with exact implemented scope

## Known limitations

- `waveguide_1d` exists as an evaluated primitive but is not yet assembled
- no general output/export pipeline yet beyond direct helper functions
- no broader validation yet against external reference cases
- current coupled solver scope is intentionally minimal

## Working method

- development proceeds in small patches
- each patch must preserve or intentionally extend tests
- code changes are applied locally by the operator
- repository docs act as the long-term project memory
