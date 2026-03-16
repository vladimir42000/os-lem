# Debug offset-line checkpoint

## Purpose

This document tracks the bounded Hornresp overlap workflow for the first `v0.2.0` offset-line investigation.

The goal is **not** to claim broad transmission-line support.

The goal is only to determine whether one minimal offset-line case overlaps acceptably with Hornresp in the current shared subset, and then isolate the remaining SPL mismatch conservatively.

---

## Current repo truth before SPL isolation

The current repository already shows that a minimal offset-line topology can be expressed internally as:

- one closed stub `waveguide_1d`
- one main `waveguide_1d`
- shared junction at the driver rear node
- mouth radiator at the open end

The repo already proves this topology can:

- parse
- assemble
- solve
- expose internally consistent junction/profile behavior

External overlap already looks reasonably credible for:

- input impedance
- cone excursion, once RMS-vs-peak convention is handled correctly

The remaining large mismatch is concentrated in total SPL.

---

## Comparison workflow

Use:

- `examples/offset_line_minimal/model.yaml`
- `examples/offset_line_minimal_baffle_mouth/model.yaml`
- `debug/export_offset_line_compare.py`
- `debug/hornresp_offset_line_reference.txt` or `.csv`

The script now:

- treats Hornresp `Xd (mm)` as peak excursion
- compares it against derived `os-lem` peak excursion (`RMS * sqrt(2)`)
- emits both `oslem_x_rms_mm` and `oslem_x_peak_mm` in the CSV
- reports band-limited `spl_total_db` metrics

---

## A/B mouth-radiator test

Two bounded comparison models are provided:

### A. Current mouth model
- `examples/offset_line_minimal/model.yaml`
- mouth radiator: `unflanged_piston`

### B. Experimental baffle-mouth hypothesis
- `examples/offset_line_minimal_baffle_mouth/model.yaml`
- mouth radiator: `infinite_baffle_piston`

This is an experiment only.
Do not treat Test B as the new baseline unless the evidence supports it.

---

## Recommended comparison priority

1. `zin_mag_ohm`
2. `x_peak_mm`
3. `spl_total_db`
4. `spl_total_db` by bands:
   - 10–200 Hz
   - 200–1000 Hz
   - 1000–5000 Hz
   - 5000–20000 Hz

---

## Interpretation policy

Possible honest outcomes:

### A. A/B changes mostly affect SPL while `Zin` and `X` stay strong
This supports the view that the remaining mismatch is mostly in mouth-radiation / SPL observation behavior.

### B. A/B also damages `Zin` or `X`
This suggests the mouth-radiator hypothesis is not the right primary explanation.

### C. Low-band SPL is decent but high-band SPL remains poor
This strongly supports a source-spacing / phase-summation mismatch rather than a core TL-physics failure.

Do not widen claims beyond the evidence.

---

## Current caution

This debug thread must remain bounded.

Do not mix into it:

- broad TL implementation work
- frontend work
- API redesign
- unrelated kernel changes
