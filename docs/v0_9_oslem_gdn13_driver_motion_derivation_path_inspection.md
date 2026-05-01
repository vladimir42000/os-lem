# OS-LEM GDN13 driver-motion derivation path inspection (v0.9 audit)

Patch: `AUDIT/oslem-gdn13-driver-motion-derivation-path-inspection`  
Base: `d936ffd` - Export GDN13 normalized model packet for OPT  
Branch: `proof/poc3-blh-benchmark-pass1`  
Document type: audit-only inspection note

## A. Accepted GDN13 OPT-facing state at d936ffd

The accepted OPT-facing state at `d936ffd` is:

- accepted GDN13 low-frequency parity gate exists;
- accepted GDN13 normalized model packet exists;
- the packet exports a solver-facing `model_dict`;
- the packet exports `frequencies_hz`;
- solver callable: `os_lem.api.run_simulation(model_dict, frequencies_hz)`;
- SPL convention for the accepted GDN13 case: `spl_total_diagnostic`;
- impedance convention: `abs(zin_complex_ohm)`;
- `full_band_spl_claim = false`;
- `mouth_only_spl_claim = false`;
- normalization and model construction remain os-lem-owned.

The accepted model-packet path is expected to be owned by `src/os_lem/gdn13_offset_tqwt_opt_model_packet.py`.  
The accepted low-frequency parity gate path is expected to be owned by `src/os_lem/gdn13_offset_tqwt_opt_parity_gate.py`.

## B. Current OPT blocker

OPT currently requires an accepted `cone_excursion_mm` output surface with this shape/convention:

- one-dimensional array;
- real-valued;
- finite;
- same length as `frequencies_hz`;
- units: millimetres;
- solver/kernel-derived;
- aligned with the accepted GDN13 normalized model packet.

The accepted GDN13 OPT-facing packet does not currently establish such a field. Therefore the safe status for OPT remains:

`OPT-DEV-006 remains blocked_pending_kernel_driver_motion_observable`

This audit specifically rejects no optimizer-side reconstruction of cone excursion from SPL, score, or external assumptions.

## C. Source inspection summary

Inspected source targets requested by the handoff:

- src/os_lem/solve.py: present; motion-keyword hits=369; result/output-keyword hits=32
- src/os_lem/api.py: present; motion-keyword hits=89; result/output-keyword hits=47
- src/os_lem/gdn13_offset_tqwt_opt_model_packet.py: present; motion-keyword hits=42; result/output-keyword hits=13
- src/os_lem/gdn13_offset_tqwt_opt_parity_gate.py: present; motion-keyword hits=43; result/output-keyword hits=15
- src/os_lem/reference_gdn13_offset_tqwt_mapping_trial.py: present; motion-keyword hits=89; result/output-keyword hits=54
- driver/electromechanical named modules discovered:
  - src/os_lem/driver.py
  - src/os_lem/reference_driver_front_chamber.py

Bounded grep command used for motion/electromechanical candidates:

```text
grep -RniE "excursion|displacement|diaphragm|cone|velocity|volume velocity|volume_velocity|source.*flow|flow|current|Bl|Sd|Mmd|Cms|Rms" src tests | head -n 250
```

Bounded grep command used for solver/result candidates:

```text
grep -RniE "result|frequency_hz|zin_complex_ohm|spl_total_diagnostic|spl_mouth|run_simulation|solve_frequency" src/os_lem | head -n 250
```

The inspection distinguishes three surfaces:

1. accepted public result truth returned by `os_lem.api.run_simulation`;
2. internal solver quantities that may exist transiently during solve;
3. candidate post-processing equations that would still need a kernel-owned output contract.

Only the first category is currently safe for OPT consumption without further os-lem export work.

## D. Candidate motion/flow fields found, if any

This audit finds no accepted OPT-facing public result field named `cone_excursion_mm`, diaphragm displacement, cone displacement, diaphragm velocity, or driver volume velocity in the exported GDN13 normalized model packet contract.

The accepted public solver outputs used by current GDN13 parity and packet exports are acoustic/electrical observables, especially:

- `frequency_hz`;
- `zin_complex_ohm`;
- `spl_total_diagnostic`;
- `spl_mouth` where available as a diagnostic/non-claim surface;
- other SPL diagnostic surfaces where exposed by existing result objects.

