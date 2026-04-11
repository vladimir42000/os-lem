# TQWT side-resonator optimization probe phase-1 note (v0.6.0)

## Status

This document freezes the current phase-1 interpretation for the landed TQWT + one-side-resonator engineering probe.

It is intentionally bounded to the current accepted repo truth above the validated working line:
- `6baf52d` — `Add TQWT side resonator optimization probe definition`
- `2c11690` — `Add TQWT side resonator optimization probe phase-1 coarse search`

This note exists so future sessions do not keep rediscovering the same phase-1 engineering-probe reading or overclaiming it as a general optimizer result.

## Evidence basis

This note is grounded in landed repo-resident material only:
- `proof/tqwt_side_resonator_optimization_probe_definition.md`
- `proof/tqwt_side_resonator_optimization_probe_template.yaml`
- `proof/tqwt_side_resonator_optimization_probe_phase1_coarse_search.py`
- `src/os_lem/reference_tqwt_side_resonator_optimization_probe.py`
- `tests/reference/test_tqwt_side_resonator_optimization_probe_definition.py`
- `tests/reference/test_tqwt_side_resonator_optimization_probe_phase1_coarse_search.py`

This note does **not** depend on local generated reports, local probe files, local plots, or other operator-only byproducts.

## Fixed probe boundary

The current landed probe remains strictly bounded to:
- validated TQWT / offset transmission-line family only
- conical
- no fill
- one fixed driver
- exactly one side resonator
- frozen score surface:
  - ripple in `40–250 Hz`
  - excursion penalty
  - output penalty
  - geometry penalty
- frozen geometric/attachment constraints from the definition patch
- phase-1 coarse search only
- fixed-seed, repeatable, bounded run discipline

The accepted baseline family is not redefined by this note.

## Current phase-1 reading

The current landed phase-1 reading is:

- the bounded coarse search ran successfully on the frozen probe definition
- the score surface was usable and non-chaotic for this engineering probe
- the reported bounded run evaluated its candidates successfully
- the best reported candidates materially improved score versus the preserved baseline entry
- the best reported candidates were not dominated by excursion, output, or geometry penalties
- the best region in the current bounded run appears to favor `chamber_neck` variants
- this is a same-probe engineering result, not a generalized family law

This is enough to treat the current phase-1 search as a truthful engineering-probe step rather than a failed or unusable optimization surface.

## What phase 1 now does establish

Current repo truth supports the following bounded conclusions:

- a YAML-first coarse-search execution path can be run repeatably on this frozen probe definition
- the frozen score/penalty/constraint surface is usable enough to rank candidates meaningfully in a bounded run
- the baseline entry can be preserved and compared against sampled solutions truthfully
- improvement over baseline is possible within the frozen same-case search space
- the reported best region in the current bounded run is compatible with `chamber_neck` resonator choices
- this probe can support a bounded future implementation step without first requiring a solver redesign or general optimizer framework

## What phase 1 does not establish

Current repo truth does **not** justify the following claims:

- global optimality
- a generally solved optimization problem for TQWT systems
- a general optimizer framework requirement
- a claim that `chamber_neck` is universally best for the broader family
- a claim that side-pipe variants are broadly ruled out in all future bounded runs
- new topology-family growth
- solver/API/frontend redesign
- replacement of the benchmark-led v0.6 control discipline

## Durable truth vs local byproducts

Durable repo truth lives in the landed definition, reference helper, bounded tests, and the landed phase-1 coarse-search script.

The following remain non-authoritative unless later curated explicitly:
- local generated JSON or Markdown reports
- local probe files
- local plots
- local ad hoc run artifacts

They may be useful operationally, but they are not the controlling truth for this note.

## What remains unproven

The following are still intentionally open:

- whether a larger bounded sample budget materially changes the currently observed best region
- whether a still-bounded follow-up on the same frozen definition should add a local refinement step
- how robust the current best region remains under carefully controlled same-probe reruns or slightly larger bounded searches
- whether a future bounded output-curation step is worth landing in repo truth

None of these open questions justify immediate framework expansion.

## Useful next-step discipline

Future sessions should use this note to distinguish between:

- what phase 1 already proved:
  - the frozen probe can run repeatably and yield meaningful ranked improvement over baseline
- what phase 1 did not prove:
  - global optimality, general optimizer needs, or general family laws
- what kind of next step would still be bounded:
  - a same-probe, still-repeatable follow-up such as modestly expanded coarse sampling or explicitly frozen local refinement on the same definition
- what kinds of expansion remain unjustified:
  - framework build-out
  - broader topology growth
  - solver redesign
  - productization language

## Separation from current POC3 control-plane work

This engineering probe does not replace or rewrite the current benchmark-led POC3 reading.

The truthful control-plane distinction remains:
- POC3 is the active benchmark-led cross-tool interpretation line
- the TQWT side-resonator work is a bounded engineering-probe line above validated topology capability

## Reproducibility

From repo root, the landed definition and phase-1 surfaces can be exercised with:

```bash
PYTHONPATH=src python proof/tqwt_side_resonator_optimization_probe_phase1_coarse_search.py
```
