# Milestone charter

## Current milestone

- milestone name: `v0.2.0`
- working title: `offset-line observation-contract stabilization`
- current status: planned / not yet opened as a clean milestone branch

---

## Why this milestone exists

The repository has already completed a long debug cycle on observation semantics.

That work changed the situation from:
- "we need a general line truth check"

to:
- `front/raw` is broadly credible
- the remaining mismatch is localized to `mouth/port` observable semantics
- the next useful move is a bounded observation-layer patch, not broad solver rework

So `v0.2.0` should package one coherent next step:
turn the debug conclusion into a narrow, documented milestone outcome.

---

## Release intent

`v0.2.0` should deliver:
- one bounded mouth-observable candidate patch
- regression protection that `front` remains unchanged
- narrow validation on the existing offset-line case
- aligned documentation that states the new contract honestly

This milestone is about observation-contract stabilization.
It is not a broad transmission-line release.

---

## In scope

Allowed items for `v0.2.0`:

- governance/docs reset needed to restart disciplined progress
- opening a clean milestone branch for `v0.2.0`
- bounded observation-layer development
- `mouth_directivity_only` candidate evaluation and, if validated, integration
- focused regression tests around `front` invariance and mouth semantics
- narrow comparison tooling or validation notes directly supporting the above
- release-note preparation for the resulting bounded claim

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

- a clean milestone branch exists
- the selected mouth-observable patch is small and well bounded
- `front` behavior is explicitly preserved
- the suite is green
- the docs distinguish clearly between released truth and current working-line conclusions
- the resulting claim is narrow enough to defend honestly

---

## Recommended branch sequence

Governance reset branch:
- `chore/v0.2.0-docs-reset`

Recommended milestone branch after the docs reset:
- `milestone/v0.2.0-offset-line-observation`

Recommended first technical patch branch:
- `fix/v0.2.0-mouth-directivity-only`

---

## Planned patch pack for the next session block

Suggested session size:
- roughly 10 to 12 patches

Suggested pack:
1. docs/governance reset
2. milestone branch creation
3. mouth directivity helper/invariant patch
4. `mouth_directivity_only` implementation
5. regression test: `front` unchanged
6. narrow validation harness update
7. docs update for observation contract
8. release-note draft
9. milestone sanity pass

---

## Exit condition

At the end of `v0.2.0`, the repo should be able to say:

- the released baseline remains `v0.1.0`
- the next milestone was advanced in one bounded, test-preserving way
- the observation-layer story is cleaner and better documented
- no unsupported broad parity claim was introduced
