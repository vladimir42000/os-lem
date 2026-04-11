# POC3 benchmark analysis and known limitations (v0.6.0)

## Status

This document freezes the current benchmark reading for the landed `POC3` BLH pass-1 line.

It is intentionally bounded to the current accepted repo truth on `proof/poc3-blh-benchmark-pass1`:
- `e8e994d` — `Add POC3 BLH benchmark pass 1`
- `05e0733` — `Add general graph surface audit`
- `9262170` — `Freeze supported graph surface for v0.6.0`
- `c5d4a8d` — `Add POC3 mouth superposition semantics isolation`
- `ecb592d` — `Add POC3 benchmark analysis and known limitations`
- `a5957e7` — `Add POC3 mouth observation convention sensitivity`

This note exists so future sessions do not reopen the same residual as if it were still an unclassified failure, and so they also do not overclaim the later convention-sensitivity result as though it had silently replaced the accepted baseline.

## Evidence basis

This note is grounded in landed repo-resident evidence only:
- `proof/poc3_blh_benchmark_pass1/run_summary.txt`
- `proof/poc3_blh_benchmark_pass1/comparison_outputs/comparison_summary.txt`
- `proof/poc3_blh_benchmark_pass1/comparison_outputs/hornresp_vs_oslem_total_spl_db.txt`
- `proof/poc3_blh_benchmark_pass1/comparison_outputs/hornresp_vs_oslem_front_spl_db.txt`
- `proof/poc3_blh_benchmark_pass1/comparison_outputs/hornresp_vs_oslem_mouth_spl_db.txt`
- `proof/poc3_blh_benchmark_pass1/comparison_outputs/akabak_vs_oslem_total_spl_db.txt`
- `proof/poc3_blh_benchmark_pass1/oslem_spl_magnitude_db.txt`
- `proof/poc3_blh_benchmark_pass1/oslem_spl_front_db.txt`
- `proof/poc3_blh_benchmark_pass1/oslem_spl_mouth_db.txt`
- `proof/poc3_blh_benchmark_pass1/mouth_superposition_semantics_isolation.py`
- `proof/poc3_blh_benchmark_pass1/mouth_observation_convention_sensitivity.py`

This note does **not** depend on local-only generated plots, JSON reports, Markdown reports, or probe files.

## Fixed accepted benchmark baseline

### Stable quantitative baseline

The current accepted baseline reading is:
- `hornresp_total_spl_mae_db = 4.896901`
- `hornresp_front_spl_mae_db = 2.279926`
- `hornresp_mouth_spl_mae_db = 14.513826`
- `hornresp_impedance_mag_mae_ohm = 0.158622`
- `hornresp_impedance_phase_mae_deg = 0.691623`
- `hornresp_excursion_mae_mm = 0.174121`
- `akabak_total_spl_mae_db = 0.767164`
- `dominant_mismatch_classification = model-equivalence`

### Stable qualitative baseline reading

Current repo truth supports the following bounded baseline reading:
- electro-mechanical agreement is strong
- total SPL agreement is strong, especially versus AkAbak
- front SPL mismatch is moderate
- mouth-side SPL observation mismatch is the dominant residual
- the dominant mismatch remains classified as `model-equivalence`

This is enough to treat the current POC3 line as benchmark-meaningful.
It is not an unclassified benchmark failure.

## Mouth-side semantics isolation reading

The landed mouth-semantics isolation step sharpened the current interpretation without requiring broad solver growth.

### Candidate ranking against Hornresp mouth

The current direct mouth observation remains the closest landed candidate under phase-free `total - front` reinterpretation testing:
- `oslem_direct_mouth: mae_db = 14.513826`
- `oslem_implied_mouth_amplitude: mae_db = 17.750086`
- `oslem_implied_mouth_power: mae_db = 19.096039`

So the baseline residual is **not** improved by a simple phase-free `total - front` reinterpretation.

### Reconstruction and self-consistency reading

The landed surfaces also show:
- Hornresp mouth is not reproduced best by phase-free total/front magnitude reconstruction
- os-lem total is not reproduced by simple front-plus-mouth magnitude addition

This narrows the remaining issue away from naive magnitude-only arithmetic and toward a partition / convention / observation-side limitation.

### Frequency concentration of the baseline direct mouth residual

The accepted baseline direct mouth residual is not uniform across band:
- low band `[0, 200) Hz`: `mae_db = 0.176441`
- mid band `[200, 2000) Hz`: `mae_db = 4.837846`
- high band `[2000, 20000) Hz`: `mae_db = 42.715577`

So the current mouth residual is mainly a **high-band** issue, not a broad low-frequency collapse of the benchmark.

