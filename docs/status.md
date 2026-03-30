# os-lem status

## Released baseline

- latest released version: `v0.3.0`
- released branch of record: `main`
- observed green suite on the release line: `128 passed`

---

## Current accepted working-line truth

- active working-line milestone: `v0.5.0`
- accepted working branch for the current live control state: `feat/v0.5.0-seed-driver-front-chamber-topology`
- accepted working commit for the current live control state: `def4edae4839379ef50848fd6f79b32a50d6436a`
- observed green suite on the accepted working line: `201 passed`
- operator probe worktree state at bookkeeping time: no tracked modifications; local probe artifacts may be untracked

The current accepted working line is now ahead of the last bookkeeping checkpoint.
The latest landed chain above that older bookkeeping line is:
- `d161fae8fcc867c95920b82b5ae07509ede8bce0` — throat-side Akabak smoke comparison landed
- `def4edae4839379ef50848fd6f79b32a50d6436a` — driver-front chamber topology landed

---

## Milestone state

- active working-line milestone: `v0.5.0`
- milestone title: `opening decision`
- milestone branch of record: `milestone/v0.5.0-opening`
- milestone status: active on the working line

Latest landed bounded topology / validation chain on the accepted line:
- rear chamber tapped skeleton
- rear chamber tapped Akabak smoke
- rear-chamber port injection topology
- throat chamber topology
- blind throat-side segment topology
- throat-side Akabak smoke
- driver-front chamber topology

This remains a working-line capability-expansion track, not a public release promotion.

---

## Frontend contract state

- latest explicit frontend checkpoint: `81727af854207ccc94eeeede26988c688571cb30`
- carried statement on the current accepted line: `No frontend contract change`

The landed chain through `d161fae8fcc867c95920b82b5ae07509ede8bce0` and `def4edae4839379ef50848fd6f79b32a50d6436a` does not change the frozen frontend contract v1 surface.

---

## Current control-plane truth

- the accepted live control line is `def4edae4839379ef50848fd6f79b32a50d6436a`
- `d161fae8fcc867c95920b82b5ae07509ede8bce0` throat-side smoke is landed on the validated line below it
- `def4edae4839379ef50848fd6f79b32a50d6436a` driver-front chamber topology is landed on the current accepted line
- the single next live action is intentionally tracked only in `docs/next_patch.md`
