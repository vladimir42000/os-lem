# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- active working-line milestone: `v0.5.0`
- accepted working branch for the current live control state: `test/v0.5.0-stability-envelope-and-minimal-release-surface`
- accepted working commit for the current live control state: `152c7d2`
- observed green suite on the accepted working line: `318 passed`
- operator probe worktree state at bookkeeping time: no tracked modifications; local probe artifacts may be untracked

The current accepted line is the validated v0.5 convergence surface.
It is the line on which close-readiness is now judged.

Validated v0.5 surface carried by the accepted line:
- back-loaded-horn-class direct+rear support with bounded smoke and regression coverage
- explicit front/rear radiation-sum observability
- explicit rear-delay/path observability
- explicit front/rear contribution observability
- direct-plus-branched rear-path family with seed, smoke, contract, and regression coverage
- direct-plus-split-merge rear-path family with seed, smoke, contract, and regression coverage
- direct-plus-branched-split-merge rear-path family with seed, smoke, contract, and regression coverage
- direct-plus-branched-split-merge rear-path front-chamber throat-side coupling variant with seed, smoke, contract, and regression coverage
- bounded multi-family consistency and observability probe coverage
- bounded stability-envelope and minimal-release-surface probe coverage

---

## Milestone state

- active working-line milestone: `v0.5.0`
- milestone title: `direct+rear reusable graph convergence`
- milestone status: close-ready on the working line
- close-readiness result: `ready to close now`
- further bounded technical patch required before close: `no`

This is a truthful working-line close-readiness state, not a public release promotion by itself.

---

## Frontend contract state

- latest explicit frontend checkpoint: `81727af854207ccc94eeeede26988c688571cb30`
- carried statement on the current accepted line: `No frontend contract change`

The validated v0.5 surface does not change the frozen frontend contract v1 surface.

---

## Current control-plane truth

- the validated v0.5 line is `152c7d2` on `test/v0.5.0-stability-envelope-and-minimal-release-surface`
- the accepted line is sufficient to support an immediate v0.5 close decision
- no additional technical patch is required before close
- the single next live action is intentionally tracked only in `docs/next_patch.md`
