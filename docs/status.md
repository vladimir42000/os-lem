# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- active working-line milestone: `v0.6.0`
- accepted control-plane branch for the current live state: `chore/post-v0.5.0-control-plane-alignment`
- accepted control-plane commit for the current live state: `2a96338`
- validated `v0.5.0` close-basis branch: `test/v0.5.0-stability-envelope-and-minimal-release-surface`
- validated `v0.5.0` close-basis commit: `152c7d2`
- observed green suite on the validated close basis: `318 passed`
- operator probe worktree state at control-plane bookkeeping time: clean working tree expected; local probe artifacts may be untracked

The current accepted control-plane line is a post-close alignment state above the validated `v0.5.0` technical basis.
The active milestone is now `v0.6.0`, opened as a bounded exposure/coherence milestone.

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
- opening scope is carried by the current control-plane documents
- milestone branch of record: not yet frozen as a dedicated milestone branch; current control-plane truth remains on `chore/post-v0.5.0-control-plane-alignment`

### Intent carried by `v0.6.0`

Use `v0.6.0` to turn the validated `v0.5.0` kernel surface into a truthful exposure/coherence milestone.
This is not a new capability-expansion milestone.

The bounded intent is:
- preserve Closed Box as the stable truthful anchor
- define the next truthful exposure boundary above the current stable anchor
- target one additional truthful end-to-end non-trivial workflow only if it can be exposed honestly on the landed kernel surface
- avoid assuming in advance whether that truthful exposure boundary becomes `extended frontend contract v1` or `frontend contract v2`

### Explicitly out of scope for `v0.6.0` opening state

- new topology-family growth before a bounded exposure/coherence decision is frozen
- solver redesign or new solver feature campaigns
- frontend/API contract redesign by assumption
- repo-wide cleanup or housekeeping detours
- public release promotion unsupported by repo truth

---

## Frontend contract state

- stable truthful anchor remains: `Closed Box`
- carried statement on the current accepted line: `No frontend contract change`
- contract naming beyond the stable truthful anchor is intentionally not precommitted at this opening stage

---

## Current control-plane truth

- `v0.5.0` is closed on the working line
- `v0.6.0` is now the active working-line milestone
- the single next live action is intentionally tracked only in `docs/next_patch.md`
