# Session handover

## Accepted checkpoint for this handover

Accepted starting checkpoint for the `v0.5.0` opening patch:
- branch: `chore/post-v0.4.0-next-milestone-decision`
- commit: `c548267`
- retained technical decision base from the last closed milestone: `7e22c0e`
- observed tests on the retained decision base: `140 passed`
- operator probe worktree state: clean

---

## Decision recorded here

This handover records one authoritative control-plane decision:
- `v0.5.0` is now open as the active working-line milestone
- the single `v0.5.0` milestone branch of record is `milestone/v0.5.0-opening`
- no routine `v0.5.0` DEV patch is frozen in this patch

This decision adds no solver work and no new technical scope.
It is also not a public release promotion; `v0.3.0` remains the latest released version on `main`.

---

## Closed-basis context retained after opening

The retained technical close basis from `v0.4.0` is still the post-reset revalidation on `7e22c0e`, namely:
- lossy conical `waveguide_1d` support within the current documented boundary
- preserved endpoint and line-profile observability on that path
- focused conical validation on the working line
- maintained conical example coverage on the live repo line
- segmentation-refinement validation for the official conical reference case

---

## Live sequencing note

The single next live action is kept only in `docs/next_patch.md` to avoid reintroducing duplicated sequencing state.
This patch does not guess the first routine `v0.5.0` development patch.
