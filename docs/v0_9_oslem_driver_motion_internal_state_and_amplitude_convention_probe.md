# OS-LEM driver-motion internal state and amplitude convention probe (v0.9 audit, observations-list repair)

Patch: `AUDIT/oslem-driver-motion-internal-state-and-amplitude-convention-probe`  
Repair package: `_05`, using repo-supported `observations` list mechanism  
Base: `e277577` - Audit GDN13 driver motion derivation path  
Branch: `proof/poc3-blh-benchmark-pass1`  
Document type: audit/probe only

## A. Accepted starting point

The accepted starting point is commit `e277577` (`Audit GDN13 driver motion derivation path`) on branch `proof/poc3-blh-benchmark-pass1`.

Accepted GDN13 normalized model packet callable:

- `os_lem.gdn13_offset_tqwt_opt_model_packet.get_gdn13_offset_tqwt_normalized_model_packet_for_opt`

Accepted solver callable:

- `os_lem.api.run_simulation`

The accepted public state before this probe remains:

- `d936ffd` exports the accepted GDN13 normalized model packet for OPT;
- `e277577` audits the driver-motion derivation path;
- prior accepted classification: `not_derivable_from_current_accepted_public_solver_result_surface`;
- accepted SPL convention remains `spl_total_diagnostic`;
- accepted impedance convention remains `abs(zin_complex_ohm)`;
- `full_band_spl_claim = false`;
- `mouth_only_spl_claim = false`.

## B. Current blocker

`OPT-DEV-006 remains blocked_pending_kernel_driver_motion_observable` until an explicit OPT-facing export is accepted.

OPT correctly blocks because no accepted OPT-facing `cone_excursion_mm` output contract has yet been exported. The required future field remains:

- `cone_excursion_mm`;
- one-dimensional;
- real-valued;
- finite;
- same length as `frequencies_hz`;
- units: millimetres;
- kernel-derived;
- aligned with the accepted GDN13 normalized model packet.

This probe authorizes no optimizer-side reconstruction and no score/constraint change.

## C. Internal cone-motion machinery inspected

Source files and class/result surfaces inspected:

- `src/os_lem/api.py`: present; cone hits=15; displacement hits=7; velocity hits=23; observations hits=4; observable_contract hits=9; run_simulation hits=2
- `src/os_lem/solve.py`: present; cone hits=30; displacement hits=9; velocity hits=66; observations hits=0; observable_contract hits=109; run_simulation hits=0
- `src/os_lem/gdn13_offset_tqwt_opt_model_packet.py`: present; cone hits=0; displacement hits=0; velocity hits=0; observations hits=0; observable_contract hits=0; run_simulation hits=1
- `src/os_lem/gdn13_offset_tqwt_opt_parity_gate.py`: present; cone hits=0; displacement hits=0; velocity hits=0; observations hits=0; observable_contract hits=0; run_simulation hits=0
- `src/os_lem/reference_gdn13_offset_tqwt_mapping_trial.py`: present; cone hits=0; displacement hits=0; velocity hits=0; observations hits=1; observable_contract hits=0; run_simulation hits=4
- `tests/api/test_api.py`: present; cone hits=6; displacement hits=3; velocity hits=21; observations hits=11; observable_contract hits=4; run_simulation hits=27
- `SimulationResult` annotated fields observed: `model`, `observation_types`, `series`, `sweep`, `system`, `units`, `warnings`
- `SimulationResult` motion-like attributes observed: `cone_displacement_m`, `cone_excursion_mm`, `cone_velocity_m_per_s`

Bounded search commands used:

```text
grep -RniE "excursion|displacement|diaphragm|cone|velocity|volume velocity|volume_velocity|source.*flow|flow|current|Bl|Sd|Mmd|Cms|Rms" src tests | head -n 250

grep -RniE "result|frequency_hz|zin_complex_ohm|spl_total_diagnostic|spl_mouth|run_simulation|solve_frequency" src/os_lem | head -n 250

grep -RniE "observations|observable_contract|cone_velocity|cone_displacement|cone_excursion_mm" src tests | head -n 250
```

The repair specifically follows repo-visible test evidence for an `observations` list, including observation entries like:

```python
{"id": "xcone", "type": "cone_displacement", "target": "drv1"}
```

It also checks the repo-visible relationship asserted by API tests:

```python
result.cone_excursion_mm == abs(result.cone_displacement_m) * 1e3
```

## D. Probe method

The runtime probe used the accepted GDN13 normalized model packet callable:

```text
os_lem.gdn13_offset_tqwt_opt_model_packet.get_gdn13_offset_tqwt_normalized_model_packet_for_opt
```

Packet fields observed:

