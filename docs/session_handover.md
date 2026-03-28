# Session handover

## Accepted checkpoint for this handover

Accepted starting checkpoint for the `v0.5.0` first routine-patch decision:
- branch: `chore/v0.5.0-opening-decision`
- commit: `9766931`
- retained technical decision base from the last closed milestone: `7e22c0e`
- observed tests on the retained decision base: `140 passed`
- operator probe worktree state: clean

---

## Decision recorded here

This handover records one authoritative control-plane decision:
- `v0.5.0` remains open as the active working-line milestone
- the single `v0.5.0` milestone branch of record remains `milestone/v0.5.0-opening`
- the single first routine `v0.5.0` patch is `chore/v0.5.0-seed-branching-topology`
- no solver work is added in this decision patch

This decision freezes only the minimal branching / recombination topology opening needed to start tapped-horn-class graph work.
It does not freeze passive radiator work, multi-driver active architecture, electrical-network element graph work, or broad frontend / API work.
It is also not a public release promotion; `v0.3.0` remains the latest released version on `main`.

---

## Closed-basis context retained after the decision

The retained technical close basis from `v0.4.0` is still the post-reset revalidation on `7e22c0e`, namely:
- lossy conical `waveguide_1d` support within the current documented boundary
- preserved endpoint and line-profile observability on that path
- focused conical validation on the working line
- maintained conical example coverage on the live repo line
- segmentation-refinement validation for the official conical reference case

---

## Live sequencing note

The single next live action is kept only in `docs/next_patch.md` to avoid reintroducing duplicated sequencing state.
This patch freezes exactly one first routine `v0.5.0` development patch and no alternatives.
