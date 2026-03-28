# Next action

## Live rule

This file is the single live-action document.
It must stay aligned with `docs/status.md` and `docs/session_handover.md` without duplicating milestone decision history.

---

## Current state after `v0.5.0` opening

- active working-line milestone: `v0.5.0`
- active milestone branch of record: `milestone/v0.5.0-opening`
- opening decision carried forward from checkpoint: `c548267`
- no routine `v0.5.0` DEV patch is frozen yet
- retained technical decision base from the last closed milestone: `7e22c0e`
- observed suite on the retained decision base: `140 passed`

---

## Next live action

- `AUDIT: v0.5.0 first routine-patch freeze check`

---

## Guard rail

Do not reopen `v0.4.0` or guess the first routine `v0.5.0` DEV patch from older planning text.
The first bounded `v0.5.0` patch, if any, must be frozen only after that audit reads current repo truth.
