# TQWT + one-side-resonator optimization probe definition (v0.6.0)

## Purpose

This note defines a **single bounded engineering probe** above the current validated topology capability.

It does **not** introduce:
- a new product line
- a general optimization framework
- new topology-family growth
- solver redesign
- frontend or API expansion

The purpose is narrower:
- define a YAML-first optimization probe for one validated TQWT / offset transmission-line family
- keep the variable count small and explicit
- make the evaluation and score function auditable before any future implementation campaign

## Baseline topology family

The baseline family for this probe is fixed as:
- TQWT / offset transmission line
- conical main line
- no fill
- one fixed driver

This probe is **not** a new reusable family campaign. It is a bounded engineering probe defined on top of an already validated family.

## Allowed modification

Exactly one additional side resonator is allowed.

No more than one side element may be added, and it must be one of:
- `side_pipe`
- `chamber_neck`

Explicitly out of scope:
- multiple resonators
- resonator trees
- benchmark-family mixing
- broad topology growth

## Attachment definition

The single side resonator attaches at one position on the main line.

The attachment is parameterized by:
- `x_attach_norm`

Interpretation:
- normalized position along the main acoustic centerline span of the validated TQWT baseline
- `0.0` corresponds to the upstream start of the main line span used by the probe
- `1.0` corresponds to the downstream end of the main line span used by the probe

For future implementation, the attachment node is selected by a deterministic policy:
- map `x_attach_norm` to the nearest valid segment boundary or discretization boundary on the main line
- do not create a new topology family to support arbitrary graph surgery for this probe

## Parameterization

The probe keeps the variable count bounded.

### Active probe variables

The preferred bounded parameter set is:
- `x_attach_norm`
- `resonator_type` in `{side_pipe, chamber_neck}`
- `L_res_m`
- `S_res_m2`
- `V_res_m3` only when `resonator_type = chamber_neck`

### Frozen optional variable

A small driver-position offset is recognized as a possible future extension, but it is **not active in phase 1**.

For the probe definition it is frozen to:
- `driver_offset_norm = 0.0`

So phase-1 optimization remains a 4-variable continuous search plus 1 bounded discrete switch.

## Supported engineering encodings inside current repo-truth element space

This probe stays inside currently supported, repo-resident element space.

### `side_pipe`

Engineering encoding:
- one side branch attached to the selected main-line node
- represented by one `waveguide_1d` branch with conical profile and constant area
- terminated by a very small fixed end volume used as a bounded closed-end approximation for this engineering probe

This encoding is a **probe convention**, not a claim of final rigid-end physics.

### `chamber_neck`

Engineering encoding:
- one side `duct` neck attached to the selected main-line node
- one shunt `volume` at the far end of that neck

This encoding stays inside current repo-resident branch + shunt element space.

## Canonical YAML-first execution boundary

The canonical YAML template for this probe lives at:
- `proof/tqwt_side_resonator_optimization_probe_template.yaml`

The YAML contract is definition-first:
- it freezes the baseline family identifier
- it freezes the small parameter set
- it freezes the parameter-to-element mapping
- it freezes the objective and constraint surface

### YAML to model mapping

For future implementation, the mapping is:
1. load the frozen validated TQWT / offset-TL baseline model
2. apply the probe overlay from the YAML template
3. map the selected resonator variant into existing repo-resident elements
4. convert the resulting canonical model into the current runner input shape
5. evaluate it using the current runner path

The intended runner call is:
- `os_lem.api.run_simulation(model_dict, frequencies_hz)`

If a thin current repo-truth adapter is more accurate than calling the API facade directly, that is acceptable, but the evaluation surface must remain equivalent in outputs and scoring semantics.

## Evaluation outputs

The future evaluator for this probe must at minimum expose:
- SPL magnitude
- cone excursion / displacement magnitude

Optional but useful:
- input impedance magnitude / phase

The score definition below uses SPL and excursion only. Impedance is diagnostic, not part of the phase-1 score.

## Objective function

### Primary band

The probe objective is defined on:
- `40 Hz` to `250 Hz`

### Smoothing and ripple

Let the SPL magnitude in dB on the target band be lightly smoothed with a fixed centered moving-average window.

Frozen phase-1 smoothing constant:
- `smoothing_window_bins = 5`

Define:
- `ripple_db = max(smoothed_spl_band_db) - min(smoothed_spl_band_db)`

### Penalties

#### Excursion penalty

Let:
- `x_peak_mm = max(excursion_band_mm)`

Frozen phase-1 threshold:
- `excursion_limit_mm = 4.0`

