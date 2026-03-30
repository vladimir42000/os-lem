# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- current accepted working-line branch: `feat/v0.5.0-seed-blind-throat-side-segment`
- current accepted working commit: `aa1a238c618f1f64fa4cc9f243b04f81d3ccf4db`
- observed green suite on the accepted working line: `193 passed`
- latest explicit frontend checkpoint: `81727af854207ccc94eeeede26988c688571cb30`
- operator probe worktree state at bookkeeping time: only untracked probe artifacts (`info.md`, `info.sh`)

This accepted working line is materially ahead of the old `9766931` opening-decision checkpoint. The live control-plane docs are realigned here to the current tested topology chain through the blind throat-side segment.

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
- active milestone title: `tapped-horn topology seeding`
- active milestone status: open on the working line
- current accepted topology checkpoint: `aa1a238c618f1f64fa4cc9f243b04f81d3ccf4db`
- latest explicit frontend checkpoint within this milestone: `81727af854207ccc94eeeede26988c688571cb30`
- frontend impact through the current accepted topology chain: `No frontend contract change`

Landed topology chain carried by the current accepted working line:
- parallel split/recombine bundles between the same two acoustic nodes
- one true interior acoustic junction
- one minimal branched horn skeleton
- one bounded recombination case
- one dual-junction split/merge horn skeleton
- one bounded tapped-driver skeleton
- one bounded offset-tap topology
- one bounded rear-chamber tapped skeleton
- one bounded rear-chamber port-injection topology
- one bounded throat-chamber topology
- one bounded blind throat-side horn segment

This remains a working-line milestone, not a public release promotion.

---

## Current control-plane truth

- `v0.5.0` remains the active working-line milestone
- the current accepted working commit is `aa1a238c618f1f64fa4cc9f243b04f81d3ccf4db`
- `81727af854207ccc94eeeede26988c688571cb30` remains the latest explicit frontend checkpoint
- the landed topology chain through `aa1a238` caused `No frontend contract change`
- the stale next action from the old opening-decision line is retired

The single next live action is intentionally tracked only in `docs/next_patch.md` so sequencing state is not duplicated.
