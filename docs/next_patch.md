# Next action

## Live rule

This file is the single live-action document.
It must stay aligned with `docs/status.md` and `docs/session_handover.md` without duplicating milestone decision history.

---

## Current state after post-driver-front-chamber bookkeeping

- active working-line milestone: `v0.5.0`
- accepted working branch: `feat/v0.5.0-seed-driver-front-chamber-topology`
- accepted working commit: `def4edae4839379ef50848fd6f79b32a50d6436a`
- observed suite on the accepted working line: `201 passed`
- latest landed validation patch on the line below it: `d161fae8fcc867c95920b82b5ae07509ede8bce0`
- latest landed topology patch on the accepted line: `def4edae4839379ef50848fd6f79b32a50d6436a`
- carried statement: `No frontend contract change`

---

## Next live action

- `test/v0.5.0-driver-front-chamber-akabak-reference-smoke`

---

## Guard rail

Do not open another topology-seeding patch before this bounded validation patch is resolved.
Do not change the frozen frontend contract unless that validation patch proves a contract change is required.
