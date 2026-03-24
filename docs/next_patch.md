# Next patch

## Current state

The `v0.2.0` milestone has completed its intended bounded patch sequence for
**offset-line observation-contract stabilization**.

The current milestone spine is:

1. docs/governance reset
2. `mouth_directivity_only` observation contract
3. mouth observable normalization guard
4. offset-line compare harness
5. `v0.2.0` release-notes draft

The compare harness and release-note draft mean the project is no longer in an
open-ended “what should we try next?” state inside `v0.2.0`.

## There is no default next development patch inside `v0.2.0`

The next action is now a **release-candidate review and release decision**.

That decision should explicitly answer:

- Are the current `v0.2.0` claims honest and bounded?
- Are the milestone docs aligned with the actual repository state?
- Is the release-notes draft accurate enough to ship with minimal edits?
- Is there any remaining issue that truly requires another bounded patch before release?

## Allowed outcomes from the release-candidate review

### Outcome A — release now

If the claims remain bounded and the release-story is coherent, the next step is:

- merge `milestone/v0.2.0-offset-line-observation` into `main`
- tag `v0.2.0`
- publish the release notes

### Outcome B — one final bounded close patch

Only if the release-candidate review surfaces a concrete and narrow issue should
one final patch be opened.

That patch must stay inside one of these categories:

- wording/claim correction
- release-note correction
- one tiny milestone-close validation/doc correction

It must **not** reopen broad debugging.

## Strict non-goals

Do not open a new default patch for:

- matrix assembly changes
- driver coupling changes
- broad radiator model redesign
- waveguide topology expansion
- frontend/UI work
- cleanup of old historical debug branches

## Startup rule for the next session

A new session should start by treating the milestone as **release-candidate ready**,
not as an open debugging branch.
