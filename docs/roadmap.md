# os-lem roadmap

## Project intent

`os-lem` is an open, scriptable lumped-element loudspeaker / enclosure simulator with a development style inspired by Akabak-era workflows, but implemented as a clean, testable Python codebase with disciplined incremental growth.

The roadmap is both phase-based and release-based:

- phases explain technical evolution
- releases explain what is honest to expose externally

Latest released baseline:
- `v0.1.0` on `main`

Current active planning target:
- `v0.2.0` — offset-line observation-contract stabilization

---

## Historical phase record

### Phase 0 — recovery and primitive stabilization
**Status:** completed

Delivered:
- repository recovery
- parser / normalization scaffold
- frozen early input subset
- primitive formulas and tests for:
  - `volume`
  - `duct`
  - `waveguide_1d`
  - `radiator`

### Phase 1 — first coupled one-frequency solver
**Status:** completed

Delivered:
- deterministic topology assembly
- first acoustic nodal matrix assembly
- driver electrical + mechanical coupling
- one-frequency complex solve
- first solved internal state for current, pressures, and cone motion

### Phase 2 — sweep and first observables
**Status:** completed

Delivered:
- frequency sweep helper
- solved sweep result container
- first classical outputs:
  - input impedance
  - cone velocity
  - cone displacement
  - one-radiator far-field pressure
  - one-radiator SPL

### Phase 3 — validation of the current solver path
**Status:** completed

Delivered:
- documentation alignment with the then-current assembled subset
- internal validation sanity tests for the current solver path

### Phase 4 — diagnostic fault isolation before topology expansion
**Status:** completed

Delivered:
- driver sign/coupling correction checkpoint
- numerical reference refresh
- validation updates on the corrected baseline

### Phase 5 — extended acoustic topology support and later corrective integration
**Status:** completed as historical technical phase

Delivered across the later Phase 5 and corrective lineage:
- assembled `waveguide_1d`
- first waveguide observability subset
- cylindrical distributed-loss support within the frozen boundary
- corrected `ts_classic` `Bl` normalization
- closed-box baffled-radiator Struve-path correction
- bass-reflex observation `radiation_space` correction
- provisional `os_lem.api` facade
- first release-governance structure
- `v0.1.0` foundation release

---

## Current release-driven roadmap

The project is now better described by milestones than by opening a new large technical phase.

### `v0.2.0` — offset-line observation-contract stabilization
**Status:** planned

Goal:
- turn the long observation/debug cycle into one bounded, documented release step

Current best-supported interpretation:
- `front/raw` is broadly credible
- remaining mismatch is localized to `mouth/port` observable semantics

Planned first move:
- one bounded observation-layer patch implementing/testing `mouth_directivity_only`
- keep `front` unchanged

### `v0.3.0` — observability and API maturity
**Status:** provisional planning only

Possible direction:
- cleaner exposure of existing observability features
- stronger maintained examples
- tighter provisional API posture

### `v0.4.0` — waveguide physics maturity
**Status:** provisional planning only

Possible direction:
- conical-loss maturity
- stronger loss-boundary documentation
- more disciplined line-workflow claims

### Later milestones
Choose one major capability family per release:
- passive radiator support
- richer electrical network support
- multi-driver support
- broader workflow productization
