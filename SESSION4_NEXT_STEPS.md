# Session 4 next steps

## Primary goal
Start implementation without reopening the frozen Session 3 specification.

## Immediate task queue
1. scaffold `src/os_lem/`, `tests/`, and `examples/`
2. write parser/normalizer skeleton
3. add canonical example input files
4. add standalone tests for:
   - driver canonicalization
   - `volume`
   - `duct`
   - radiator formulas
5. implement acoustic matrix assembly for lumped elements first
6. add driver coupling
7. add observations in the same order as validation priority

## Recommended first milestone
A minimal working kernel that can solve and export at least:

- free-air driver input impedance
- closed-box impedance
- one radiator SPL

without yet requiring `waveguide_1d` or `line_profile`.

## Recommended second milestone
Add:

- segmented `waveguide_1d`
- line-profile reconstruction
- vented-box reference case
- `spl_sum`
- group delay

## Recommended third milestone
Make the validation suite pass for the official v1 release-gating set.

## Rule for Session 4
If implementation pain appears, prefer checking the spec and tightening the code to match it.
Do not casually patch around issues by changing the math contract unless an actual contradiction is found.
