# AUDIT/v0.9.0-poc3-graph-solver-equivalence-gap-definition

## 1. Audit status

This document is an audit/specification checkpoint only.

It defines the currently visible gap between the graph-defined POC3 path and the accepted hand-mapped POC3 path before any further solver-equivalence implementation is opened.

This audit does not modify production code, tests, solver execution, graph compiler behavior, benchmark references, or public release state.

## 2. Accepted starting point

Current internal line:

- branch: `proof/poc3-blh-benchmark-pass1`
- latest accepted commit: `573945e` -- `Add POC3 graph-defined solver execution diagnostic smoke`
- relevant preceding accepted anchor: `7b0df05` -- `Map acoustic chamber to solver model for POC3 anchor`

Accepted current reading at `573945e`:

- the graph-defined POC3 payload validates;
- the graph-defined POC3 payload compiles;
- the graph-defined POC3 payload runs through `os_lem.api.run_simulation` on a bounded frequency surface;
- the accepted hand-mapped POC3 payload also runs through the same solver boundary on the same bounded frequencies;
- this is a `POC3 graph-defined solver execution diagnostic`, not solver equivalence.

Accepted limitation:

- `solver_equivalence_status = not_established_requires_later_alignment`
- `later_equivalence_alignment_required = true`
- `thresholds_used_for_equivalence = None`

Visible diagnostic differences from the accepted smoke:

- `zin_complex_ohm` max_abs about `1.1685 ohm`
- `spl_front` max_abs about `2.1568 dB`
- `spl_mouth` max_abs about `4.0378 dB`
- `spl_total` max_abs about `2.5908 dB`

Visible chamber limitation:

- `graph_acoustic_chamber_count = 0`
- `graph_acoustic_chamber_records = []`
- `chamber_bearing_proof_status = not_established_by_current_poc3_graph_helper`

## 3. Inspection targets

This audit target is bounded to the following files and paths:

- `tests/graph/test_poc3_graph_defined_solver_equivalence_smoke.py`
- `tests/graph/test_poc3_blh_graph_to_handmapped_construction_equivalence_smoke.py`
- `tests/graph/test_acoustic_chamber_solver_model_mapping_for_poc3_anchor.py`
- `src/os_lem/acoustic_graph_ir.py`
- `proof/poc3_blh_benchmark_pass1/model.yaml`

Optional context targets for a later local confirmation pass:

- existing POC3 benchmark helpers;
- `proof/poc3_blh_benchmark_pass1/run_benchmark.py`;
- any POC3 authority loading helper used by the graph tests.

This document intentionally records the gap definition. It does not implement repair logic.

## 4. Graph helper/path inspected

The current graph-defined POC3 diagnostic path is understood as:

1. `tests/graph/test_poc3_graph_defined_solver_equivalence_smoke.py` imports the construction helper by file path.
2. That helper is `tests/graph/test_poc3_blh_graph_to_handmapped_construction_equivalence_smoke.py`.
3. The helper loads the accepted hand-mapped POC3 authority from `proof/poc3_blh_benchmark_pass1/model.yaml`.
4. The helper constructs the graph IR through `_poc3_graph_from_authority(...)`.
5. The graph IR is validated with `os_lem.acoustic_graph_ir.validate_acoustic_graph_ir`.
6. The graph IR is compiled with `os_lem.acoustic_graph_ir.compile_acoustic_graph_ir_to_model_dict`.
7. The compiled graph model and hand-mapped model are both passed to `os_lem.api.run_simulation` on the bounded diagnostic frequency surface.

This is currently an execution diagnostic path. It is not a solver-equivalence path.

## 5. Hand-mapped POC3 authority path inspected

The accepted hand-mapped POC3 authority path used by the diagnostic and construction helper is:

- `proof/poc3_blh_benchmark_pass1/model.yaml`

The construction helper explicitly treats this file as the accepted hand-mapped POC3 construction authority.

## 6. Graph-level POC3 element inventory

Current diagnostic report inventory:

- graph model element count: `6`
- graph acoustic chamber count: `0`
- graph acoustic chamber records: `[]`

Current inferred graph-level element classes exercised by the POC3 helper:

- electrodynamic driver;
- horn/duct segment sequence;
- radiation load;
- possible closed termination depending on the authority projection;
- no demonstrated `acoustic_chamber` records in the current POC3 graph path.

The key gap is that the POC3 anchor was expected to exercise chamber semantics, but the diagnostic evidence does not yet prove that the current graph path is chamber-bearing.

## 7. Compiled solver-facing POC3 element inventory

Current diagnostic report inventory:

- graph solver-facing model element count: `6`
- hand-mapped solver-facing model element count: `5`
- graph solver-facing `acoustic_chamber` count: `0`

The `acoustic_chamber` compiler support itself has a separate positive mapping contract: chamber records can compile into solver-facing `acoustic_chamber` element records and into metadata under `graph_compiled_acoustic_chambers`.

