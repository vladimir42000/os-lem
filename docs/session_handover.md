# Session handover

## Accepted checkpoint for this handover

Accepted starting checkpoint for the successor-milestone decision patch:
- branch: `chore/post-v0.4.0-milestone-branch-alignment`
- commit: `b6dfc75`
- accepted post-reset close-decision commit carried by the aligned milestone line: `068d9f1`
- retained technical decision base: `7e22c0e`
- observed tests on the retained decision base: `140 passed`
- operator probe worktree state: clean

---

## Decision recorded here

This handover records one authoritative control-plane decision:
- `v0.4.0` remains closed on the working line
- the single successor milestone is `v0.5.0`
- `v0.5.0` is named only; no successor milestone branch or routine DEV patch is opened in this patch

This decision adds no solver work and no new technical scope.
It is also not a public release promotion; `v0.3.0` remains the latest released version on `main`.

---

## Close basis retained after successor decision

The retained technical close basis is still the post-reset revalidation on `7e22c0e`, namely:
- lossy conical `waveguide_1d` support within the current documented boundary
- preserved endpoint and line-profile observability on that path
- focused conical validation on the working line
- maintained conical example coverage on the live repo line
- segmentation-refinement validation for the official conical reference case

---

## Live sequencing note

The single next live action is kept only in `docs/next_patch.md` to avoid reintroducing duplicated sequencing state.
This patch does not guess the first routine `v0.5.0` development patch.
