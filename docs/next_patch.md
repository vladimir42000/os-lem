# Next action

## Live rule

This file is the single live-action document.
It must stay aligned with `docs/status.md` and `docs/session_handover.md` without duplicating milestone decision history.

---

## Current state after post-front-chamber-throat-side-coupling bookkeeping

- active working-line milestone: `v0.5.0`
- accepted working branch: `feat/v0.5.0-seed-front-chamber-throat-side-coupling-topology`
- accepted working commit: `4e4fb45d6df5dce73ebd62a8d8448147680c8ef5`
- observed suite on the accepted working line: `targeted topology regression set 8 passed`
- latest landed validation patch on the line below it: `2fbb2c81955115b8c2356c38c333aeb30a2e57bb`
- latest landed topology patch on the accepted line: `4e4fb45d6df5dce73ebd62a8d8448147680c8ef5`
- carried statement: `No frontend contract change`

---

## Next live action

- `test/v0.5.0-front-chamber-throat-side-akabak-reference-smoke`

---

## Guard rail

Do not open another topology-seeding patch before this bounded validation patch is resolved.
Do not change the frozen frontend contract unless that validation patch proves a contract change is required.
