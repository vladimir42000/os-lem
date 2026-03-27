# Next action

## Live rule

This file is the single live-action document.
It must stay aligned with `docs/status.md` and `docs/session_handover.md` without duplicating milestone decision history.

---

## Current state after post-reset close decision

- `v0.4.0` is closed on the working line
- decision base: `7e22c0e`
- observed suite at decision time: `140 passed`
- no successor milestone is open yet
- no routine DEV patch is frozen yet

---

## Next live action

- `AUDIT: post-v0.4.0 next-milestone readiness check`

---

## Guard rail

Do not reopen `v0.4.0` or guess a new DEV patch from older planning text.
The next bounded patch, if any, must be frozen only after that audit reads the current repo truth.
