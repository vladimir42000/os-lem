# os-lem v0.2.0 release notes (draft)

## Draft status

This file is a draft.

`v0.2.0` is not released yet.
The purpose of this draft is to freeze the wording early so the eventual merge to `main` stays honest and bounded.

Working release title:
- `offset-line observation-contract stabilization`

---

## Release character

`v0.2.0` is intended to be a narrow follow-up to the `v0.1.0` foundation release.

It does **not** attempt to turn `os-lem` into a broad transmission-line or parity release.
Instead, it packages one disciplined next step from the long observation/debug cycle:

- preserve the already-credible `front/raw` path
- localize new work to `mouth/port` observable semantics
- expose the bounded candidate explicitly and test it
- keep the remaining residual visible instead of speculative

---

## Planned inclusions in v0.2.0

### Observation-contract stabilization
- opt-in `observable_contract: mouth_directivity_only`
- passive mouth/port usage only
- available for `spl` observations and term-level `spl_sum` terms
- explicit rejection of driver-front use for this bounded contract

### Candidate guardrails
- connected-aperture area consistency guard for the passive mouth candidate
- one frozen physical mouth area used for both mouth flow semantics and `D(ka_mouth)`
- regression coverage that preserves raw/default behavior

### Maintained comparison support
- one maintained offset-line compare harness
- reported channels:
  - `front_raw`
  - `mouth_raw`
  - `mouth_candidate`
  - `sum_raw`
  - `sum_candidate`
- comparison artifacts that keep the remaining mouth residual explicit

### Process significance
- milestone/governance reset that separates release integration from the historical debug line
- clearer distinction between released truth, milestone truth, debug archive, and companion book material

---

## Explicit non-claims

`v0.2.0` should **not** claim:

- broad Hornresp parity
- broad AkAbak parity
- general transmission-line maturity
- broad horn / line workflow coverage
- global radiator directivity correction
- default replacement of the existing raw observation path
- passive radiator support as a general project capability
- multi-driver support
- conical lossy `waveguide_1d`
- stable long-term public API
- product-grade frontend maturity

---

## Recommended release wording

Suggested short release summary:

> `v0.2.0` stabilizes one bounded next step in the offset-line observation story by adding an opt-in mouth/port observation candidate, guarding its mouth-area semantics, and preserving a maintained compare harness around the remaining residual.

Suggested one-sentence caveat:

> This is a narrow observation-contract release, not a broad transmission-line or parity claim.

---

## Pre-release checklist

Before merging `v0.2.0` to `main`, confirm:

- milestone branch is green
- release wording still matches the tested repository state
- no unsupported parity language slipped into docs
- compare harness remains maintained
- the remaining residual is described honestly as bounded, not silently erased

---

## Follow-on direction after v0.2.0

Only after `v0.2.0` closes cleanly should the project consider the next milestone family, such as:
- observability/API maturity
- waveguide physics maturity
- one new capability family per later milestone
