# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- accepted closed-milestone branch of record: `milestone/v0.4.0-capability-expansion`
- current accepted control-plane checkpoint: `b6dfc75`
- accepted post-reset close-decision commit carried by that line: `068d9f1`
- retained technical decision base for that close decision: `7e22c0e`
- observed green suite on the retained decision base: `140 passed`
- operator probe worktree state before this successor-milestone decision patch: clean

The current accepted control-plane checkpoint keeps the closed `v0.4.0` line aligned while naming one successor milestone without opening technical work yet.

---

## Milestone state

- most recently completed working-line milestone: `v0.4.0`
- title: `capability expansion`
- milestone branch of record: `milestone/v0.4.0-capability-expansion`
- status: closed on the working line after post-reset revalidation

Close basis retained on the current working line:
- bounded lossy conical `waveguide_1d` support
- preserved endpoint and line-profile observability on that path
- focused conical-loss validation
- one maintained conical-line example on the live repo line
- segmentation-refinement validation for the official conical example

This remains a working-line milestone close decision, not a public release promotion.

---

## Successor milestone state

- named successor milestone: `v0.5.0`
- successor milestone title: `pending post-v0.4.0 readiness audit`
- successor milestone status: named only
- no successor milestone branch of record is opened by this patch
- no routine DEV patch is frozen by this patch

This patch makes one bounded control-plane decision only: the successor milestone is `v0.5.0`, but its first routine development patch remains intentionally unset until the next audit reads current repo truth.

---

## Current control-plane truth

- `v0.4.0` remains closed on the working line
- `v0.5.0` is the single named successor milestone
- no successor milestone branch is opened yet
- no routine DEV patch is frozen yet

The single next live action is intentionally tracked only in `docs/next_patch.md` so sequencing state is not duplicated.
