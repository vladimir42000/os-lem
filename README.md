# os-lem

Open, scriptable loudspeaker and enclosure simulator with a disciplined, test-first development style inspired by classic Akabak-era LEM workflows.

## Release posture

Latest released version:
- `v0.2.0` on `main`

Current green suite on the released line:
- `118 passed`

Current project posture:
- `v0.2.0` is released
- the offset-line observation-contract stabilization milestone is complete
- the next work item is **post-release housekeeping**, not immediate new solver development

## What `v0.2.0` adds

Released milestone additions beyond the earlier foundation line:

- opt-in `observable_contract: mouth_directivity_only`
- connected-aperture normalization guard for the bounded mouth/port candidate path
- maintained offset-line compare harness under `debug/`
- tightened milestone/release documentation for observation-layer work

These changes were intentionally bounded to the observation layer and release-story alignment.

## What is still not claimed

`os-lem` still does **not** claim:

- broad Hornresp parity
- broad AkAbak parity
- mature transmission-line product workflow support
- passive radiator support
- multi-driver support
- crossover-network maturity
- stable long-term public API
- product-grade GUI/frontend

## Companion documentation

The explanatory companion book now lives separately at:
- `https://github.com/vladimir42000/os-lem-book`

Repository docs remain the source of truth for release status, supported scope, and next patch planning.

## Documentation entry points

Start with:
- `docs/doc_index.md`
- `docs/start_here.md`
- `docs/status.md`
- `docs/next_patch.md`
- `docs/session_handover.md`
- `docs/book_contract.md`

## Immediate next work

Recommended next branch:
- `chore/post-v0.2.0-housekeeping`

That patch should stay docs/governance only and should cover:
- reciprocal repo links (`os-lem` <-> `os-lem-book`)
- branch/tag cleanup guidance
- stale milestone/debug branch review
- next-milestone planning handoff
