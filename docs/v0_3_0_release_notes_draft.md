# v0.3.0 release notes draft

> Editorial status note: `v0.3.0` is already the current public release baseline on `main`.
> This file remains a draft editorial artifact for the already-public baseline; earlier pre-release gating language is historical context only and is not current repo truth.

## Draft status

This file is a draft editorial note attached to the already-public `v0.3.0` baseline.
It no longer serves as a pre-promotion gate.

Working release title:
- `waveguide observability and API maturity`

---

## Public release character

`v0.3.0` is the currently released public baseline on `main`.

It is a bounded maturity release for:
- promoted element observables in the supported API/output surface
- parser/API contract hardening around that promoted surface
- regression-backed documentation and governance alignment

It does **not** present:
- a broad transmission-line parity claim
- a broad AkAbak or Hornresp parity claim
- a `v0.6.0` working-line promotion
- a `v0.7.0` opening

---

## Public-line suite truth

At the public-line green-suite truth audit, the reproducible public-line test state is:

- `127 passed, 1 failed`

Observed failing surface:
- `tests/debug/test_offset_line_compare_harness.py`

Observed bounded cause:
- missing file: `debug/hornresp_offset_line_drv.frd`

This note records that public-line truth directly.
It does not broaden the public capability story beyond the released `v0.3.0` baseline.

---

## Released scope summary

### Promoted supported observability surface
- `element_volume_velocity`
- `element_particle_velocity`
- supported targets:
  - `duct`
  - `radiator`
  - `waveguide_1d` endpoint exports via explicit `location: a|b`

### Contract hardening
- early parser rejection for incomplete or unsupported promoted element-observable requests
- explicit facade behavior around invalid promoted element-observable requests
- preserved default behavior outside the promoted bounded surface

### Regression and governance significance
- end-to-end facade regression coverage for valid promoted element observables
- end-to-end facade regression coverage for invalid promoted element-observable requests
- released public baseline on `main`
- public-line suite truth recorded as observed, including the bounded known failure above

---

## Explicit non-claims

`v0.3.0` should **not** be read as claiming:

- broad Hornresp parity
- broad AkAbak parity
- broad transmission-line maturity beyond the currently documented supported surface
- new waveguide physics models
- passive radiator support as a general project capability
- multi-driver support
- conical lossy `waveguide_1d` maturity beyond the current bounded state
- stable long-term public API beyond the promoted documented facade surface
- product-grade frontend maturity

---

## Suggested short public summary

> `v0.3.0` is the released public baseline on `main`, promoting bounded element observability into the supported API/output surface and hardening the contract around that surface.

> Public-line test truth currently reproduces as `127 passed, 1 failed`, with the single known failure limited to the offset-line debug harness because `debug/hornresp_offset_line_drv.frd` is missing.
