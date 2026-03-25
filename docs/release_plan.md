# Release plan

## Latest completed release

- `v0.3.0`
- title: `waveguide observability and API maturity`
- release branch of record: `main`

Observed release-line validation at close:
- `128 passed`

---

## What is complete

`v0.3.0` is released.
The release package includes:
- promoted element-observable exposure through the supported API/output surface
- bounded parser/API contract hardening for that promoted observable surface
- end-to-end facade regression coverage for invalid promoted element-observable requests
- aligned governance/docs/release posture around the released `v0.3.0` truth

---

## Current active milestone

- `v0.4.0`
- title: `capability expansion`
- milestone branch: `milestone/v0.4.0-capability-expansion`

Current milestone focus:
- waveguide physics maturity for practical TL / horn workflows

Opening planned patch pack:
- `chore/v0.4.0-seed-waveguide-maturity`
- `feat/v0.4.0-conical-lossy-waveguide-mvp`
- `test/v0.4.0-conical-lossy-waveguide-validation`
- `chore/v0.4.0-waveguide-example-refresh`

Planning principle from here:
- treat `v0.4.0` as a coherent capability campaign rather than many unrelated micro-features
- keep the first code move focused on lossy conical `waveguide_1d` maturity
- do not mix passive radiator, multi-driver, or electrical-network expansion into the opening waveguide campaign
