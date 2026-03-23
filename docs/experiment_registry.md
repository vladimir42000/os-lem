# Experiment registry

This file indexes the main debug and comparison scripts so future sessions can tell:
- what each script is for
- whether it is still operationally useful
- whether it is historical evidence only

---

## Active comparison/debug support

### `debug/export_offset_line_compare.py`
- purpose: main offset-line comparison harness against preserved reference data
- status: active support
- use when: checking the current overall overlap and tracking whether a bounded observation patch improves or degrades the case

### `debug/export_offset_line_mouth_contract_compare.py`
- purpose: isolates mouth-only reference/contract variants while keeping driver normalization fixed
- status: active support
- use when: validating mouth/port observation semantics specifically

### `debug/export_offset_line_mouth_observable_expert_audit.py`
- purpose: focused mouth-observable audit used during the latest debug cycle
- status: active support
- use when: comparing alternative mouth semantics or expert hypotheses

### `debug/export_offset_line_directivity_sensitivity.py`
- purpose: explores how directivity assumptions affect the offset-line compare
- status: active support
- use when: checking whether directivity alone can explain the remaining mouth mismatch

### `debug/export_hf_rolloff_fit_study.py`
- purpose: studies the high-frequency on-axis rolloff and comparison fit
- status: active support
- use when: validating on-axis piston/directivity assumptions without reopening broad debugging

---

## Historical but still useful lineage scripts

### `debug/export_closed_box_compare.py`
- purpose: sealed-box backend export used to localize the closed-box mismatch
- status: historical evidence
- note: root cause was already isolated and fixed; keep for reference, not as the current main validation surface

### `debug/export_free_air_directivity_confirmation.py`
- purpose: free-air directivity sanity script
- status: historical/supportive
- note: useful when checking observation-layer assumptions at a simpler boundary

### `debug/export_offset_line_segmentation_audit.py`
- purpose: ruled out line segmentation density as the dominant remaining mismatch source
- status: historical evidence

### `debug/export_offset_line_reference_contract_audit.py`
- purpose: reference-distance/contract isolation
- status: historical evidence

### `debug/export_offset_line_observer_phase_split_audit.py`
- purpose: phase-split auditing of the observer path
- status: historical evidence

### `debug/export_offset_line_contribution_compare.py`
- purpose: contribution separation and comparison
- status: historical evidence

### `debug/export_offset_line_convention_scan.py`
- purpose: contribution mapping / polarity-convention scan with solver math held fixed
- status: historical evidence, potentially reusable
- note: useful if `mouth_directivity_only` does not explain the remaining mismatch

---

## Output folders worth preserving

### `debug/offset_line_compare_out/`
- purpose: main compare output directory for the offset-line overlap work
- status: preserve

### `debug/offset_line_mouth_observable_expert_audit_smoke_out/`
- purpose: smoke-output folder for mouth-observable audit runs
- status: preserve only if it still helps operator review

---

## Registry rule

When a new debug script is added, record it here only if it has clear reuse value.
Do not catalog every one-off scratch experiment.