## Mouth observation / convention sensitivity reading

The later landed proof adds one bounded refinement **above** the frozen baseline reading.
It does not silently replace that baseline.

### Sweep boundary

The landed sensitivity proof stays inside current supported repo-resident convention space:
- same accepted `POC3` case only
- radiation space fixed at `2pi`
- front radiator model fixed at `infinite_baffle_piston`
- mouth radiator model swept only across supported mouth models:
  - `infinite_baffle_piston`
  - `flanged_piston`
  - `unflanged_piston`
- mouth observation contract swept only across:
  - `raw`
  - `mouth_directivity_only`

This keeps the proof diagnostic and bounded within current repo truth.

### Strongest reported supported variant

Within that supported convention space, the strongest reported variant is:
- `mouth_model = infinite_baffle_piston`
- `mouth_contract = mouth_directivity_only`

In the landed proof reading, this supported variant materially narrows the Hornresp comparison on the same case:
- mouth MAE improves from `14.513826` to `3.503930`
- total SPL MAE improves from `4.896901` to `2.562861`
- high-band mouth MAE improves from `42.546490` to `7.636978`

At the same time, the cross-tool tradeoff surface remains real:
- AkAbak total SPL MAE worsens from the frozen baseline `0.767164` to `3.845534`
- the baseline is therefore **not** silently superseded by this variant

### Supported reading of the result

The truthful bounded reading is:
- the remaining mouth-side residual is materially sensitive inside the currently supported mouth observation/radiator convention space
- the strongest supported variant improves the Hornresp mouth-side and total comparisons materially on the same benchmark case
- this is evidence of **supported-convention sensitivity**, not proof that the accepted default baseline should be replaced
- this is not proof that the strongest reported supported variant is the final correct physics story

## What the current POC3 benchmark does imply

The current accepted repo truth supports these bounded conclusions:
- the current POC3 pass is benchmark-meaningful
- the generic graph/compiler surface is strong enough to produce materially credible electro-mechanical and total-SPL behavior for this BLH case
- the remaining dominant residual is mouth-side and interpretation-limited rather than a blanket proof-of-reality failure
- the mouth-semantics isolation step materially sharpened the diagnosis without opening a new benchmark family or broad solver campaign
- the observation/convention sensitivity proof shows that the mouth-side reading changes materially inside current supported repo-resident convention space
- future sessions may use repo truth to distinguish between the frozen accepted baseline and the best reported supported sensitivity variant

## What the current POC3 benchmark does not imply

The current accepted repo truth does **not** justify these claims:
- a broad solver failure
- a stuffing/filling failure explanation for this current no-fill benchmark case
- an immediate broad solver redesign campaign
- a claim that simple phase-free mouth reconstruction explains the residual
- a claim of exact Hornresp or AkAbak semantic equivalence across all observation partitions
- a claim that `mouth_directivity_only` is now silently the default accepted benchmark interpretation
- a claim that the strongest reported supported variant is established final physics

## Current known limitations

The current bounded limitations that remain visible are:
- mouth-side reading still carries a partition / convention / observation limitation
- the dominant baseline mouth residual is concentrated in the high band
- the current high-level surface does not export a truthful total SPL phase observable
- exact cross-tool equivalence is still limited by current observation semantics and current 1D mapping choices
- the supported convention sweep exposes a real tradeoff surface rather than a uniquely closed answer
- the current note does not claim resolution of every radiator/directivity/end-correction convention difference

These are real remaining limitations, but they are not currently classified as broad numerical pathology.

## Control-plane use of this note

Future audit/dev sessions should use this note to distinguish clearly between:
- what is already known about the frozen accepted baseline
- what is newly known about supported-convention sensitivity above that baseline
- what remains limited
- what should not be re-litigated without new evidence

Specifically, absent genuinely new repo-resident evidence, future sessions should **not** reopen the current POC3 residual as though it still proved:
- a broad solver failure, or
- a stuffing omission failure

They also should **not** overclaim that the convention question is fully closed, or that the best supported variant has already replaced the accepted baseline by default.

The truthful current reading is therefore two-layered:
- accepted baseline remains frozen and benchmark-meaningful overall
- a later landed same-case proof shows meaningful supported-convention sensitivity above that baseline

## Reproducibility

From repo root, the landed benchmark and diagnostic surfaces can be reproduced with:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONPATH=src python proof/poc3_blh_benchmark_pass1/run_benchmark.py
PYTHONPATH=src python proof/poc3_blh_benchmark_pass1/mouth_superposition_semantics_isolation.py
PYTHONPATH=src python proof/poc3_blh_benchmark_pass1/mouth_observation_convention_sensitivity.py
```
