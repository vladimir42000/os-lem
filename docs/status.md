# os-lem status

## Current development status

- active release target: `v0.1.0`
- integration branch: `milestone/v0.1.0-foundation`
- current known green suite on the development line: `104 passed`

Current branch activity may happen on short-lived child branches, but milestone integration truth now lives on the `milestone/v0.1.0-foundation` branch until the first release is ready.

---

## Current validated foundation

The current validated foundation includes:

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

---

## Recent corrective checkpoints now integrated

The current development line already includes these corrective checkpoints:

- corrected `ts_classic` canonical `Bl` normalization
- corrected closed-box baffled-radiator low-frequency reactance behavior through the Struve-path fix
- corrected bass-reflex SPL observation behavior by decoupling observation `radiation_space` from the radiator mechanical model

These checkpoints improve trust in the current narrow kernel baseline, but they do **not** justify broad external parity claims.

---

## Current project interpretation

`os-lem` is now beyond pure early scaffolding and has enough real validated behavior to justify a first honest release target.

That release target is intentionally narrow:

- a validated foundation release
- not a broad loudspeaker product
- not a broad Hornresp/AkAbak replacement claim
- not a frozen long-term API claim

---

## Immediate next objective

After the current docs-alignment patch is merged, the next bounded milestone patch should be:

- preserve maintained validation/example assets cleanly
- keep example posture explicit
- avoid mixing this with new kernel work

After that, the milestone should be reviewed for `v0.1.0` release readiness.

---

## Explicitly out of scope right now

- broad refactor
- multi-driver expansion
- passive radiator support
- broad horn / transmission-line claims
- broad GUI / product claims
- unsupported external parity marketing
