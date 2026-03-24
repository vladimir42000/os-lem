# os-lem next patch

## Status

The `mouth_directivity_only` observation-layer candidate has now been implemented as a bounded opt-in contract.

Current post-patch reality:
- `front/raw` remains unchanged by default
- passive `mouth/port` radiators can now opt into `observable_contract: mouth_directivity_only`
- API support exists for both `spl` and term-level `spl_sum` usage
- the suite is green at `114 passed` on this branch snapshot

---

## Immediate next patch target

**Do one narrow residual micro-check on mouth-path amplitude / normalization semantics, without reopening broad debugging.**

Recommended clean patch branch after this patch merges:
- `fix/v0.2.0-mouth-amplitude-microcheck`

---

## Purpose

The directivity candidate improved the observation contract coverage, but the handover evidence already suggested that the remaining discrepancy is more likely an amplitude / area / observable-definition issue than a generic solver bug.

The next patch should therefore stay tightly scoped to one of these micro-checks:

- mouth / port area consistency
- endpoint-flow normalization consistency
- explicit confirmation that the area used in `Q_mouth` and in `D(ka_mouth)` is the same physical mouth area

---

## Required scope

Do exactly these things:

- keep the current raw path unchanged
- keep `mouth_directivity_only` unchanged unless a direct bug is found in that specific implementation
- add only one narrowly targeted amplitude / normalization check
- add focused regression protection for whatever micro-check is implemented
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

- it stays narrow and evidence-driven
- the raw front path remains unchanged
- the suite remains green
- any claim about residual mismatch is stated honestly and locally

---

## Must-not-change list

- the released `v0.1.0` baseline
- the bounded `mouth_directivity_only` contract just added
- broad capability vocabulary
- unrelated waveguide or solver internals
- the small-patch discipline
