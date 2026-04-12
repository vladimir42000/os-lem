# TQWT side-resonator optimization probe local-refinement pass 1 note (v0.6.0)

## Status

This note freezes the control-plane reading for the landed bounded local-refinement pass 1 on the TQWT + one-side-resonator engineering-probe line.

It is intentionally bounded to the accepted repo truth on `proof/poc3-blh-benchmark-pass1` through:
- `6baf52d` — `Add TQWT side resonator optimization probe definition`
- `2c11690` — `Add TQWT side resonator optimization probe phase-1 coarse search`
- `bf1b274` — `Add TQWT side resonator optimization probe phase-1 note`
- `6dc38d3` — `Add TQWT side resonator optimization probe repeatability and budget sensitivity`
- `bbcc198` — `Add TQWT side resonator optimization probe robustness note`
- `5c3e76d` — `Add TQWT side resonator optimization probe bounded local refinement definition`
- `9f37e88` — `Add TQWT side resonator optimization probe bounded local refinement pass 1`

This note exists so future sessions do not reopen the same local-refinement pass as though it were still an unclassified engineering outcome.

## Fixed refinement boundary

The landed local-refinement pass stays inside the already frozen engineering-probe contract:
- validated TQWT / offset transmission-line family only
- conical main line
- no fill
- one fixed driver
- exactly one side resonator
- same frozen score / penalty / constraint surface
- same bounded seed-selection rule from the landed coarse-search surface
- bounded coordinate search only
- fixed local budgets and stopping rules
- no framework abstraction
- no new variables
- no topology changes

This remains a bounded engineering probe, not a general optimizer product and not a new reusable topology-family campaign.

## Evidence basis

This note is grounded in landed repo-resident truth only:
- `proof/tqwt_side_resonator_optimization_probe_definition.md`
- `proof/tqwt_side_resonator_optimization_probe_phase1_coarse_search.py`
- `proof/tqwt_side_resonator_optimization_probe_repeatability_and_budget_sensitivity.py`
- `proof/tqwt_side_resonator_optimization_probe_bounded_local_refinement_definition.md`
- `proof/tqwt_side_resonator_optimization_probe_bounded_local_refinement_pass1.py`
- the minimal repo-resident reference/test surfaces landed with those steps

This note does **not** depend on local-only reports, plots, probe files, or ad hoc run dumps.

## Current landed refinement reading

The current durable control-plane reading is:
- bounded local refinement pass 1 was executed on top of the already robust coarse-search seed surface
- additional gain over the coarse-search seeds was demonstrated inside the frozen contract
- the pass stayed penalty-safe and non-degenerate within the bounded engineering reading
- the behavior remained interpretable and did not require new variables, new objective terms, or framework growth
- the result is sufficient to treat the engineering-probe technical scope as completed for `v0.6.0`

The exact per-seed classification labels remain carried by the landed proof surface itself. For control-plane purposes, the important durable fact is narrower: bounded local refinement produced additional gain without changing the frozen probe contract or creating pressure for broader optimizer expansion.

## What this pass does establish

The landed pass now supports these bounded conclusions:
- the TQWT + one-side-resonator engineering-probe line is technically capable of supporting:
  - a frozen definition
  - a bounded coarse search
  - a repeatability / budget-sensitivity reading
  - a bounded local-refinement step above the robust coarse-search region
- the local-refinement step remains interpretable under the frozen contract
- additional gain can be explored without reopening the global search problem
- penalties and geometry constraints remain part of the trusted interpretation surface rather than something bypassed by the refinement pass
- no further technical implementation is required for `v0.6.0` to establish the bounded engineering-probe claim

## What this pass does not establish

The landed pass does **not** justify these claims:
- global optimality
- universal chamber-neck superiority
- a general optimizer framework
- multi-resonator growth
- solver redesign
- API or frontend redesign
- a family-wide loudspeaker design recommendation
- a claim that the refined candidate is permanent final design truth

## Decision boundary for close-readiness work

For future control-plane sessions, the useful decision boundary is now:
- **already demonstrated**
  - one validated benchmark-led line for `v0.6.0`
  - one bounded engineering-probe line showing YAML-first parameterized search and bounded local refinement on a validated topology family
  - interpretable gain without framework expansion pressure
- **still unproven / not claimed**
  - global optimizer quality
  - family-wide optimum statements
  - multi-resonator generalization
  - product/framework-level optimizer claims
- **bounded next step, if any**
  - close-readiness audit / control-plane handling
- **still unjustified**
  - more implementation work by default
  - framework growth
  - solver/API/frontend campaigns tied to this engineering-probe line

The truthful reading is that `v0.6.0` is now technically complete in scope and ready for final close-readiness audit, not that every possible optimization question has been closed.

## Durable truth vs local byproducts

The following remain non-authoritative unless explicitly curated later:
- local JSON / Markdown reports
- local plots
- local probe files
- ad hoc run artifacts

Durable repo truth for this step lives in the committed proof code, committed definition notes, committed interpretation notes, and committed minimal reference/test surfaces.
