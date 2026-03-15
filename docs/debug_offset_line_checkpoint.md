# Debug offset-line checkpoint

## Purpose

This document tracks the bounded Hornresp overlap workflow for the first `v0.2.0` offset-line investigation.

The goal is **not** to claim broad transmission-line support.

The goal is only to determine whether one minimal offset-line case overlaps acceptably with Hornresp in the current shared subset.

---

## Current repo truth before external overlap

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

That is an internal-truth result, not yet an external-validation result.

---

## Comparison workflow

Use:

- `examples/offset_line_minimal/model.yaml`
- `debug/export_offset_line_compare.py`
- `debug/hornresp_offset_line_reference.csv`

The reference CSV should be created by copying:

- `debug/hornresp_offset_line_reference_template.csv`

and filling the available Hornresp-exported columns.

Supported optional comparison columns:

- `zin_mag_ohm`
- `x_mm`
- `spl_total_db`
- `spl_mouth_db`

Required column:

- `frequency_hz`

---

## Recommended comparison priority

Start with:

1. `zin_mag_ohm`
2. `x_mm`

Only then consider SPL overlap, because SPL comparisons are more sensitive to convention mismatches.

---

## Interpretation policy

Possible honest outcomes:

### A. Minimal offset-line behavior already overlaps reasonably
This would support a narrow statement such as:

- minimal offset-line topology is already partially valid in the current kernel

### B. Topology solves, but overlap is materially wrong
This would support a different narrow statement such as:

- minimal offset-line topology is representable, but one or more physics/convention corrections are still needed before validation claims

### C. Comparison workflow itself exposes convention mismatch first
This would support a statement such as:

- overlap evaluation requires a tighter comparison protocol before kernel conclusions can be drawn

Do not widen claims beyond the evidence.

---

## Current caution

This debug thread must remain bounded.

Do not mix into it:

- broad TL implementation work
- frontend work
- API redesign
- unrelated kernel changes
