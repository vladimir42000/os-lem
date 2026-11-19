# OS-LEM session instructions

At the beginning of each development session, fetch the latest
`docs/PROJECT_CONTROL.md` from GitHub. Treat it as the authoritative
coordination record, verify the relevant commit IDs, and do not rely on
older chat summaries when they conflict with current repository evidence.

The source and test evidence at pinned commits is the technical truth;
the control record governs acceptance, release status, and scope. A branch
head is not accepted or publicly released merely because it exists.

Director authorizes bounded tasks and accepts milestones; Developer makes
only the authorized change and reports reproducible tests; Auditor verifies
independently before acceptance. If source evidence conflicts with this
record, stop and reconcile before implementing additional work.

Update `docs/PROJECT_CONTROL.md` only following an accepted milestone.
