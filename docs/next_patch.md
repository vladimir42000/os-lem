# os-lem next patch

## Status

The bounded mouth normalization micro-check has now been implemented around the existing `mouth_directivity_only` contract.

Current post-patch reality:
- `front/raw` remains unchanged by default
- passive `mouth/port` radiators can still opt into `observable_contract: mouth_directivity_only`
- that candidate now explicitly requires the passive radiator area to match the unique connected duct / waveguide endpoint area
- the same physical mouth area is therefore frozen for both passive mouth flow semantics and `D(ka_mouth)`
- the suite is green at `117 passed` on this branch snapshot

---

## Immediate next patch target

**Add one narrow offset-line compare harness update that exercises the bounded mouth contracts without reopening broad debugging.**

Recommended clean patch branch after this patch merges:
- `fix/v0.2.0-offset-line-compare-harness`

---

## Purpose

The current milestone now has both:
- the opt-in `mouth_directivity_only` candidate
- an explicit area-consistency guard for that candidate

The next useful patch should therefore stay small and move one layer outward:
- add one maintained compare harness or regression fixture that uses the current bounded contracts in a repeatable way
- keep the result honest even if the residual mismatch remains

---

## Required scope

Do exactly these things:

- keep the current raw path unchanged
- keep the current area-consistency guard unchanged unless a direct bug is found
- add only one focused compare harness or regression fixture for offset-line observation semantics
- keep the patch evidence-oriented and bounded
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
- the new harness or fixture is explicit about which observation contract it is exercising
- any claim about remaining mismatch is stated honestly and locally

---

## Must-not-change list

- the released `v0.1.0` baseline
- the bounded `mouth_directivity_only` contract
- the new mouth-area consistency guard
- broad capability vocabulary
- unrelated waveguide or solver internals
- the small-patch discipline
