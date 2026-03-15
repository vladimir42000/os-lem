# os-lem release plan

## Planning principle

Releases are defined by capability maturity, not by raw patch count.

A release should answer:

- what the software can do
- how confident we are
- what is explicitly not yet claimed

Current integration target:
- `milestone/v0.1.0-foundation`

---

## v0.1.0 — foundation release

### Release intent

`v0.1.0` should be the first honest, externally visible release of `os-lem`.

It should present a narrow but real kernel with clear limits.

### Planned included scope

The intended `v0.1.0` scope is:

- corrected sealed-box baseline
- corrected vented / bass-reflex baseline
- narrow validated output path for:
  - input impedance
  - cone velocity
  - cone displacement
  - one-radiator far-field pressure
  - one-radiator SPL
- minimal assembled `waveguide_1d`
- currently validated minimal waveguide observability subset:
  - endpoint flow export
  - endpoint particle-velocity export
  - minimal `line_profile` export for `pressure`
  - minimal `line_profile` export for `volume_velocity`
  - minimal `line_profile` export for `particle_velocity`
- current minimal cylindrical distributed-loss support for `waveguide_1d` within the frozen cylindrical-loss boundary
- corrected `ts_classic` canonical motor normalization
- provisional `os_lem.api` frontend facade
- at least one maintained example path
- green regression suite
- docs aligned to actual delivered behavior

### Explicit non-claims for v0.1.0

`v0.1.0` does **not** claim:

- broad Hornresp parity
- broad AkAbak parity
- mature transmission-line support
- broad horn / line workflow coverage
- conical lossy `waveguide_1d`
- thermo-viscous auto-derived losses
- stable long-term public API
- product-grade GUI
- multi-driver support
- passive radiator support
- crossover-network maturity

### Likely remaining work before release

The exact sequence may change, but likely remaining items are:

1. docs/status alignment
2. preserved validation/example asset integration
3. final milestone review
4. release tagging / release-note preparation

---

## v0.1.x — stabilization releases

### Intent

Post-`v0.1.0` patch releases may contain:

- bug fixes
- example hardening
- documentation correction
- narrow non-architectural cleanup
- regression-test strengthening

They should not redefine project scope.

---

## v0.2.0 — next bounded capability milestone

### Intent

`v0.2.0` should introduce exactly one coherent next-level capability step beyond the `v0.1.0` foundation.

Likely candidate directions include one of:

- first additional waveguide-specific exported observable beyond the current minimal subset
- first bounded line / offset-line truth-finding result strong enough to support a narrow claim
- another tightly scoped topology/observability extension

### Rule

`v0.2.0` must still preserve the small-patch philosophy.
It must not become a broad “everything after v0.1” bucket.

---

## v0.3.0 and later

Further releases should continue capability-based growth, such as:

- stronger line / waveguide maturity
- broader validation
- cleaner examples
- more coherent user-facing workflows
- tighter API posture when warranted

These items must only be scheduled when validated maturity supports them.

---

## v1.0.0 — first intentionally supported release

`v1.0.0` should not be defined by time or patch count.

It should be defined by release quality:

- coherent supported core use-cases
- honest and stable capability boundaries
- strong enough regression confidence
- reproducible examples
- stable enough public-facing API surface for the claimed scope
- clear documentation of both supported and unsupported areas

Until then, all releases remain intentionally pre-1.0.

---

## Current planning caution

The repository already contains more capability than the old public release posture suggested.

That is acceptable.

The job of release planning is not to claim everything that exists.
The job is to release what is coherent, validated, and supportable.
