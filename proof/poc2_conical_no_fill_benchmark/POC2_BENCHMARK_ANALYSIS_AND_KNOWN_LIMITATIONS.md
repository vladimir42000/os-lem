# POC2 Benchmark Analysis and Known Limitations

## Purpose

POC2 is the current proof-of-reality reference benchmark for the os-lem direct-front plus rear-path TL / TQWT family. It was selected to remove the avoidable semantic ambiguity present in the earlier PoC and to isolate model-truth versus solver-truth more cleanly.

## Benchmark source set

The benchmark basis is the aligned POC2 source bundle:

- `poc2.txt`
- `poc2_hornresp.txt`
- `poc2.aks`
- `POC2.FRD`
- `POC2PH.FRD`
- `POC2IMP.TXT`
- `POC2XC.TXT`

Interpretation priority used for this benchmark:

1. conical / no-fill Hornresp case as primary truth source
2. AkAbak schematic / exported data as interpretation support and secondary comparison surface
3. os-lem benchmark model as the bounded truthful translation target

## Mapping choices that made POC2 apples-to-apples

The successful realignment depended on keeping only what current os-lem can represent truthfully:

- conical expansion only
- no stuffing / filling
- explicit direct-front radiation path
- explicit rear acoustic path to mouth
- clean radiation assumption aligned to current os-lem capability
- no silent Hornresp-specific semantic carry-over beyond what the os-lem model actually encodes

This made the benchmark materially cleaner than the previous PoC because the main geometry and loss assumptions were no longer cross-model guesses.

## What current os-lem represented truthfully

For POC2, current os-lem represented the following benchmark aspects truthfully enough for reference use:

- two-section conical 1D acoustic path geometry
- direct-front plus rear-path topology structure
- no-fill acoustic path
- explicit mouth radiation termination within current os-lem radiation vocabulary
- impedance magnitude trend comparison
- excursion / displacement trend comparison
- SPL magnitude trend comparison at benchmark level

## What was intentionally not modeled

The benchmark intentionally did **not** claim exact equivalence for the following:

- Hornresp-specific semantics beyond the aligned conical/no-fill case
- stuffing / filling behavior
- any silent loss-model fitting to force visual agreement
- any silent conversion from Hornresp `Mmd` to a more speculative corrected `Mms`
- any stronger semantic claim than a bounded truthful translation into current os-lem vocabulary

The current mass note remains explicit:

- `Mmd -> Mms` was kept as a declared approximation for this benchmark line
- no air-load correction was silently introduced

## Why the earlier PoC mismatch was misleading

The earlier PoC mismatch was not strong evidence of solver fantasy. It mixed several avoidable equivalence problems into one comparison:

- flare semantics were not cleanly aligned
- filling/stuffing semantics were not truthfully shared
- geometric interpretation had more ambiguity than the kernel could honestly support

That made the comparison look like a solver-level disagreement even though a large part of the mismatch was translation-level.

## Why POC2 is the correct reference benchmark

POC2 is the correct current reference benchmark because it removes those avoidable equivalence traps:

- conical instead of semantically ambiguous non-conical flare interpretation
- no fill instead of unsupported or weakly-supported damping equivalence
- explicit reference exports from Hornresp and AkAbak
- topology and observation choices that current os-lem can encode honestly

As a result, POC2 is much closer to an apples-to-apples proof-of-reality check for the present kernel line.

## Known remaining limitations

The remaining differences should now be interpreted as bounded model / implementation limitations, not as broad benchmark ambiguity.

Most likely remaining systematic sources are:

1. **high-frequency electrical behavior**, especially inductance / `Le` treatment and model-shape differences between tools
2. **radiation/end-condition differences**, including exact mouth treatment and any residual observation-surface mismatch
3. **moving-mass semantics**, because `Mmd -> Mms` is still an explicit approximation, not an exact semantic identity
4. **1D path idealization**, especially where real tools differ in small implementation details around coupling and termination

The most likely visible systematic difference to watch first is:

- **HF divergence likely driven primarily by `Le` / electrical high-frequency behavior rather than by the main low-frequency acoustic path translation**

## Freeze statement

POC2 is frozen as the current proof-of-reality reference benchmark for this kernel line.

Use it as the first benchmark when checking future changes to:

- direct-front plus rear-path TL / TQWT behavior
- impedance trend coherence
- excursion trend coherence
- SPL trend coherence

Do not replace POC2 with a looser or more ambiguous benchmark without a clearer reference case.
