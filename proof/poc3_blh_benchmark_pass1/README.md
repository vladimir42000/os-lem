# POC3 BLH benchmark pass 1

This benchmark builds the first os-lem pass for the supplied back-loaded horn case using the cleaned no-fill Hornresp source and the supplied AkAbak / Hornresp export surfaces.

## Primary truth source and interpretation support

Primary benchmark truth:
- `source_inputs/poc3.txt`
- `source_inputs/poc3_hr_all.txt`

Interpretation support:
- `source_inputs/poc3.aks`
- `source_inputs/VisatonFRS8M.tsp`

Comparison surfaces:
- `source_inputs/poc3_hr_drv.txt`
- `source_inputs/poc3_hr_mth.txt`
- `source_inputs/poc3_hr_all.txt`
- `source_inputs/POC3SP.FRD`
- `source_inputs/POC3PHS.FRD`
- `source_inputs/POC3IMP.ZMA`
- `source_inputs/POC3XCR.TXT`

The AkAbak schematic is used only to freeze the intended BLH topology:
- direct front diaphragm radiation
- rear node into a short constant-area throat chamber
- then two conical horn sections
- then one horn mouth radiator in `2pi`

## Exact os-lem mapping used in this pass

- Radiation space: `2pi`
- Source voltage: `2.83 V RMS`
- Source resistance: `0`
- Filling / stuffing: **not modeled because the cleaned source is explicitly no-fill**
- Front radiation element: `infinite_baffle_piston` with area `Sd = 22.00 cm2`
- Rear throat chamber mapping:
  - `Vtc = 600.00 cm3`
  - `Atc = 100.00 cm2`
  - mapped as a constant-area 1D section with `length = Vtc / Atc = 6.00 cm`
- Horn segment 1:
  - `24.00 cm2 -> 439.00 cm2`
  - `87.70 cm`
  - conical
- Horn segment 2:
  - `439.00 cm2 -> 736.00 cm2`
  - `30.90 cm`
  - conical
- Mouth radiation element: `infinite_baffle_piston` with area `736.00 cm2`

## Electrical / moving-mass assumptions

- `Le` is modeled in the pass-1 os-lem driver as `0.60 mH`
- The Hornresp source provides `Mmd = 0.81 g`
- The companion `VisatonFRS8M.tsp` file provides both:
  - `Mms = 0.87 g`
  - `Mmd = 0.81 g`
- This benchmark therefore uses:
  - `Mms = 0.00087 kg`
- No direct `Mmd -> Mms` identity mapping is used in this pass
- No extra air-load correction formula is introduced beyond the companion TSP value

## What is intentionally not modeled

This pass does **not** claim exact Hornresp or AkAbak semantic equivalence for:
- any internal end-correction convention beyond the current os-lem radiator/waveguide choices
- any AkAbak-specific driver inductance shaping beyond the simple `Le` value
- any higher-order radiation/directivity effect beyond the present piston-radiator surface
- any non-1D geometric detail outside the explicit chamber + two conical sections

## What is exported

Main os-lem exports:
- `oslem_spl_magnitude_db.txt`
- `oslem_impedance_magnitude_ohm.txt`
- `oslem_impedance_phase_deg.txt`
- `oslem_cone_excursion_displacement.txt`
- `oslem_spl_front_db.txt`
- `oslem_spl_mouth_db.txt`
- `run_summary.txt`

Comparison outputs:
- `comparison_outputs/*.txt`
- `comparison_outputs/comparison_summary.txt`

A standalone os-lem SPL phase export is **not** written in this pass, because the current high-level result surface used here provides SPL magnitude traces but not a dedicated truthful SPL phase observable.

## Reproducibility

From repo checkout root:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONPATH=src python proof/poc3_blh_benchmark_pass1/run_benchmark.py
```
