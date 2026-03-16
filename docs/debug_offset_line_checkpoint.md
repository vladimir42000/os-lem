# Debug offset-line checkpoint

## Purpose

This document tracks the bounded Hornresp overlap workflow for the first `v0.2.0` offset-line investigation.

The goal is to keep the TL kernel frozen while tightening the comparison contract.

---

## Current conclusion before this patch

The current evidence already shows:

- input impedance is reasonably close
- cone excursion is extremely close once RMS-vs-peak is handled correctly
- driver, port, and sum SPL all show similar HF magnitude drift
- raw phase mismatch is large and similar for driver, port, and sum

That strongly suggests a comparison-layer phase-reference mismatch.

---

## Phase-reference isolation workflow

Use:

- `debug/export_offset_line_contribution_compare.py`
- Hornresp FRD exports for driver, port, and sum

The updated script now reports:

- raw phase metrics
- normalized phase metrics after:
  - removing a configurable observation distance
  - optionally applying a 180° polarity flip

Recommended first run for the current hypothesis:

- `--phase-reference-distance-m 1.0`
- `--phase-polarity-flip`

If normalized phase error collapses strongly, that supports the view that the remaining phase mismatch is observational, not a TL-physics failure.
