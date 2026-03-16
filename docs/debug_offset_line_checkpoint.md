# Debug offset-line checkpoint

## Purpose

This document tracks the bounded Hornresp overlap workflow for the first `v0.2.0` offset-line investigation.

The goal is **not** to claim broad transmission-line support.

The goal is to determine whether one minimal offset-line case overlaps acceptably with Hornresp in the current shared subset, and then isolate the remaining SPL mismatch conservatively.

---

## Current conclusion before this patch

The current evidence already shows:

- input impedance is reasonably close
- cone excursion is extremely close once RMS-vs-peak is handled correctly
- simple external path-delay injection does not explain the remaining SPL mismatch

That means the next useful question is not "is the line solve broken?"

The next useful question is:

- which radiated contribution is diverging:
  - driver
  - mouth/port
  - or only the final sum?

---

## Contribution-isolation workflow

Use:

- `examples/offset_line_minimal/model.yaml`
- `debug/export_offset_line_contribution_compare.py`
- `debug/hornresp_offset_line_sum.frd`
- `debug/hornresp_offset_line_drv.frd`
- `debug/hornresp_offset_line_port.frd`

The script:

- parses Hornresp FRD amplitude + phase for each contribution
- computes os-lem complex driver, mouth, and summed pressures
- compares both SPL magnitude and phase
- reports overall and band-limited errors

---

## Interpretation policy

Possible honest outcomes:

### A. Driver matches, port mismatches
Then the remaining problem is likely in mouth-radiation / line-output observation behavior.

### B. Driver and port both match, sum mismatches
Then the remaining problem is primarily in summation convention or phase reference.

### C. Port matches, driver mismatches
Then front-radiator observation behavior is the main target.

### D. All three mismatch
Then the comparison contract itself still needs tightening before solver conclusions are drawn.

Do not widen claims beyond the evidence.
