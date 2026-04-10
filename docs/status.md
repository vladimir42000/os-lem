# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- active working-line milestone: `v0.6.0`
- accepted benchmark-led working-line branch for the current live state: `proof/poc2-conical-no-fill-benchmark-realignment`
- accepted benchmark-led working-line commit for the current live state: `d1a1d8a`
- validated `v0.5.0` close-basis branch: `test/v0.5.0-stability-envelope-and-minimal-release-surface`
- validated `v0.5.0` close-basis commit: `152c7d2`
- observed green suite on the accepted benchmark-led line: `318 passed`
- operator probe worktree state at bookkeeping time: local proof artifacts may remain untracked

The active working line is now a benchmark-led `v0.6.0` state above the validated `v0.5.0` kernel surface.
This line carries the landed `POC2` benchmark realignment plus the benchmark analysis note.

---

## Milestone state

### Most recent completed working-line milestone

- name: `v0.5.0`
- title: `bounded reusable topology growth and observability consolidation`
- status: closed on the working line
- validated close basis: `152c7d2`
- close-readiness alignment checkpoint: `ca9e346`
- post-close control-plane alignment checkpoint: `2a96338`
- public release claim: not made by this control-plane state

### Active working-line milestone

- name: `v0.6.0`
- title: `truthful exposure and coherence`
- status: opened on the working line
- opening/scope checkpoint: `667f3a5`
- current benchmark-led proof checkpoint: `d1a1d8a`
- milestone branch of record is not separately frozen beyond the current accepted working-line truth

### Intent carried by `v0.6.0`

Use `v0.6.0` to turn the validated `v0.5.0` kernel surface into a truthful exposure/coherence milestone.
At the current checkpoint, `v0.6.0` is operating in benchmark-led development mode.

The bounded intent is:
- preserve `Closed Box` as the stable truthful anchor
- preserve `POC2` as the current proof-of-reality reference benchmark
- freeze a reusable benchmark protocol before further real-world comparison work drifts
- avoid blind topology or solver growth while benchmark interpretation remains the main task

### Explicitly out of scope at this benchmark-led checkpoint

- new topology-family growth by default
- solver redesign or new solver feature campaigns
- frontend/API contract redesign
- repo-wide cleanup or housekeeping detours
- public release promotion unsupported by repo truth

---

## Benchmark-led development state

### Current reference benchmark

- reference-truth benchmark: `proof/poc2_conical_no_fill_benchmark/`
- benchmark protocol document: `proof/BENCHMARK_PROTOCOL.md`

### Why `POC2` is the current anchor

`POC2` is the current proof-of-reality anchor because it removed the earlier avoidable ambiguity around flare-law / semantic equivalence and produced a materially cleaner benchmark surface.

### Current protocol state

The benchmark protocol is now frozen for future benchmark-led work.
All future benchmark conclusions must distinguish among:
- model-equivalence issues
- missing-physics issues
- solver/pathology issues

---

## Frontend contract state

- stable truthful anchor remains: `Closed Box`
- carried statement on the current accepted line: `No frontend contract change`
- benchmark-led work at this checkpoint does not expand frontend/API contract scope

---

## Current control-plane truth

- `v0.5.0` remains closed on the working line
- `v0.6.0` remains the active working-line milestone
- the current live state is benchmark-led and protocol-frozen
- the single next live action is intentionally tracked only in `docs/next_patch.md`
