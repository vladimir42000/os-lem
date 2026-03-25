# Milestone charter

## Current release state

Latest completed release:
- `v0.2.0`

Release title:
- `offset-line observation-contract stabilization`

Status:
- released on `main`

---

## Current completed milestone

Name:
- `v0.3.0`

Title:
- `waveguide observability and API maturity`

Milestone branch:
- `milestone/v0.3.0-waveguide-observability-and-api-maturity`

Status:
- complete on milestone branch
- observed green suite on the close-decision line: `128 passed`

### Delivered scope

- promoted already-implemented element observables into the supported API/output surface
- kept the promoted contract bounded to `duct`, `radiator`, and `waveguide_1d` endpoint targets
- kept parser-side validation aligned to the promoted supported contract
- added end-to-end facade negative-path regression coverage for invalid promoted element-observable requests
- kept milestone scope conservative without reopening broad solver or API redesign work

### Out of scope for the completed milestone

- new waveguide physics models
- conical lossy waveguide maturity work
- passive radiator roadmap growth
- multi-driver support
- frontend productization
- broad API redesign beyond the bounded observable surface

### Exit condition

`v0.3.0` is considered complete because the promoted observability surface is now documented, tested, and usable without relying on debug-only workflows.

---

## Current continuation posture

There is no further `v0.3.0` milestone-scope patch planned by default.

If work continues from here, it should follow one of two explicit tracks:

1. bounded `v0.3.0` release-promotion planning and execution
2. later next-milestone seeding after release/governance decisions are made

Default recommendation:
- do not reopen closed `v0.3.0` milestone scope by default
- do not broaden claims beyond the tested milestone branch
- treat any next patch as release-promotion planning unless a different track is explicitly chosen
