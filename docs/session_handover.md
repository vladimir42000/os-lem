# Session handover

## Handover state at director reset

Accepted working-line checkpoint at reset entry:
- branch: `chore/v0.4.0-close-decision`
- commit: `5cb5548`
- observed tests: `140 passed`

This checkpoint remains recoverable through the safety tag created before the reset branch is opened.

---

## What changed in this reset

This reset does not change solver code.
It changes the control plane so routine work runs through three roles:
- `DIRECTOR`
- `AUDIT`
- `DEV`

It also compresses live sequencing authority to:
- `docs/status.md`
- `docs/next_patch.md`
- `docs/session_handover.md`

---

## Required next action

The next action is **not** a DEV patch.
The next action is:
- `AUDIT: post-reset readiness check for v0.4.0`

That audit must decide whether the repo is:
- `READY` for one exact next bounded DEV patch, or
- `NOT READY`, requiring one exact bounded reset/decision patch first.

---

## Important caution

Do not reuse the older `close-prep` / `close-decision` / `release-promotion-plan` sequence automatically.
After this reset, that sequence must be re-validated from current repo truth by AUDIT before DEV proceeds.
