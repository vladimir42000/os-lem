# os-lem

## Public baseline

- Latest released version: `v0.3.0`
- Public branch of record: `main`
- Observed reproducible suite on the public release line: `127 passed, 1 failed`
- Public project posture: released `v0.3.0` baseline only
- Supported public scope: stable released baseline only; no working-line `v0.6.0` promotion and no `v0.7.0` opening are implied here
- Known bounded public-line failure at audit time: `tests/debug/test_offset_line_compare_harness.py` due to missing `debug/hornresp_offset_line_drv.frd`

Open, scriptable loudspeaker and enclosure simulator with a disciplined, test-first development style inspired by classic Akabak-era LEM workflows.

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
