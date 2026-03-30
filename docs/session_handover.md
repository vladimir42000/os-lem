# Session handover

## Accepted checkpoint for this handover

Accepted working-line checkpoint for post-blind-throat-side bookkeeping:
- branch: `feat/v0.5.0-seed-blind-throat-side-segment`
- commit: `aa1a238c618f1f64fa4cc9f243b04f81d3ccf4db`
- observed tests: `193 passed`
- latest explicit frontend checkpoint: `81727af854207ccc94eeeede26988c688571cb30`
- frontend impact through this checkpoint: `No frontend contract change`
- operator probe worktree state: only untracked probe artifacts (`info.md`, `info.sh`)

---

## Decision recorded here

This handover records one authoritative bookkeeping decision:
- the live control-plane docs are realigned to the current accepted working line at `aa1a238c618f1f64fa4cc9f243b04f81d3ccf4db`
- the stale live-action entry inherited from the old `9766931` opening-decision line is retired
- `81727af854207ccc94eeeede26988c688571cb30` remains the latest explicit frontend checkpoint
- the landed topology chain through the blind throat-side segment caused `No frontend contract change`

This patch adds no solver work and no frontend/API work.
It is not a public release promotion; `v0.3.0` remains the latest released version on `main`.

---

## Current landed kernel chain carried by the accepted working line

The current accepted working line carries the bounded v0.5.0 topology sequence through:
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

---

## Live sequencing note

The single next live action is kept only in `docs/next_patch.md` to avoid reintroducing duplicated sequencing state.
After this bookkeeping patch, the exact next bounded kernel patch is:
- `test/v0.5.0-throat-side-akabak-reference-smoke`
