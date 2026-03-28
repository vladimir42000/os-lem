# Next action

## Live rule

This file is the single live-action document.
It must stay aligned with `docs/status.md` and `docs/session_handover.md` without duplicating milestone decision history.

---

## Current state after successor-milestone decision

- `v0.4.0` remains closed on the working line
- named successor milestone: `v0.5.0`
- successor milestone title: `pending post-v0.4.0 readiness audit`
- no successor milestone branch is open yet
- no routine DEV patch is frozen yet
- retained technical decision base for the closed milestone: `7e22c0e`
- observed suite on the retained decision base: `140 passed`

---

## Next live action

- `AUDIT: v0.5.0 opening readiness check`

---

## Guard rail

Do not reopen `v0.4.0` or guess the first `v0.5.0` DEV patch from older planning text.
The first bounded `v0.5.0` patch, if any, must be frozen only after that audit reads current repo truth.