```text
baseline_parity_gate_reason, baseline_parity_gate_status, callable_path, case_id, export_commit_requirement, frequencies_hz, full_band_spl_claim, impedance_band_hz, impedance_metric, impedance_observable, impedance_parity_passed, impedance_reference, impedance_threshold, kernel_commit_basis, limitations, model_builder_path, model_construction_owner, model_construction_source, model_dict, mouth_only_rejected_observable, mouth_only_spl_claim, normalization_owner, normalization_source, packet_status, parity_band, parity_callable, solver_callable, spl_band_hz, spl_mae_db, spl_max_abs_db, spl_metric, spl_observable, spl_parity_passed, spl_reference, spl_rms_db, spl_rms_threshold_db, spl_threshold, ze_mae_ohm, ze_max_abs_ohm, ze_rms_ohm, ze_rms_threshold_ohm
```

Driver IDs detected from the accepted packet `model_dict`:

```text
['drv_gdn13']
```

The probe did not assume `drv1` unless the accepted packet model actually contained that ID.

The probe used a bounded deterministic frequency subset from packet `frequencies_hz`:

```text
[10.0, 14.504097, 21.036882, 30.512097, 44.25504, 64.187937, 93.098803, 135.031404, 195.850852, 284.063968, 412.009123, 597.582011]
```

The probe created a defensive copy of the accepted packet `model_dict` and added repo-supported observations:

```python
[
    {"id": "gdn13_cone_displacement", "type": "cone_displacement", "target": "<actual_driver_id>"},
    {"id": "gdn13_cone_velocity", "type": "cone_velocity", "target": "<actual_driver_id>"},
]
```

Then it ran:

```text
os_lem.api.run_simulation(model_dict_with_observations, bounded_frequencies)
```

This patch did not change solver physics, did not change API behavior, and did not add production code. Required literal audit phrase: no solver physics change.

## E. Probe result

Observation-list runtime attempts:

- driver target `drv_gdn13`: passed; mechanism: `model_dict observations list`
  - observations added: `[{'id': 'gdn13_cone_displacement', 'type': 'cone_displacement', 'target': 'drv_gdn13'}, {'id': 'gdn13_cone_velocity', 'type': 'cone_velocity', 'target': 'drv_gdn13'}]`
  - available motion-like fields: `series`, `cone_velocity_m_per_s`, `cone_displacement_m`, `cone_excursion_mm`
  - series observation IDs: `['gdn13_cone_displacement', 'gdn13_cone_velocity', 'spl_mouth', 'spl_total_diagnostic', 'zin']`
  - cone_excursion convention check: `{'verified': True, 'relation': 'cone_excursion_mm == abs(cone_displacement_m) * 1e3', 'max_abs_difference_mm': 0.0, 'displacement_complex_valued': True, 'displacement_complex_capable': True, 'excursion_real_valued': True, 'excursion_finite': True}`
  - accepted motion surface probe passed: `True`

Best verified observation-list success:

