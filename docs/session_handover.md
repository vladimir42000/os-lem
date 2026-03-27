# Session handover

## Accepted checkpoint for this handover

Accepted working-line checkpoint for the post-reset close decision:
- branch: `milestone/v0.4.0-capability-expansion`
- commit: `7e22c0e`
- observed tests: `140 passed`
- operator probe worktree state: clean

---

## Decision recorded here

This handover records one authoritative post-reset milestone decision:
- `v0.4.0` is closed on the current working line

This close decision is grounded in the current tested repo state, not in the pre-reset close sequence by itself.
It is also not a public release promotion; `v0.3.0` remains the latest released version on `main`.

---

## Close basis used for the decision

The working line still carries the bounded `v0.4.0` capability set named in the milestone charter:
- lossy conical `waveguide_1d` support within the current documented boundary
- preserved endpoint and line-profile observability on that path
- focused conical validation on the working line
- maintained conical example coverage on the live repo line
- segmentation-refinement validation for the official conical reference case

The earlier milestone-branch lag that motivated the reset is no longer present on the probed line.

---

## Live sequencing note

No successor milestone is opened in this patch.
The single next live action is kept only in `docs/next_patch.md` to avoid reintroducing duplicated sequencing state.
