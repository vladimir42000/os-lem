# Next action

## Live rule

This file is the single live-action document.
It must stay aligned with `docs/status.md` and `docs/session_handover.md` without duplicating milestone decision history.

---

## Current state after post-driver-front-chamber-smoke bookkeeping

- active working-line milestone: `v0.5.0`
- accepted working branch: `test/v0.5.0-driver-front-chamber-akabak-reference-smoke`
- accepted working commit: `2fbb2c81955115b8c2356c38c333aeb30a2e57bb`
- observed suite on the accepted working line: `205 passed`
- latest landed topology patch immediately below the accepted line: `def4edae4839379ef50848fd6f79b32a50d6436a`
- latest landed validation patch on the accepted line: `2fbb2c81955115b8c2356c38c333aeb30a2e57bb`
- carried statement: `No frontend contract change`

---

## Next live action

- `feat/v0.5.0-seed-front-chamber-throat-side-coupling-topology`

---

## Guard rail

Do not open another docs-only patch before this bounded technical patch is resolved.
Do not broaden scope into passive radiator work, multi-driver active architecture, electrical-network graph work, or frontend redesign.
Do not change the frozen frontend contract unless that bounded technical patch proves a frontend contract change is required.
