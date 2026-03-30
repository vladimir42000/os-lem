# Next action

## Live rule

This file is the single live-action document.
It must stay aligned with `docs/status.md` and `docs/session_handover.md` without duplicating milestone decision history.

---

## Current state after post-blind-throat-side bookkeeping

- active working-line milestone: `v0.5.0`
- active milestone title: `tapped-horn topology seeding`
- current accepted working line: `feat/v0.5.0-seed-blind-throat-side-segment`
- current accepted working commit: `aa1a238c618f1f64fa4cc9f243b04f81d3ccf4db`
- observed suite on the accepted working line: `193 passed`
- latest explicit frontend checkpoint: `81727af854207ccc94eeeede26988c688571cb30`
- frontend impact through the current accepted topology chain: `No frontend contract change`
- stale live action from the old opening-decision line is retired

---

## Next live action

- `DEV: test/v0.5.0-throat-side-akabak-reference-smoke`

---

## Guard rail

Do not reopen the old `9766931` opening-decision line and do not reintroduce stale control-plane state.
The next bounded patch is the single validation step named above and should compare the currently landed throat-chamber plus blind throat-side structure against the existing TH Akabak reference bundle.