However, the current POC3 graph-defined diagnostic does not show such chamber records for the accepted POC3 path.

Therefore the gap is probably not simply that the compiler cannot map `acoustic_chamber`. The more likely problem is that the current POC3 graph helper or accepted POC3 authority projection is not producing chamber-bearing graph IR for this case.

## 8. Hand-mapped POC3 element inventory

The accepted hand-mapped POC3 authority is `proof/poc3_blh_benchmark_pass1/model.yaml`.

The diagnostic report compares a hand-mapped model element count of `5` against a graph model element count of `6`.

The construction-equivalence helper explicitly keeps a chamber field visible in its bounded projection but records the current authority-derived chamber projection as empty rather than inventing chamber records that are not present in the hand-mapped authority surface.

This is a critical finding: the phrase “POC3 chamber-bearing anchor” is not yet supported by the current helper/authority projection that the diagnostic actually runs.

## 9. Chamber mapping comparison

Known accepted chamber mapping behavior:

- A minimal graph containing `acoustic_chamber` records can validate and compile.
- A `volume_l` chamber maps deterministically to a canonical solver volume string such as `0.0075 m3`.
- A `volume_m3` chamber maps deterministically to a canonical solver volume string such as `0.00125 m3`.
- The compiler also records mapped chamber metadata through `graph_compiled_acoustic_chambers`.

Current POC3 diagnostic behavior:

- `graph_acoustic_chamber_count = 0`
- `graph_acoustic_chamber_records = []`
- `chamber_bearing_proof_status = not_established_by_current_poc3_graph_helper`

Audit conclusion:

The chamber compiler contract and the current POC3 helper behavior are not aligned in the accepted diagnostic. Before solver equivalence can be attempted, the project must determine whether the POC3 authority model really exposes chamber data to the helper, whether the helper drops or fails to discover it, or whether the POC3 anchor has been mislabeled as chamber-bearing at this graph stage.

## 10. Driver/source/front/rear convention comparison

The next implementation step must not assume the driver/source/front/rear convention is aligned.

The audit should compare, using the local repo truth:

- driver id;
- raw driver parameters;
- normalized driver parameters if derived from TS-classic authority fields;
- front node;
- rear node;
- source node;
- driver tap/source location;
- whether graph-side `front_node` and `rear_node` map to the same solver-side convention used by the accepted hand-mapped POC3 model;
- whether the graph helper copies, derives, or defaults any source/front/rear field.

Current known risk:

The visible impedance and SPL differences could be consistent with a source/front/rear convention mismatch, especially if the graph path and hand-mapped path are not semantically identical even though both execute.

No repair is authorized by this document.

## 11. Horn/duct/radiation comparison

The next local audit pass should compare:

- horn/duct segment count;
- segment ids;
- segment ordering;
- segment connectivity;
- segment lengths;
- endpoint areas;
- flare/profile normalization;
- closed termination convention;
- radiation-load id;
- radiation node;
- radiation area;
- radiation space convention.

Current known risk:

The graph model element count `6` versus hand-mapped model element count `5` means dictionary-level shape is already different. Construction equivalence may still hold on a bounded projection, but solver equivalence cannot be claimed until the solver-facing semantic inventory is reconciled.

## 12. Observable convention comparison

The accepted diagnostic compared these solver fields:

- `frequency_hz`
- `zin_complex_ohm`
- `spl_front`
- `spl_mouth`
- `spl_total`

The current visible differences are:

- `zin_complex_ohm` max_abs about `1.1685 ohm`
- `spl_front` max_abs about `2.1568 dB`
- `spl_mouth` max_abs about `4.0378 dB`
- `spl_total` max_abs about `2.5908 dB`

The next local audit pass must check the observable convention, including:

- whether graph-side observations are copied from the authority or generated by compiler defaults;
- whether graph-side and hand-mapped SPL observation ids are identical;
- whether `spl_front`, `spl_mouth`, and `spl_total` are tied to the same physical nodes and radiation surfaces;
- whether any observable is a derived sum, a direct radiation result, or a convention-specific projection;
- whether front/mouth naming differs between construction and solver output layers.

Audit conclusion:

Observable convention drift remains a plausible mismatch source. It must be isolated before any solver-equivalence threshold is proposed.

## 13. Likely mismatch source

The most likely immediate gap is construction/semantic alignment, not numerical tolerance.

Priority ranking from current evidence:

1. Missing chamber-bearing graph construction evidence.
   - The POC3 anchor was expected to exercise chamber semantics.
   - `acoustic_chamber` compiler support exists.
   - The current diagnostic still reports `graph_acoustic_chamber_count = 0`.
   - The construction helper appears to expose an empty chamber projection rather than chamber records.

