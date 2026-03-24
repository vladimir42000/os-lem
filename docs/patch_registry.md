# Patch registry

## Active milestone

- Milestone: `v0.2.0`
- Milestone branch: `milestone/v0.2.0-offset-line-observation`
- Intent: offset-line observation-contract stabilization
- Status: **release-candidate ready**

## Landed milestone patches

| Order | Branch | Commit intent | Status |
|---|---|---|---|
| 0 | `chore/v0.2.0-docs-reset` | Reset `v0.2.0` docs and restructure debug archive | landed on milestone |
| 1 | `fix/v0.2.0-mouth-directivity-only` | Add `mouth_directivity_only` observation contract | landed on milestone |
| 2 | `fix/v0.2.0-mouth-observable-normalization-check` | Add mouth observable normalization guard | landed on milestone |
| 3 | `fix/v0.2.0-offset-line-compare-harness` | Add offset-line compare harness | landed on milestone |
| 4 | `chore/v0.2.0-release-notes-draft` | Draft `v0.2.0` release notes | landed on milestone |
| 5 | `chore/v0.2.0-release-candidate-close` | Close milestone into release-candidate state | active / to land |

## Current milestone assessment

The planned bounded `v0.2.0` work is now effectively complete. The remaining work
is release-candidate close and release decision support.

## No default technical follow-up patch

There is intentionally **no default next technical patch** queued after the
release-candidate close patch.

Any further patch before release must be justified as one of:

- a claim-correction patch
- a release-note correction patch
- a tiny final validation/doc correction

## Deferred after `v0.2.0`

The following topics belong to later milestones, not this one:

- broader transmission-line maturity work
- richer waveguide physics growth
- passive-radiator and multi-driver growth
- API/productization expansion
- large repository branch cleanup
