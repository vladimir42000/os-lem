# os-lem next patch

## Status

The `v0.2.0` release-note draft now exists and the milestone has reached its close-preparation phase.

Current post-patch reality:
- `front/raw` remains unchanged by default
- passive `mouth/port` radiators can still opt into `observable_contract: mouth_directivity_only`
- the bounded area-consistency guard remains active for that candidate
- the repository contains one maintained offset-line compare harness that reports:
  - `front_raw`
  - `mouth_raw`
  - `mouth_candidate`
  - `sum_raw`
  - `sum_candidate`
- the release-note draft now states the intended `v0.2.0` claim and non-claims explicitly
- the suite should remain green at `118 passed` on this branch snapshot

---

## Immediate next patch target

**Do one final `v0.2.0` scope-and-claim alignment pass before any merge to `main`.**

Recommended clean patch branch after this patch merges:
- `chore/v0.2.0-release-candidate-close`

---

## Purpose

The milestone now has its bounded implementation work and a release-note draft.

The next useful patch should therefore be a final close pass:
- make sure governance docs all tell the same release story
- remove any stale wording that still suggests the milestone is merely planned
- confirm that the release claim stays narrow and honest
- prepare the branch for the eventual merge/tag decision without performing that merge yet

---

## Required scope

Do exactly these things:

- keep solver behavior unchanged
- keep the compare harness unchanged unless a direct wording bug is found
- align release-facing and governance docs to the same narrow `v0.2.0` story
- keep the patch documentation-focused and bounded
- update only directly affected docs

---

## Out of scope

- broad transmission-line implementation work
- broad observation-layer redesign
- solver refactor
- frontend expansion
- new capability work
- unrelated kernel work
- broad restart of the debug tree
- actual merge to `main`
- release tag creation in the same patch

---

## Acceptance requirement

The next patch is complete only if:

- it stays bounded to wording and final milestone-close preparation
- docs no longer disagree about whether `v0.2.0` is active, in close phase, or still unopened
- it makes no unsupported parity claims
- the suite remains green
- the milestone is ready for a separate merge/tag decision after that close pass

---

## Must-not-change list

- the released `v0.1.0` baseline
- the bounded `mouth_directivity_only` contract
- the mouth-area consistency guard
- the maintained compare harness semantics
- broad capability vocabulary
- unrelated waveguide or solver internals
- the small-patch discipline
