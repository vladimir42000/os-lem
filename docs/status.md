# os-lem status

## Current development status

- latest released version: `v0.1.0`
- released branch of record: `main`
- current known green suite on the released baseline: `104 passed`

The `v0.1.0` foundation release is now complete and tagged.

That release established:
- a real released `main`
- pre-1.0 semantic versioning
- milestone-based integration before release
- conservative capability/release vocabulary

---

## Current released foundation (`v0.1.0`)

The released foundation includes:

- one-driver coupled electro-mechano-acoustic solve
- frequency sweep
- assembled `volume`, `duct`, `radiator`, and minimal `waveguide_1d`
- classical outputs:
  - input impedance
  - cone velocity
  - cone displacement
  - one-radiator far-field pressure
  - one-radiator SPL
- waveguide outputs:
  - endpoint flow
  - endpoint particle velocity
  - minimal `line_profile` for `pressure`
  - minimal `line_profile` for `volume_velocity`
  - minimal `line_profile` for `particle_velocity`
- cylindrical distributed loss for `waveguide_1d` within the currently frozen cylindrical-loss boundary
- provisional `os_lem.api` integration facade
- maintained example path in `examples/streamlit_frontend/app.py`
- preserved prototype/example path in `examples/streamlit_frontend/app2.py`

---

## Current interpretation

`v0.1.0` is a narrow but real foundation release.

It is intentionally conservative and does **not** imply:
- broad Hornresp parity
- broad AkAbak parity
- mature transmission-line support
- broad horn / line workflow coverage
- stable long-term public API
- product-grade GUI/frontend

---

## Next release target

The next planned release target is:

- `v0.2.0`

The purpose of `v0.2.0` is **not** to become a broad feature bucket.

It should deliver exactly one coherent next capability step beyond the `v0.1.0` foundation.

---

## Immediate next objective

The immediate next objective is to prepare the `v0.2.0` cycle with a bounded truth-finding step:

- create a `v0.2.0` milestone branch
- investigate current repository truth for a minimal transmission-line / offset-line case
- determine whether current support is:
  - already present
  - partial
  - or absent

Only after that should the first real `v0.2.0` implementation claim be chosen.

---

## Explicitly out of scope right now

- broad refactor
- broad post-release cleanup
- broad transmission-line marketing claims
- multi-driver expansion
- passive radiator support
- GUI productization
