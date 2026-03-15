# os-lem v0.1.0 release notes

## Release character

`v0.1.0` is the first honest external foundation release of `os-lem`.

It marks the transition from internal scaffolding/project recovery to a narrow but real, tested loudspeaker/enclosure kernel with an explicit release structure.

---

## Included in v0.1.0

### Kernel foundation
- one-driver coupled electro-mechano-acoustic solve
- frequency sweep
- assembled:
  - `volume`
  - `duct`
  - `radiator`
  - minimal `waveguide_1d`

### Classical outputs
- input impedance
- cone velocity
- cone displacement
- one-radiator far-field pressure
- one-radiator SPL

### Minimal waveguide observability
- endpoint flow export
- endpoint particle-velocity export
- minimal `line_profile` export for `pressure`
- minimal `line_profile` export for `volume_velocity`
- minimal `line_profile` export for `particle_velocity`

### Minimal lossy waveguide subset
- cylindrical distributed loss for `waveguide_1d` within the frozen cylindrical-loss boundary

### Corrective checkpoints integrated into the release line
- corrected `ts_classic` canonical `Bl` normalization
- corrected closed-box baffled-radiator low-frequency reactance behavior through the Struve-path fix
- corrected bass-reflex SPL observation behavior through explicit observation `radiation_space` decoupling

### Integration/example surface
- provisional `os_lem.api` facade
- maintained Streamlit example path in `examples/streamlit_frontend/app.py`
- preserved prototype/example artifact in `examples/streamlit_frontend/app2.py`

---

## Explicit non-claims

`v0.1.0` does **not** claim:

- broad Hornresp parity
- broad AkAbak parity
- mature transmission-line support
- broad horn / line workflow coverage
- conical lossy `waveguide_1d`
- thermo-viscous auto-derived losses
- stable long-term public API
- product-grade GUI/frontend
- passive radiator support
- multi-driver support
- crossover-network maturity

---

## Process significance

`v0.1.0` also establishes the new project release structure:

- `main` for released/stable history
- milestone branch integration before release
- pre-1.0 semantic versioning
- conservative capability/status vocabulary

This release is intentionally narrower than the long-term project vision.
That is a deliberate discipline choice, not a limitation of ambition.
