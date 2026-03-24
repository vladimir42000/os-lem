# os-lem next patch

## Status

The bounded offset-line compare harness has now been added around the current mouth observation contracts.

Current post-patch reality:
- `front/raw` remains unchanged by default
- passive `mouth/port` radiators can still opt into `observable_contract: mouth_directivity_only`
- the bounded area-consistency guard remains active for that candidate
- the repository now contains one maintained offset-line compare harness that reports:
  - `front_raw`
  - `mouth_raw`
  - `mouth_candidate`
  - `sum_raw`
  - `sum_candidate`
- the compare harness keeps solver behavior unchanged and makes the remaining residual explicit instead of speculative
- the suite is green at `118 passed` on this branch snapshot

---

## Immediate next patch target

**Prepare the `v0.2.0` release-note draft and milestone-close wording while keeping unsupported claims out.**

Recommended clean patch branch after this patch merges:
- `chore/v0.2.0-release-notes-draft`

---

## Purpose

The current milestone now has:
- the opt-in `mouth_directivity_only` candidate
- an explicit mouth-area consistency guard for that candidate
- one maintained compare harness for the offset-line case

The next useful patch should therefore move from implementation to release wording:
- draft the `v0.2.0` release notes early
- state clearly what was stabilized
- state clearly what remains a bounded residual or deferred topic

---

## Required scope

Do exactly these things:

- keep the current raw path unchanged
- keep the current compare harness unchanged unless a direct wording bug is found
- draft release-note language and milestone-close wording only
- keep the patch documentation-focused and bounded
- update only directly affected docs

---

## Out of scope

- broad transmission-line implementation work
- broad observation-layer redesign
- solver refactor
- frontend expansion
- broad docs rewrite beyond directly affected files
- unrelated kernel work
- broad restart of the debug tree

---

## Acceptance requirement

The next patch is complete only if:

- it stays bounded to release wording and milestone close preparation
- it makes no unsupported parity claims
- the current bounded `v0.2.0` scope is described honestly
- the suite remains green
- the release-note draft is clear enough to support the eventual merge to `main`

---

## Must-not-change list

- the released `v0.1.0` baseline
- the bounded `mouth_directivity_only` contract
- the mouth-area consistency guard
- the maintained compare harness semantics
- broad capability vocabulary
- unrelated waveguide or solver internals
- the small-patch discipline
