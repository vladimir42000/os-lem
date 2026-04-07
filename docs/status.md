# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- active working-line milestone: `v0.6.0`
- accepted control-plane checkpoint: `ca9e346` on `chore/v0.5.0-close-readiness-and-control-plane-alignment`
- retained validated technical close basis: `152c7d2` on `test/v0.5.0-stability-envelope-and-minimal-release-surface`
- observed green suite on the retained validated technical basis: `318 passed`
- operator probe worktree state at milestone-decision time: no tracked modifications; local probe artifacts may be untracked

The current accepted control state is post-`v0.5.0` milestone closure.
The retained validated technical basis for immediate successor control remains `152c7d2`.

Validated `v0.5.0` surface carried by the retained technical basis:
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

- most recently closed working-line milestone: `v0.5.0`
- closed working-line milestone title: `direct+rear reusable graph convergence`
- `v0.5.0` close-control checkpoint: `ca9e346`
- `v0.5.0` validated technical close basis: `152c7d2`
- `v0.5.0` close result: `closed on the working line`
- successor working-line milestone: `v0.6.0`
- successor milestone state: `opened by post-v0.5.0 control-plane decision`

This is a truthful working-line milestone-control state, not a public release promotion by itself.

---

## Frontend contract state

- latest explicit frontend checkpoint: `81727af854207ccc94eeeede26988c688571cb30`
- carried statement on the retained validated technical basis: `No frontend contract change`

The post-`v0.5.0` milestone decision does not change the frozen frontend contract v1 surface.

---

## Current control-plane truth

- `v0.5.0` is closed on the working line
- `v0.6.0` is now opened as the successor working-line milestone
- `v0.6.0` intent is bounded successor-line continuation above the validated `v0.5.0` surface, one exact bounded technical patch at a time
- no new topology family, solver redesign, API expansion, frontend redesign, or repo-wide cleanup is implicitly authorized by this decision alone
- the single next live action is intentionally tracked only in `docs/next_patch.md`