2. Graph helper / authority projection mismatch.
   - The current helper may be faithfully translating only what it sees in `proof/poc3_blh_benchmark_pass1/model.yaml`.
   - If the accepted authority stores chamber semantics under names not found by the helper, the graph can be solver-executable while still not representing the intended POC3 chamber-bearing topology.

3. Source/front/rear convention drift.
   - The driver and source conventions must be compared directly before any equivalence claim.

4. Observable convention drift.
   - SPL differences may be affected by observation id, node, radiation, and summation conventions.

5. Unit/area/length/segment ordering drift.
   - This remains possible, but the existing construction-equivalence helper reduces the likelihood that gross length/area normalization is the first problem.

## 14. Required answers to the audit questions

### Q1. What exact graph helper/path produced the current graph-defined POC3 model in commit `573945e`?

The current path is the POC3 graph-defined solver diagnostic importing the construction helper from `tests/graph/test_poc3_blh_graph_to_handmapped_construction_equivalence_smoke.py`, then using `_poc3_graph_from_authority(...)` on `proof/poc3_blh_benchmark_pass1/model.yaml`.

### Q2. Does that graph helper include `acoustic_chamber` elements at graph IR level?

Current diagnostic evidence says no for the accepted POC3 path:

- `graph_acoustic_chamber_count = 0`
- `graph_acoustic_chamber_records = []`

The helper may support chamber extraction in principle, but the currently loaded authority projection does not expose chamber records to the helper.

### Q3. Are `acoustic_chamber` records compiled into the solver-facing model representation for the current POC3 graph path?

Current diagnostic evidence says no for the accepted POC3 path.

Separate minimal chamber mapping tests show that `acoustic_chamber` can compile into solver-facing chamber records and metadata, so this is likely a POC3 helper/authority projection issue rather than a generic compiler mapping failure.

### Q4. Does the graph-defined POC3 construction still match the accepted hand-mapped POC3 construction projection after the chamber solver-model mapping step?

The construction-level helper reports bounded construction projection agreement, but that projection currently has an empty chamber field. Therefore it does not prove chamber-bearing construction equivalence.

### Q5. Do graph-defined and hand-mapped POC3 paths use exactly the same driver/source/front/rear, chamber, horn/duct, radiation, and observable conventions?

Not established by the current diagnostic.

This must be determined by local inventory comparison before any solver-equivalence claim.

### Q6. Are the visible solver-output differences consistent with missing chamber semantics, source/front/rear mismatch, segment mismatch, unit mismatch, observable mismatch, or expected approximation?

The visible differences are consistent with non-identical model semantics. Current evidence most strongly points to a graph helper / chamber-bearing construction gap, with source/front/rear and observable convention drift remaining plausible.

The differences should not be treated as a tolerance-selection problem yet.

### Q7. What is the single smallest next implementation step required before a solver-equivalence claim can be attempted?

The smallest next step is a non-solver implementation diagnostic that inventories and compares the graph IR, compiled solver-facing model, and hand-mapped authority projection for POC3, with explicit chamber/source/observable fields.

Recommended bounded next task:

`test/fix-v0.9.0-poc3-graph-helper-chamber-bearing-construction-alignment`

Open this only if the audit is accepted and if local inspection confirms that the current helper is missing chamber-bearing construction. Otherwise select one of the alternate next tasks listed below.

## 15. Recommended next bounded step

Recommended next step after this audit is accepted:

`test/fix-v0.9.0-poc3-graph-helper-chamber-bearing-construction-alignment`

Purpose:

- add or harden a construction-level inventory/projection test that proves whether the accepted POC3 authority path contains chamber semantics;
- if the authority does contain them, align the graph helper so it emits chamber-bearing graph IR;
- if the authority does not contain them, update claim wording so POC3 is not called a chamber-bearing graph anchor until a true chamber-bearing POC3 authority path is introduced.

Alternate next steps depending on local findings:

- if chambers compile but are hidden in probe terminology:
  `test/v0.9.0-poc3-chamber-bearing-graph-solver-diagnostic-probe-hardening`
- if source/front/rear convention differs:
  `fix/v0.9.0-poc3-graph-source-convention-alignment`
- if observable convention differs:
  `fix/v0.9.0-poc3-graph-observable-convention-alignment`

Do not open a solver-equivalence implementation until one of these semantic-alignment paths has landed and been audited.

## 16. Explicit non-claims and non-goals

This audit makes the following non-claims explicit:

- no POC3 solver-equivalence claim;
- no HornResp parity claim;
- no Akabak parity claim;
- no external parity claim;
- no OPT graph consumption;
- no Studio graph consumption;
- no Akabak parser;
- no HornResp importer;
- no arbitrary topology mutation;
- no graph expansion;
- no solver-core rewrite;
- no public promotion;
- no replacement of the accepted hand-mapped POC3 path.

The current accepted result remains:

- POC3 graph execution now runs;
- graph-vs-handmapped solver equivalence remains unresolved;
- the missing chamber-bearing proof must be diagnosed before repair by implementation.
