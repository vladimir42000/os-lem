# Milestone charter

## Current milestone

- milestone name: `v0.2.0`
- working title: `offset-line observation-contract stabilization`
- current status: active / in progress
- active integration branch: `milestone/v0.2.0-offset-line-observation`

---

## Why this milestone exists

The repository completed a long debug cycle on observation semantics.

That work changed the situation from:
- "we need a general line truth check"

to:
- `front/raw` is broadly credible
- the remaining mismatch is localized to `mouth/port` observable semantics
- the next useful move is a bounded observation-layer patch, not broad solver rework

So `v0.2.0` packages one coherent next step:
turn the debug conclusion into a narrow, documented milestone outcome.

---

## Release intent

`v0.2.0` is intended to deliver:
- one bounded mouth-observable candidate contract
- regression protection that `front` remains unchanged
- one maintained offset-line compare harness around the bounded candidates
- aligned documentation and release wording that state the result honestly

This milestone is about observation-contract stabilization.
It is not a broad transmission-line release.

---

## Landed milestone work so far

The milestone branch now contains:

1. docs/governance reset and debug-archive restructuring
2. clean milestone-branch promotion away from the long debug line
3. opt-in `mouth_directivity_only` support for passive `spl` and term-level `spl_sum`
4. explicit rejection of driver-front use of that bounded contract
5. connected-aperture area consistency guard for the mouth candidate
6. maintained offset-line compare harness with regression coverage

Observed green suite on the current milestone snapshot:
- `118 passed`

---

## In scope

Allowed items for `v0.2.0`:

- governance/docs reset needed to restart disciplined progress
- bounded observation-layer development
- `mouth_directivity_only` candidate implementation and guardrails
- focused regression tests around `front` invariance and mouth semantics
- narrow comparison tooling or validation notes directly supporting the above
- release-note preparation and final claim-tightening for the resulting bounded release

---

## Out of scope

Not allowed in `v0.2.0`:

- broad transmission-line marketing claims
- broad Hornresp parity claims
- broad AkAbak parity claims
- multi-driver support
- passive radiator support
- conical lossy `waveguide_1d`
- major frontend expansion
- public API freeze beyond the current provisional facade
- unrelated cleanup or refactor

---

## Acceptance criteria

The milestone is complete only if:

- the active milestone branch remains green
- the selected mouth-observable work stays small and well bounded
- `front` behavior is explicitly preserved
- the compare harness and regression coverage remain maintained
- docs distinguish clearly between released truth and current working-line conclusions
- the resulting release notes make no unsupported parity claim

---

## Remaining close work

Still needed before merging to `main`:

1. `v0.2.0` release-note draft
2. final scope-and-claim alignment pass
3. explicit merge/tag decision once the wording is stable

Recommended next patch after this draft lands:
- `chore/v0.2.0-release-candidate-close`

---

## Exit condition

At the end of `v0.2.0`, the repo should be able to say:

- the released baseline remains `v0.1.0`
- the next milestone advanced in a bounded, test-preserving way
- the observation-layer story is cleaner, better guarded, and better documented
- no unsupported broad parity claim was introduced
