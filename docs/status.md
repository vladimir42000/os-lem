# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- active working-line milestone branch of record: `milestone/v0.5.0-opening`
- accepted successor-milestone decision checkpoint carried into this opening: `c548267`
- retained technical decision base from the most recent closed milestone: `7e22c0e`
- observed green suite on the retained decision base: `140 passed`
- operator probe worktree state before this opening patch: clean

This control-plane opening patch makes `v0.5.0` the active milestone on the working line and defines one milestone branch of record without freezing routine development scope.

---

## Milestone state

- most recently completed working-line milestone: `v0.4.0`
- completed milestone title: `capability expansion`
- completed milestone branch of record: `milestone/v0.4.0-capability-expansion`
- completed milestone status: closed on the working line after post-reset revalidation

Retained close basis from the completed `v0.4.0` line:
- bounded lossy conical `waveguide_1d` support
- preserved endpoint and line-profile observability on that path
- focused conical-loss validation
- one maintained conical-line example on the live repo line
- segmentation-refinement validation for the official conical example

- active working-line milestone: `v0.5.0`
- active milestone title: `opening decision`
- active milestone branch of record: `milestone/v0.5.0-opening`
- active milestone status: open on the working line
- first routine `v0.5.0` DEV patch: not frozen
- technical scope added by this patch: none

This remains a working-line milestone-control change, not a public release promotion.

---

## Current control-plane truth

- `v0.4.0` remains closed on the working line
- `v0.5.0` is now the active working-line milestone
- the single `v0.5.0` milestone branch of record is `milestone/v0.5.0-opening`
- no routine `v0.5.0` DEV patch is frozen yet

The single next live action is intentionally tracked only in `docs/next_patch.md` so sequencing state is not duplicated.
