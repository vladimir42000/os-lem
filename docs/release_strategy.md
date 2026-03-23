# os-lem release strategy

## Purpose

This document defines how `os-lem` moves from patch work to milestone integration to tagged releases.

The goal is to keep development disciplined while making project status visible.

---

## 1. Source of truth

The source of truth is, in this order:

1. current tested repository state
2. current branch and commit history
3. current milestone branch, if one exists
4. release planning docs
5. older planning / handover text
6. parallel book commentary

Tarballs are backup or handover artifacts.
They are not the primary source of truth when they disagree with the live repo.

---

## 2. Branch roles

### `main`
`main` is the released / stable branch.

Rules:
- do not develop directly on `main`
- do not merge unfinished work into `main`
- every commit on `main` should be acceptable as a release candidate
- tags are created from `main`

### `milestone/*`
A `milestone/*` branch is the integration branch for the next planned release.

Rules:
- one active milestone branch at a time unless explicitly justified
- short-lived patch branches should normally branch from the active milestone branch
- milestone branches collect validated, bounded patches for one release target

Latest completed milestone lineage:
- `milestone/v0.1.0-foundation`

Recommended next milestone branch:
- `milestone/v0.2.0-offset-line-observation`

### Short-lived patch branches
Use short-lived branches for bounded work:

- `feature/*` — new capability within agreed scope
- `fix/*` or `bugfix/*` — targeted corrective change
- `debug/*` — diagnosis, root-cause isolation, truth-finding
- `chore/*` — docs, examples, governance, non-kernel maintenance

Rules:
- one patch = one purpose
- keep branches narrow
- do not mix unrelated work

---

## 3. Promotion flow

Default flow:

1. inspect repo truth
2. branch from the active milestone branch when it exists
3. implement one bounded patch
4. run tests
5. align directly affected docs only
6. commit the patch
7. merge the patch into the milestone branch
8. continue until the milestone is release-ready
9. merge the milestone into `main`
10. tag the release on `main`

Preferred direction:

`patch branch -> milestone branch -> main -> release tag`

---

## 4. Debug branch policy

`debug/*` branches are allowed for investigation and fault isolation.

However:
- a debug branch is not automatically release history
- if a debug branch contains long experimental lineage, do not merge it blindly
- either extract the proven narrow fix on a fresh patch branch
- or merge only the clean bounded part that has become milestone truth

The purpose of a debug branch is to discover repo truth, not to justify broad cleanup.

---

## 5. Versioning policy

`os-lem` uses pre-1.0 semantic versioning.

Format:
- `v0.1.0`
- `v0.1.1`
- `v0.2.0`
- ...
- `v1.0.0`

Interpretation:
- `0.x.0` = meaningful capability or maturity milestone
- `0.x.y` = stabilization / bugfix / docs / example hardening release on top of an existing milestone
- `1.0.0` = first coherent, intentionally supported release with stable enough scope and documentation

---

## 6. Capability status vocabulary

Use these terms consistently:

- **Exploratory** — idea exists or debug investigation exists, but not a supported claim
- **Implemented** — code exists, but confidence or scope is still limited
- **Validated** — tests and/or focused comparisons support the narrow claim
- **Released** — included in a tagged release on `main`

Do not confuse:
- implemented
- validated
- released

---

## 7. Release criteria

A patch is eligible for milestone integration when:
- scope stayed bounded
- tests are green
- docs changed only where directly needed
- the patch does not broaden claims beyond evidence
- commit history remains understandable

A milestone is eligible for release when:
- included patches form one coherent release story
- the milestone branch is green
- supported capabilities are documented honestly
- examples are coherent enough for the claimed scope
- known non-claims are stated explicitly

---

## 8. Documentation discipline for releases

The following docs define release posture and should remain aligned:

- `docs/doc_index.md`
- `docs/start_here.md`
- `docs/current_scope.md`
- `docs/status.md`
- `docs/milestone_charter.md`
- `docs/release_strategy.md`
- `docs/release_plan.md`
- `docs/capability_matrix.md`

Planning docs such as `docs/next_patch.md`, `docs/patch_registry.md`, and `docs/session_handover.md` must be verified against repo reality before being trusted.

---

## 9. Scope discipline

Release management must not become an excuse for broad refactors.

Rules:
- no history rewriting for cosmetic reasons
- no broad repo cleanup during release planning
- no mixing governance work with kernel changes
- no freezing unsupported contracts too early

---

## 10. Current release posture

Latest released baseline:
- `v0.1.0`

Current active planning target:
- `v0.2.0`

Current intended release story:
- `offset-line observation-contract stabilization`

Current best-supported opening move after the docs reset:
- one bounded observation-layer patch implementing or testing `mouth_directivity_only`
- keep `front` unchanged
- validate narrowly against the existing offset-line case
