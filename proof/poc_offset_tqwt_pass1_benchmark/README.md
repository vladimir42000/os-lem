# POC offset TQWT / offset TL pass-1 benchmark

This benchmark is an honest pass-1 Hornresp-to-os-lem translation for the supplied offset TQWT / offset TL case.

## Frozen modeling assumptions

- Source files used: `hornresp_source/poc.txt`, `hornresp_source/poc-tl-geometry.txt`, `hornresp_source/poc-plots.txt`.
- Frozen path interpretation:
  - section 1 = closed end to driver
  - section 2 = driver to mouth
- `Eg = 2.83 V RMS`
- `Rg = 0`
- `Fta` ignored
- radiation used in os-lem: `2pi`
- mouth termination proxy: `flanged_piston` radiator in `2pi`
- line geometry represented as **two conical 1D waveguide sections**:
  - `615.00 cm2 -> 529.91 cm2` over `28.30 cm`
  - `529.91 cm2 -> 176.00 cm2` over `117.70 cm`
- internal discretization uses one segment per centimeter (`29` and `118` segments)

## Driver mapping note

Hornresp source data provides `Mmd = 15.21 g` but the current os-lem explicit driver model expects `Mms`.
For this pass-1 benchmark, `Mmd` is mapped directly to `Mms = 0.01521 kg`.
No extra air-load or hidden mass correction is introduced.

## Filling / losses

Hornresp filling inputs are present in `poc.txt`, but this pass-1 benchmark does **not** claim an exact Hornresp filling equivalence.
The current run **ignores filling** rather than silently inventing a non-truthful mapping.

## Runtime safety for scripted runs

The first pass patch could oversubscribe BLAS / OpenMP worker threads on some operator machines.
This repair pass makes the scripted benchmark run operator-safe by default:

- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `NUMEXPR_NUM_THREADS=1`

These caps are applied by the patch workflow script and also default inside `run_benchmark.py` unless the operator explicitly overrides them before launch.
The benchmark scope and benchmark truth do **not** change.

## What is exported

Running `run_benchmark.py` writes plain-text comparison exports:

- `oslem_spl_magnitude_db.txt`
- `oslem_impedance_magnitude_ohm.txt`
- `oslem_impedance_phase_deg.txt`
- `oslem_cone_excursion_displacement.txt`
- `run_summary.txt`

## SPL phase

A standalone truthful SPL phase export is **not** written in this pass.
The current benchmark exports SPL magnitude only, because the current high-level result surface exposes SPL as dB magnitude rather than a dedicated SPL phase observable.

## Reproducibility

From repo checkout root:

```bash
OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 \
PYTHONPATH=src python proof/poc_offset_tqwt_pass1_benchmark/run_benchmark.py
```

## Probe file note

This repair pass writes its patch probe to a **new** filename so an earlier interrupted-run probe is not overwritten.