Motion-keyword grep excerpts are intentionally recorded in the probe file rather than treated as an export contract. The presence of names such as `Sd`, `Bl`, `Mmd`, `Cms`, or `Rms` in model construction is not by itself evidence that per-frequency cone motion is retained as accepted solver truth.

No current accepted result surface found by this audit is equivalent to a one-dimensional, real-valued, finite `cone_excursion_mm` array aligned with the GDN13 packet frequencies.

## E. Derivation feasibility

Classification:

`not_derivable_from_current_accepted_public_solver_result_surface`

The physically plausible derivation path would be:

```text
volume_velocity_at_driver_diagram [m^3/s]
  -> diaphragm_velocity = volume_velocity_at_driver_diagram / Sd
  -> displacement_m = abs(diaphragm_velocity) / omega
  -> cone_excursion_mm = 1000 * displacement_m
```

where `omega = 2*pi*frequency_hz` and `Sd` is the driver diaphragm area.

However, this derivation is safe only if os-lem can identify an unambiguous per-frequency driver diaphragm volume velocity or diaphragm velocity from existing solver truth. The current accepted GDN13 model packet and accepted `os_lem.api.run_simulation` result surface do not expose such a driver-motion state.

This means cone excursion is not presently derivable for OPT from accepted public solver truth without a new kernel-owned driver-motion observable or diagnostic export.

## F. Cone excursion convention recommendation, if derivable later

If a later os-lem diagnostic proves that a driver diaphragm volume velocity or diaphragm velocity is already computed internally and can be exported without a solver physics change, the future convention should be explicit before implementation:

- output name: `cone_excursion_mm`;
- shape: one-dimensional array aligned with `frequency_hz`;
- dtype/convention: real-valued magnitude;
- units: millimetres;
- frequency-domain convention: displacement magnitude derived as `abs(v_diaphragm) / omega`;
- amplitude convention: must state whether solver state is RMS, peak, or complex amplitude;
- source: kernel-derived from os-lem driver/acoustic state, not OPT-side reconstruction;
- invalidity handling: no silent zero-fill; no fallback from SPL.

Until this convention is proven, OPT must not infer cone excursion from SPL or impedance alone.

## G. Required future export contract, if derivable

If derivability is proven by a later bounded diagnostic or source-state inspection, the next export should be a separate DEV step, not this audit. Candidate future task name:

`EXPORT/gdn13-cone-excursion-output-surface-for-opt`

Required future export fields would include:

- `case_id`;
- `frequency_hz`;
- `cone_excursion_mm`;
- `cone_excursion_convention`;
- `cone_excursion_source`;
- `model_packet_callable`;
- `solver_callable`;
- `output_contract_status`;
- limitations and amplitude convention.

The future export must be blocked if the underlying driver-motion state is absent, ambiguous, or OPT-reconstructed.

## H. Reclassification recommendation, if not derivable

Current recommendation:

`blocked_pending_kernel_driver_motion_observable`

OPT should remain blocked for the cone-motion constraint. It should not remove the constraint, fabricate a proxy, derive motion from SPL, or duplicate os-lem model construction.

A safe next step is not optimizer implementation. The safe next step is a bounded os-lem-side diagnostic/spec step to determine whether an internal per-frequency driver motion/volume-velocity state is available and can be exposed with a precise amplitude convention.

## I. Explicit non-goals

This audit does not:

- implement `cone_excursion_mm`;
- change solver physics;
- change `os_lem.api.run_simulation` behavior;
- change API result fields;
- change optimizer behavior;
- change score or constraint behavior;
- remove the excursion constraint;
- fabricate excursion from SPL;
- add fallback normalization;
- add resonator semantics;
- expand graph/topology behavior;
- open Studio or public-promotion work.

No optimizer-side reconstruction is authorized.

## J. Exact next bounded recommendation

Recommended next bounded step:

`AUDIT/oslem-driver-motion-internal-state-and-amplitude-convention-probe`

Purpose of that next step:

- inspect whether existing internal solve state contains an unambiguous driver diaphragm volume velocity, diaphragm velocity, current-derived mechanical velocity, or displacement;
- identify exact file/function/symbol ownership;
- determine RMS/peak/complex-amplitude convention;
- prove whether exporting `cone_excursion_mm` would require no solver physics change, only a post-processing diagnostic/export, or an actual solver/model extension.

Until that diagnostic exists, `cone_excursion_mm` is not accepted as derivable from current os-lem solver truth for OPT consumption.
