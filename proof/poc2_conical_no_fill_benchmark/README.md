# POC2 conical / no-fill benchmark realignment

This benchmark realigns the earlier proof-of-reality TQWT / offset-TL translation around the cleaner `POC2` source set.

## Primary truth source and interpretation support

- Primary benchmark truth: `source_inputs/poc2_hornresp.txt` and `source_inputs/poc2.txt`
- Secondary interpretation support: `source_inputs/poc2.aks`
- Secondary comparison surface: `source_inputs/POC2.FRD`, `source_inputs/POC2PH.FRD`, `source_inputs/POC2IMP.TXT`, `source_inputs/POC2XC.TXT`

The Hornresp/AkAbak schematic support is used to disambiguate the topology: the driver radiates directly from its front side, while the rear side connects to one closed stub and one mouth path.

## Exact os-lem mapping used in this pass

- Radiation space: `2pi`
- Source voltage: `2.83 V RMS`
- Source resistance: `0`
- Filling / stuffing: **not modeled**
- Front radiation element: `infinite_baffle_piston` with area `Sd = 132.70 cm2`
- Rear closed stub:
  - `393.71 cm2 -> 455.00 cm2`
  - `33.10 cm`
  - conical
- Rear mouth path:
  - `393.71 cm2 -> 196.00 cm2`
  - `129.90 cm`
  - conical
- Mouth radiation element: `infinite_baffle_piston` with area `196.00 cm2`

## What this benchmark claims

This is a **truthful pass benchmark**, not a semantic-equivalence claim for every Hornresp or AkAbak internal detail.
The intended claim is narrower:

- the geometry is now aligned to an explicitly conical, no-fill source case
- the topology now matches the supplied AkAbak/Hornresp interpretation more closely than the earlier pass
- the comparison should therefore be materially easier to interpret

## Driver moving-mass note

The supplied Hornresp case gives `Mmd = 15.21 g`.
The current os-lem explicit driver model expects `Mms`.

This benchmark keeps the mapping:

- `Mms = Mmd = 0.01521 kg`

but treats it only as a **declared approximation**.
No silent air-load correction is introduced in this pass, because that would require an additional boundary-condition assumption that is not uniquely justified by the supplied benchmark files alone.

## Remaining approximations vs Hornresp / AkAbak

The top remaining approximation sources in this realigned pass are:

1. `Mmd -> Mms` identity mapping, which is declared rather than treated as exact truth
2. radiation-model correspondence between Hornresp/AkAbak radiator semantics and the current os-lem piston-radiator choices
3. any solver-level differences outside the current benchmark surface

## What is exported

Main os-lem exports:

- `oslem_spl_magnitude_db.txt`
- `oslem_impedance_magnitude_ohm.txt`
- `oslem_impedance_phase_deg.txt`
- `oslem_cone_excursion_displacement.txt`
- `run_summary.txt`

Additional interpretive exports:

- `oslem_spl_front_db.txt`
- `oslem_spl_mouth_db.txt`
- `comparison_outputs/*.txt`

A standalone os-lem SPL phase export is **not** written, because the current high-level result surface used here exposes SPL magnitude traces rather than a dedicated truthful SPL phase observable.

## Reproducibility

From repo checkout root:

```bash
OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 \
PYTHONPATH=src python proof/poc2_conical_no_fill_benchmark/run_benchmark.py
```