```json
{
  "accepted_motion_surface_probe_passed": true,
  "driver_id": "drv_gdn13",
  "excursion_convention_check": {
    "displacement_complex_capable": true,
    "displacement_complex_valued": true,
    "excursion_finite": true,
    "excursion_real_valued": true,
    "max_abs_difference_mm": 0.0,
    "relation": "cone_excursion_mm == abs(cone_displacement_m) * 1e3",
    "verified": true
  },
  "motion_fields": {
    "cone_displacement": {
      "access_error": "AttributeError(\"'SimulationResult' object has no attribute 'cone_displacement'\")",
      "available": false
    },
    "cone_displacement_m": {
      "available": true,
      "complex_capable": true,
      "dtype": "complex128",
      "finite": true,
      "length": 12,
      "matches_frequency_length": true,
      "real_valued": false,
      "sample": [
        "(0.0024191075146229-0.001070135413347141j)",
        "(0.0021247618167694617-0.0014932784605235767j)",
        "(0.0015110823272564467-0.001965127814907081j)"
      ],
      "shape": [
        12
      ]
    },
    "cone_excursion_mm": {
      "available": true,
      "complex_capable": true,
      "dtype": "float64",
      "finite": true,
      "length": 12,
      "matches_frequency_length": true,
      "real_valued": true,
      "sample": [
        2.6452355226339757,
        2.597016237659119,
        2.478930642165738
      ],
      "shape": [
        12
      ]
    },
    "cone_velocity": {
      "access_error": "AttributeError(\"'SimulationResult' object has no attribute 'cone_velocity'\")",
      "available": false
    },
    "cone_velocity_m_per_s": {
      "available": true,
      "complex_capable": true,
      "dtype": "complex128",
      "finite": true,
      "length": 12,
      "matches_frequency_length": true,
      "real_valued": false,
      "sample": [
        "(0.0672385910583531+0.15199700792366333j)",
        "(0.13608534688702076+0.19363364337685993j)",
        "(0.25974789820538896+0.1997327886475052j)"
      ],
      "shape": [
        12
      ]
    },
    "driver_volume_velocity_m3_per_s": {
      "access_error": "AttributeError(\"'SimulationResult' object has no attribute 'driver_volume_velocity_m3_per_s'\")",
      "available": false
    },
    "series": {
      "available": true,
      "keys": [
        "zin",
        "spl_mouth",
        "spl_total_diagnostic",
        "gdn13_cone_displacement",
        "gdn13_cone_velocity"
      ],
      "type": "dict"
    },
    "source_volume_velocity_m3_per_s": {
      "access_error": "AttributeError(\"'SimulationResult' object has no attribute 'source_volume_velocity_m3_per_s'\")",
      "available": false
    },
    "volume_velocity_m3_per_s": {
      "access_error": "AttributeError(\"'SimulationResult' object has no attribute 'volume_velocity_m3_per_s'\")",
      "available": false
    }
  },
  "observation_mechanism": "model_dict observations list",
  "observations_added": [
    {
      "id": "gdn13_cone_displacement",
      "target": "drv_gdn13",
      "type": "cone_displacement"
    },
    {
      "id": "gdn13_cone_velocity",
      "target": "drv_gdn13",
      "type": "cone_velocity"
    }
  ],
  "result_public_fields": [
    "model",
    "observation_types",
    "series",
    "sweep",
    "system",
    "units",
    "warnings"
  ],
  "run_status": "passed",
  "series": {
    "available": true,
    "gdn13_cone_displacement": {
      "available": true,
      "complex_capable": true,
      "dtype": "complex128",
      "finite": true,
      "length": 12,
      "matches_frequency_length": true,
      "real_valued": false,
      "sample": [
        "(0.0024191075146229-0.001070135413347141j)",
        "(0.0021247618167694617-0.0014932784605235767j)",
        "(0.0015110823272564467-0.001965127814907081j)"
      ],
      "shape": [
        12
      ]
    },
    "gdn13_cone_velocity": {
      "available": true,
      "complex_capable": true,
      "dtype": "complex128",
      "finite": true,
      "length": 12,
      "matches_frequency_length": true,
      "real_valued": false,
      "sample": [
        "(0.0672385910583531+0.15199700792366333j)",
        "(0.13608534688702076+0.19363364337685993j)",
        "(0.25974789820538896+0.1997327886475052j)"
      ],
      "shape": [
        12
      ]
    },
    "keys": [
      "gdn13_cone_displacement",
      "gdn13_cone_velocity",
      "spl_mouth",
      "spl_total_diagnostic",
      "zin"
    ],
    "type": "dict"
  }
}
```

Required checks performed when fields were available:

- `result.cone_displacement_m` availability;
- `result.cone_velocity_m_per_s` availability;
- `result.cone_excursion_mm` availability;
- direct `result.series` observation IDs where present;
- same length as the bounded frequency subset;
- finite values;
- complex-capable velocity/displacement values;
- real-valued `cone_excursion_mm`;
- verified relationship `cone_excursion_mm == abs(cone_displacement_m) * 1e3`.

## F. Amplitude convention reading

Amplitude convention conclusion:

`magnitude of complex displacement in millimetres: cone_excursion_mm == abs(cone_displacement_m) * 1e3`

If verified, this is a magnitude convention: `cone_excursion_mm` is the magnitude of complex displacement in millimetres. This probe does not assert RMS, peak, or peak-to-peak beyond repo-visible convention evidence. If the solver's underlying excitation amplitude basis is not otherwise specified by repo truth, RMS/peak/peak-to-peak remains outside this audit/probe.

## G. Derivability classification

Classification:

`derivable_existing_observation_mechanism`

This `_05` repair allows the explicit classification:

- `derivable_existing_observation_mechanism`

If a consumer requires the earlier enum name, this corresponds to:

- `derivable_existing_observable_contract`, with the important clarification that the actual repo mechanism is an `observations` list, not the earlier attempted `observable_contract` variants.

This classification is based on the bounded runtime probe and source inspection, not on SPL-derived reconstruction.

## H. Recommended next bounded step

Recommended next bounded step:

`EXPORT/gdn13-cone-excursion-output-surface-for-opt`

If classification is `derivable_existing_observation_mechanism`, the next DEV step may be:

`EXPORT/gdn13-cone-excursion-output-surface-for-opt`

That export is not implemented here.

If classification is not derivable or unclear, OPT remains blocked under:

`OPT-DEV-006 remains blocked_pending_kernel_driver_motion_observable`

## I. Explicit non-goals

This patch does not:

- export `cone_excursion_mm`;
- change solver physics;
- change API behavior;
- change optimizer behavior;
- change score/constraint behavior;
- authorize OPT-side reconstruction;
- add fallback normalization;
- add resonator semantics;
- open graph/topology expansion;
- open Studio/public-promotion work;
- alter `os_lem.api.run_simulation` semantics.

## J. Exact next bounded recommendation

The exact next step is the recommendation in section H. No OPT implementation is authorized by this audit/probe alone.

Most important control point: this step probes internal cone-motion state and amplitude convention only. It does not let OPT consume an unverified motion surface.
