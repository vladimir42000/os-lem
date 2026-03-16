# Debug offset-line checkpoint

## Purpose

This document tracks the bounded Hornresp overlap workflow for the first `v0.2.0` offset-line investigation.

The goal is **not** to claim broad transmission-line support.

The goal is only to determine whether one minimal offset-line case overlaps acceptably with Hornresp in the current shared subset, and then isolate the remaining SPL mismatch conservatively.

---

## Critical implementation detail

The source-spacing isolation script must use:

- `radiator_observation_pressure(...)`

not:

- `radiator_spl(...)`

Reason:
- `radiator_observation_pressure(...)` returns complex far-field pressure
- `radiator_spl(...)` returns already-converted SPL in dB

Only the complex pressure form is valid for applying additional phase delay before summation.

---

## Source-spacing isolation workflow

Use:

- `examples/offset_line_minimal/model.yaml`
- `debug/export_offset_line_spacing_compare.py`
- `debug/hornresp_offset_line_reference.txt` or `.csv`

The script:

- solves the existing os-lem model without changing the kernel
- extracts the complex front and mouth radiator pressures separately
- computes:
  - co-located sum
  - delayed mouth sum with an extra path-length phase shift
- compares both against Hornresp SPL

The separation is supplied as:

- `--separation-m <value>`

Recommended first values:

- `0.0`
- `1.15`

---

## Interpretation policy

Possible honest outcomes:

### A. Delayed summation substantially improves HF SPL
This strongly supports the view that the remaining mismatch is mostly source-spacing / phase-summation related.

### B. Delayed summation does not materially help
Then the next likely target is a different radiation/directivity/loading convention mismatch.

### C. Delayed summation improves only a narrow band
Then the next step is to identify whether the correct path-length offset is different from the current simple guess.

Do not widen claims beyond the evidence.
