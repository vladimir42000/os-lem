# os-lem next patch

## Status

This file defines the single immediate next patch target for the next development session after the current release-readiness work is merged.

---

## Current checkpoint to verify at startup

Expected integration branch:
`milestone/v0.1.0-foundation`

Expected current posture:
- release governance docs landed
- milestone docs aligned to current repo truth
- maintained validation/example assets preserved
- release metadata aligned
- suite green

Expected suite:
`104 passed` or newer green equivalent

---

## Candidate next patch after startup verification

**Release `v0.1.0` from the current milestone, unless a concrete blocker is found**

Suggested immediate sequence:
1. final review of milestone contents
2. fast-forward `main` to the milestone head
3. create tag `v0.1.0`
4. prepare release notes / GitHub release text
5. only then select the first bounded post-`v0.1.0` patch

---

## Purpose

Freeze the first honest external release of `os-lem` without broadening capability claims.

---

## Required scope

Do exactly these things:

- verify that the milestone branch is green
- verify that README, package version, and release docs match the `v0.1.0` posture
- merge the milestone into `main` without introducing unrelated changes
- create the `v0.1.0` tag on `main`
- prepare release notes that describe both included scope and explicit non-claims

---

## Out of scope

- new solver/kernel changes
- new parser changes
- new frontend capability work
- transmission-line feature expansion
- broad API redesign
- broad roadmap rewrite beyond the release step
- post-`v0.1.0` feature work in the same patch

---

## Acceptance requirement

The release step is complete only if:

- `main` reflects the milestone head
- the repository remains green
- tag `v0.1.0` exists on the released commit
- public-facing release posture stays narrow and honest

---

## Must-not-change list

- current validated kernel behavior
- current conservative release posture
- milestone branch history
