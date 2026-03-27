# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- accepted working branch at reset entry: `chore/v0.4.0-close-decision`
- accepted working commit at reset entry: `5cb5548`
- observed green suite on the accepted working line: `140 passed`

The working line already includes the landed `v0.4.0` waveguide campaign and the bounded close-decision docs that followed it.

---

## Active milestone

- milestone: `v0.4.0`
- title: `capability expansion`
- milestone branch of record: `milestone/v0.4.0-capability-expansion`

Important control-plane fact:
- before this reset, the milestone branch pointer lagged the accepted working line
- after this reset patch is accepted, the milestone branch must be fast-forwarded to the accepted reset commit

---

## Current working-line technical truth beyond `v0.3.0`

The current `v0.4.0` working line includes:
- bounded lossy conical `waveguide_1d` support
- preserved endpoint and line-profile observability on that path
- focused conical-loss validation
- one maintained conical-line hero example
- segmentation-refinement validation for the official conical example

This is working-line milestone truth, not a public release claim.

---

## Current control-plane truth

This reset exists because the previous documentation layer carried duplicated live sequencing state.
The immediate goal is to restore a smaller and stricter control model.

Until a fresh post-reset AUDIT is written:
- no DEV patch is frozen
- no routine coding session should guess the next step

---

## Immediate next action

Required next action after this reset lands:
- `AUDIT: post-reset readiness check for v0.4.0`

That audit must decide whether the repo is:
- `READY` for one exact next bounded DEV patch, or
- `NOT READY`, requiring one exact reset/decision patch first