Frozen phase-1 weight:
- `excursion_penalty_weight = 6.0`

Define:
- `excursion_penalty = 0`, if `x_peak_mm <= excursion_limit_mm`
- `excursion_penalty = excursion_penalty_weight * (x_peak_mm - excursion_limit_mm)`, otherwise

#### Output penalty

Let:
- `mean_spl_band_db = mean(smoothed_spl_band_db)`
- `baseline_mean_spl_band_db` be the corresponding mean SPL of the frozen baseline on the same band
- `mean_drop_db = baseline_mean_spl_band_db - mean_spl_band_db`

Frozen phase-1 tolerance:
- `allowed_mean_drop_db = 1.5`

Frozen phase-1 weight:
- `output_penalty_weight = 3.0`

Define:
- `output_penalty = 0`, if `mean_drop_db <= allowed_mean_drop_db`
- `output_penalty = output_penalty_weight * (mean_drop_db - allowed_mean_drop_db)`, otherwise

#### Geometry penalty

Invalid or degenerate geometry carries a hard penalty.

Frozen phase-1 value:
- `invalid_geometry_penalty = 1_000_000`

Geometry is invalid if any constraint in the next section is violated.

### Frozen total score

The phase-1 score is:

```text
score = ripple_db
      + excursion_penalty
      + output_penalty
      + geometry_penalty
```

Lower is better.

## Constraints

The phase-1 probe uses explicit hard bounds.

### Attachment bounds

- `0.15 <= x_attach_norm <= 0.85`

Reason:
- avoid trivial end-attachment solutions
- keep the search on the useful interior of the main line span

### Resonator length bounds

- `0.05 <= L_res_m <= 1.20`

Reason:
- avoid zero-length collapse
- avoid impractically long side elements for this bounded engineering probe

### Resonator area bounds

- `1.0e-4 <= S_res_m2 <= 6.0e-3`

Reason:
- avoid degenerate near-zero area
- avoid unreasonably large side apertures that would collapse the baseline family intent

### Chamber volume bounds

Only for `chamber_neck`:
- `2.0e-4 <= V_res_m3 <= 2.0e-2`

Reason:
- avoid vanishing chamber limit
- avoid chamber growth that effectively turns the probe into a different enclosure family

### Driver offset bound

Frozen in phase 1:
- `driver_offset_norm = 0.0`

The variable is recognized but not searched in this definition patch.

## Phase-1 execution plan

The probe execution plan is intentionally simple and debuggable.

### Phase 1

Use reproducible coarse random sampling with a fixed seed.

Frozen phase-1 plan:
- method: `random_uniform`
- seed: `2026`
- samples per resonator type: `256`
- total samples for the full phase-1 sweep: `512`

Reason:
- simple to debug
- easy to log and replay
- handles mixed discrete/continuous search without introducing a broader optimization framework

### Phase 2

Optional future extension only:
- local refinement around the best phase-1 candidates
- not implemented by this patch
- not required for the definition to be complete

## Required outputs for a future implementation

A future implementation of this probe should emit:
- best `N` solutions, with `N` explicitly chosen by the implementation task
- complete parameter sets for each reported solution
- corresponding rendered YAML files
- SPL plots versus baseline
- excursion plots versus baseline
- optional impedance comparison plots
- a short ranked summary table

This definition patch does **not** build that full pipeline.

## Success criteria

The future implementation should count as successful if it demonstrates all of the following:
- measurable ripple reduction in `40–250 Hz`
- no excursion explosion beyond the defined penalty envelope
- no degenerate geometry collapse
- explainable and repeatable behavior under repeated runs with the same seed and settings

## Failure criteria

The future implementation should count as failed or insufficient if it shows one or more of:
- chaotic objective behavior with no stable ranking
- repeated collapse into degenerate geometry
- no meaningful improvement over the frozen baseline
- kernel instability or unusable behavior for the defined probe
- drift into a broader optimizer or topology campaign

## Separation from POC3 benchmark control-plane work

This probe is explicitly separate from the current POC3 benchmark interpretation work.

It must **not** be used to:
- rewrite the current POC3 benchmark reading
- replace the benchmark-led v0.6 control-plane freeze
- imply that v0.6 has shifted from bounded benchmark/probe work into general productization

## Repo-resident scaffolding in this patch

This definition patch also adds bounded helper scaffolding:
- `src/os_lem/reference_tqwt_side_resonator_optimization_probe.py`
- `tests/reference/test_tqwt_side_resonator_optimization_probe_definition.py`

These files are intentionally small.
They exist only to make the parameter bounds, YAML rendering contract, and score math explicit and auditable.
