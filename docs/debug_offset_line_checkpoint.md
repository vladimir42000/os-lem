# Debug offset-line checkpoint

## Purpose

This document tracks the bounded Hornresp overlap workflow for the first `v0.2.0` offset-line investigation.

The goal is to keep the TL kernel frozen while tightening the comparison contract.

---

## Current conclusion before this patch

The current evidence already shows:

- input impedance is reasonably close
- cone excursion is extremely close once RMS-vs-peak is handled correctly
- driver phase largely collapses after 1 m reference removal + polarity flip
- port phase does **not** collapse nearly as well under that same global normalization

That means the next useful question is:

- can the remaining port-phase mismatch be explained by a simple additional mouth-only reference offset?

---

## Mouth observation contract isolation workflow

Use:

- `debug/export_offset_line_mouth_contract_compare.py`
- Hornresp FRD exports for driver and port

The script:

- keeps the driver normalization fixed
- applies the same global normalization to the port
- then scans an additional port-only reference distance offset
- reports the best-fitting extra distance and resulting phase metrics

This is a comparison-layer test only.
No kernel math is changed.
