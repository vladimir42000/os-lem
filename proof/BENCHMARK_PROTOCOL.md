# os-lem benchmark protocol

## Purpose

This protocol freezes the minimum benchmark discipline for benchmark-led development under `v0.6.0`.
It exists to keep future real-world comparison work honest, reproducible, and diagnostically useful.

The current reference-truth benchmark is:
- `proof/poc2_conical_no_fill_benchmark/`

POC2 is the current proof-of-reality anchor because it reduced avoidable model-equivalence ambiguity and produced a materially cleaner apples-to-apples comparison surface than the earlier offset-TQWT pass-1 PoC.

---

## Required comparison inputs

Every benchmark patch must provide all of the following.

1. **Primary source truth inputs**
   - the original external benchmark source files that define the case
   - examples: Hornresp input/export, AkAbak schematic/export, measured data, geometry tables

2. **Reproducible os-lem model input**
   - one explicit os-lem model file or equivalent declarative model asset

3. **Reproducible run/export path**
   - one script that can be executed from repo checkout without hidden manual steps

4. **Explicit assumptions note**
   - one short benchmark note or README that states the mapping assumptions and limitations

5. **Reference comparison surface**
   - at least one external comparison surface from the primary benchmark source
   - secondary comparison surfaces are encouraged when they improve interpretation

---

## Required exported outputs

Every benchmark patch must export plain-text outputs suitable for external plotting/comparison.

Minimum required outputs:
- SPL magnitude
- impedance magnitude
- impedance phase
- cone excursion or displacement

Optional only when truthful and available:
- SPL phase
- additional observables

A benchmark patch should also provide at least one compact comparison summary or helper table when that materially improves interpretability.

---

## Required assumptions note

The benchmark assumptions note must state, explicitly and briefly:
- which source set is treated as primary truth
- geometry/section mapping assumptions
- radiation-space assumption
- source-voltage / source-impedance assumption
- whether stuffing/filling/losses were modeled, ignored, or approximated
- any moving-mass mapping note such as `Mmd -> Mms`
- any omitted physics known to matter
- any quantity intentionally not exported because it would not be truthful

No benchmark patch may silently upgrade an approximation into a truth claim.

---

## What counts as acceptable alignment

Acceptable alignment does **not** require exact numerical identity.
It requires a comparison that is materially interpretable and diagnostically honest.

A benchmark result is acceptable when all of the following hold:
- geometry semantics are no longer materially ambiguous
- required outputs are present and reproducible
- dominant response structure is comparable on an apples-to-apples basis
- the remaining mismatch can be discussed in bounded technical terms
- the benchmark note makes clear what os-lem represented truthfully and what it did not

A benchmark may still be acceptable when a bounded systematic difference remains, provided the likely source is isolated honestly.

---

## What counts as failure or stop signal

A benchmark attempt must be treated as failure, or at least a stop-and-realign signal, when any of the following occurs:
- the case still depends on ambiguous geometry or flare-law semantics
- unsupported stuffing/filling/loss assumptions are silently reintroduced
- required exports are missing
- assumptions are not explicit
- the comparison is not materially cleaner/interpretable than the previous baseline
- os-lem produces NaNs, divergence, non-reproducible exports, or obviously unphysical curves
- the mismatch cannot be classified into a bounded cause family

When a stop signal is hit, the next step is not blind feature growth.
The next step is a bounded realignment or diagnosis patch.

---

## Required conclusion classification

Benchmark conclusions must distinguish between these categories.

### 1. Model-equivalence issue
The external case semantics and the current os-lem model are not actually one-to-one.
Examples:
- flare-law mismatch
- driver insertion semantics mismatch
- radiation/termination mismatch
- topology meaning collapsed into a simpler graph recipe

### 2. Missing-physics issue
The comparison is structurally aligned, but an omitted physical effect likely explains the residual mismatch.
Examples:
- stuffing/filling
- end correction differences
- inductance / `Le` high-frequency behavior
- air-load or moving-mass correction assumptions
- damping/loss mechanisms not represented in the benchmark model

### 3. Solver/pathology issue
The benchmark is structurally aligned, but the numerical result suggests instability, non-physical behavior, or internal pathology.
Examples:
- NaNs
- singular or unstable solves
- discontinuous output without a physical cause
- strong non-reproducibility

Every benchmark summary should say explicitly which of these categories dominates the observed mismatch.

---

## Current frozen benchmark-led rule

Until repo truth says otherwise:
- `POC2` is the reference-truth benchmark for this proof-of-reality sequence
- new benchmark work should improve interpretability, not maximize case complexity
- benchmark-led patches should prefer realignment and diagnosis before new topology growth
