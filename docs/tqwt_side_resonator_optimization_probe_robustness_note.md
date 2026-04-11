# TQWT side-resonator optimization probe robustness note (v0.6.0)

## Status

This note freezes the current robustness reading for the landed bounded engineering probe built on the validated TQWT / offset transmission-line family.

It is intentionally bounded to the current accepted repo truth above the existing TQWT probe line:
- `6baf52d` — `Add TQWT side resonator optimization probe definition`
- `2c11690` — `Add TQWT side resonator optimization probe phase-1 coarse search`
- `bf1b274` — `Add TQWT side resonator optimization probe phase-1 note`
- `6dc38d3` — `Add TQWT side resonator optimization probe repeatability and budget sensitivity`

This note exists so future sessions do not reopen the same bounded engineering reading as though repeatability and modest budget sensitivity were still completely unclassified.

## Fixed probe boundary

The current robustness reading remains bounded to the frozen engineering probe definition:
- validated TQWT / offset transmission-line family only
- conical
- no fill
- one fixed driver
- exactly one side resonator
- frozen score / penalty / constraint surface
- YAML-first execution boundary
- phase-1 coarse random search only
- fixed-seed, proof-sized bounded runs

This note does **not** broaden the probe into a general optimizer program.

## Evidence basis

This note is grounded in landed repo-resident proof surfaces only:
- `proof/tqwt_side_resonator_optimization_probe_definition.md`
- `proof/tqwt_side_resonator_optimization_probe_template.yaml`
- `proof/tqwt_side_resonator_optimization_probe_phase1_coarse_search.py`
- `proof/tqwt_side_resonator_optimization_probe_repeatability_and_budget_sensitivity.py`
- `src/os_lem/reference_tqwt_side_resonator_optimization_probe.py`
- `tests/reference/test_tqwt_side_resonator_optimization_probe_phase1_coarse_search.py`
- `tests/reference/test_tqwt_side_resonator_optimization_probe_repeatability_and_budget_sensitivity.py`

This note does **not** depend on local-only generated reports, plots, probe files, or ad hoc run dumps.

## Exact robustness question answered

The landed robustness proof answers a bounded question only:
- whether the positive phase-1 result remains interpretable under bounded reruns with different fixed seeds
- whether a modestly larger proof-sized sample budget materially changes the engineering reading
- whether the best region remains broadly stable enough that later bounded refinement discussion is at least reasonable

It does **not** answer a global-optimization question.

## Fixed robustness surface

The current bounded robustness surface is:
- same phase-1 search family only
- no local refinement
- no optimizer abstraction layer
- small fixed seed set
- two bounded proof-sized budgets
- unchanged score semantics relative to the frozen definition except for minimal implementation bugfixes already landed on the accepted line

That means the current reading is specifically about **repeatability and modest budget sensitivity inside the same coarse-search probe**, not about exhaustive search.

## Current robustness reading

Current repo truth now supports the following bounded reading:
- bounded reruns remain interpretable rather than chaotic
- improvement over baseline remains real across the bounded rerun surface
- the best region remains broadly stable across the bounded reruns
- a modestly larger proof-sized budget materially improves the median best score relative to the smaller proof-sized budget
- `chamber_neck` remains the dominant best-region reading in this bounded proof surface
- no instability, geometry collapse, or penalty-dominated pathology defines the best reported bounded runs

This is enough to say that the current positive phase-1 engineering reading is **robust enough to discuss a later bounded refinement step**, if that step is separately justified and kept tightly scoped.

## What this robustness result does imply

The current accepted repo truth supports these bounded conclusions:
- the frozen phase-1 engineering result is not a one-off chaotic artifact of a single bounded seed/run
- the current coarse-search score surface is usable enough for bounded engineering exploration on this probe
- the current best-region reading remains directionally stable under small rerun variation
- a modest budget increase improves the engineering reading without forcing a framework-scale campaign
- future sessions may responsibly discuss whether a later bounded refinement step is worth defining

## What this robustness result does not imply

The current accepted repo truth does **not** justify these claims:
- global optimality
- universal `chamber_neck` superiority across the family
- a need for a general optimizer framework
- justification for multi-resonator growth
- automatic requirement that phase-2 refinement must be landed immediately
- solver redesign
- API redesign
- frontend redesign

## Decision boundary for future sessions

Future sessions should use this note to distinguish clearly between:
- what is now robust enough to rely on
- what remains unproven
- what kind of next step is still bounded
- what kinds of expansion remain unjustified

### Robust enough to rely on

The following readings are now stable enough to use as control-plane truth:
- the bounded coarse-search probe works as an engineering probe on this validated topology family
- the score surface is usable and repeatable enough for bounded interpretation
- the best region is broadly stable under bounded reruns
- modestly larger proof-sized budgets improve the median best score without changing the work into a framework problem
- `chamber_neck` is the dominant best-region reading **within this bounded proof surface**

### Still unproven

The following remain open:
- whether a still larger but bounded budget would materially change the best-region reading
- whether any later local refinement would produce durable additional gain
- whether the currently observed best region transfers to materially different drivers, geometry families, or multi-resonator spaces
- whether a final engineering recommendation should be made beyond this bounded probe

### Still-bounded next-step shape

If a future implementation step is proposed, the current note supports only a **small, separately justified, bounded refinement discussion** such as:
- a tightly budgeted local refinement definition on top of the already-supported bounded region, or
- a similarly bounded engineering validation step that does not reopen the full search/program/framework question

### Still unjustified expansions

The following remain unjustified by current repo truth:
- optimizer framework build-out
- multi-resonator growth
- broader topology-family optimization campaigns
- product/framework language about os-lem as a generalized optimizer platform

## Durable truth versus local byproducts

Durable repo truth for this engineering-probe line lives in the committed definition/proof code, bounded tests, and curated notes.

The following remain non-authoritative unless explicitly curated later:
- local generated reports
- local plots
- local probe files
- ad hoc run artifacts

## Control-plane summary

The truthful current reading is:
- the TQWT + one-side-resonator engineering probe is now defined, implemented at bounded phase 1, and classified for bounded repeatability/budget sensitivity
- the positive phase-1 result is robust enough to support careful discussion of a later bounded refinement step
- but the line remains an engineering probe, not a general optimizer framework and not a claim of final best physics/design truth
