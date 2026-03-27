# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- accepted working branch for this decision: `milestone/v0.4.0-capability-expansion`
- accepted working commit for this decision: `7e22c0e`
- observed green suite on the accepted working line: `140 passed`
- operator probe worktree state at decision time: clean

Recent head chain confirms that the post-reset milestone branch now sits above the earlier pre-reset close-decision checkpoint and is the authoritative working line for this decision.

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

This is a working-line milestone close decision, not a public release promotion.

---

## Current control-plane truth

- the milestone branch alignment problem that triggered the reset is no longer present on the probed line
- `v0.4.0` is no longer the active milestone
- no successor milestone is opened by this patch

The single next live action is intentionally tracked only in `docs/next_patch.md` so sequencing state is not duplicated.
