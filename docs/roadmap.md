# os-lem roadmap

## Project intent

`os-lem` is an open, scriptable lumped-element loudspeaker / enclosure simulator
with a development style inspired by Akabak-era workflows, but implemented as a clean,
testable Python codebase with disciplined incremental growth.

The roadmap is both phase-based and release-based:

- phases explain technical evolution
- releases explain what is honest to expose externally

Current release track:
- `v0.1.0` foundation milestone on `milestone/v0.1.0-foundation`

---

## Phase 0 — recovery and primitive stabilization
**Status:** completed

### Goal
Recover a clean, testable baseline and freeze the first validated primitive set.

### Delivered
- repository recovery
- parser / normalization scaffold
- frozen early input subset
- primitive formulas and tests for:
  - `volume`
  - `duct`
  - `waveguide_1d`
  - `radiator`

---

## Phase 1 — first coupled one-frequency solver
**Status:** completed

### Goal
Build the first minimal coupled electro-mechano-acoustic solve for one driver at one frequency.

### Delivered
- deterministic topology assembly
- first acoustic nodal matrix assembly
- driver electrical + mechanical coupling
- one-frequency complex solve
- first solved internal state for current, pressures, and cone motion

---

## Phase 2 — sweep and first observables
**Status:** completed

### Goal
Extend the one-frequency solve into a sweep and expose the first user-relevant outputs.

### Delivered
- frequency sweep helper
- solved sweep result container
- first classical outputs:
  - input impedance
  - cone velocity
  - cone displacement
  - one-radiator far-field pressure
  - one-radiator SPL

---

## Phase 3 — validation of the current solver path
**Status:** closed

### Goal
Strengthen trust in the narrow current solver path before topology expansion.

### Delivered
- documentation alignment with the then-current assembled subset
- internal validation sanity tests for the current solver path

### Caution
Phase 3 did not freeze a broad external parity claim.

---

## Phase 4 — diagnostic fault isolation before topology expansion
**Status:** closed

### Goal
Localize major box-model discrepancies before resuming topology growth.

### Delivered
- diagnosis isolated a real solver sign-convention bug
- driver front / rear acoustic coupling signs were corrected
- frozen numerical reference outputs were refreshed
- affected validation tests were updated to remain meaningful on the corrected baseline

### Result
Phase 4 closed at a corrective checkpoint rather than a broad external-validation claim.

---

## Phase 5 — extended acoustic topology support
**Status:** current technical phase

### Goal
Resume topology growth after the corrected Phase 4 baseline.

### Delivered so far
- `waveguide_1d` now assembles as a topology-resolved branch element
- the acoustic matrix accepts reduced two-port `waveguide_1d` stamping
- focused assembly and solve tests cover the first minimal waveguide path
- stronger internal validation now covers:
  - constant-area segmentation invariance
  - conical segmentation refinement sanity
- first waveguide-specific observability is delivered:
  - endpoint flow export
  - endpoint particle-velocity export
  - minimal `line_profile` export for `pressure`
  - minimal `line_profile` export for `volume_velocity`
  - minimal `line_profile` export for `particle_velocity`
- stronger cross-profile internal validation now covers:
  - endpoint/profile agreement checks
  - cross-profile consistency checks
  - cylindrical special-case consistency
- first minimal cylindrical distributed-loss support is implemented for `waveguide_1d`
- corrected `ts_classic` canonical `Bl` normalization is integrated into the current baseline

### Still not delivered as a broad claim
- conical lossy `waveguide_1d`
- thermo-viscous auto-derived losses
- broad horn / line workflow claims
- broad external parity claims

---

## Post-Phase-5 corrective and integration checkpoints
**Status:** completed on the current development line

After the main Phase 5 waveguide growth, the current development line also absorbed several bounded corrective/integration checkpoints:

- closed-box baffled-radiator Struve-path fix
- bass-reflex SPL observation `radiation_space` fix
- provisional `os_lem.api` frontend facade
- release-governance and milestone planning docs

These are part of the current `v0.1.0` release track.

---

## v0.1.0 — foundation release
**Status:** active milestone target

### Intent
Publish the first honest external release of `os-lem` without overstating scope.

### Intended release character
- narrow but real
- validated enough to be usable
- explicit about what is and is not claimed

### Included direction
- corrected sealed and vented baseline behavior
- current one-driver classical output path
- current minimal waveguide subset
- current provisional frontend integration facade
- aligned release/status documentation
- at least one maintained example path

### Explicit non-claims
- broad Hornresp parity
- broad AkAbak parity
- mature transmission-line support
- stable long-term public API
- product-grade GUI/frontend

---

## Phase 6 — user-facing maturation
**Status:** planned after the current foundation release

### Goal
Improve usability, examples, and result inspection after the foundation release is coherent.

### Possible items
- richer maintained examples
- plotting/reporting helpers
- improved result inspection
- broader but still disciplined API posture
