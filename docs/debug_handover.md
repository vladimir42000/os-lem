# Debug handover

## Current posture

The major debug cycles that were previously active around sealed-box and bass-reflex discrepancies are no longer the primary development track.

Their outcomes are now already integrated into the current development line.

Normal development should proceed from:

- `milestone/v0.1.0-foundation`

Historical debug branches remain useful as diagnostic lineage:

- `debug/closed-box-mismatch`
- `debug/closed-box-radiator-fix`
- `debug/bassreflex-radiation-space`

Do not resume normal feature work on those branches.

---

## What the debug lineage established

### Closed-box debug result

The closed-box mismatch investigation localized a real low-frequency baffled-radiator reactance problem.

Root cause:
- bad low-frequency Struve behavior in the baffled-radiator reactance path

Bounded fix:
- replace the approximation path with `scipy.special.struve(1, z)`

Outcome:
- sealed-box resonance behavior returned to a physically sensible regime
- the corrective checkpoint was frozen on the dedicated debug/fix lineage before being incorporated into the main development path

### Bass-reflex debug result

The later bass-reflex deep-null investigation localized a false SPL cancellation mechanism.

Root cause:
- driver and port could be observed into different radiation spaces in summed SPL

Bounded fix:
- decouple observation `radiation_space` from the radiator mechanical model
- preserve explicit observation-space control for `spl` / `spl_sum`

Outcome:
- the false low-frequency cancellation was removed
- the main development line now contains the corrected observation-space behavior

---

## Reproduction assets

Main script:
- `debug/export_closed_box_compare.py`

Reference data:
- `debug/hornresp_closed_box_all.txt`

Generated outputs remain intentionally ignorable in `debug/`.

These assets are historical diagnostic tools, not the primary release-validation surface.

---

## When to use the debug branches again

Only return to dedicated debug branches if a new bounded discrepancy appears that cannot be responsibly handled on a normal feature/fix branch.

If a new discrepancy appears:

1. branch from the current milestone or other current clean integration line
2. isolate one hypothesis at a time
3. keep the main milestone branch green
4. do not mix unrelated topology growth into the debug thread
5. merge or re-apply only the proven narrow fix

---

## Current caution

Do not treat the existence of these debug branches as evidence that the current milestone is unstable.

They are preserved because they contain useful diagnostic lineage and reproducible artifacts.

Their key findings are already reflected in the current development baseline.
