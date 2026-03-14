# Debug handover

## Branches

Clean branch of record:

- `feature/p5-patch02-minimal-waveguide-assembly`

Debug branch:

- `debug/closed-box-mismatch`

Use the clean branch for normal feature work.
Use the debug branch only for diagnosing the closed-box / loudspeaker kernel mismatch.

## Current status

- clean branch is green
- debug branch is also currently green after reverting a temporary sign experiment
- debug branch contains reusable comparison assets and investigation notes
- closed-box mismatch remains unresolved

## Reproduction assets

Main script:

- `debug/export_closed_box_compare.py`

Reference data:

- `debug/hornresp_closed_box_all.txt`

Generated outputs are intentionally ignored by `debug/.gitignore`.

## How to rerun the main comparison

From repo root:

~~~bash
python debug/export_closed_box_compare.py
~~~

This generates CSV outputs in `debug/` and prints summary comparisons for:

- `ts_classic`
- `em_explicit`
- `em_explicit_large_back`

## What has already been ruled out

The following were explicitly investigated and are not the main remaining cause:

- frontend-only plotting issue
- `ts_classic` normalization as the main remaining source of error
- fully disconnected rear volume
- solving the wrong matrix instead of the coupled system
- simple back-EMF sign flip

## What remains most suspicious

The strongest remaining suspicion is a shared coupling/convention problem in the loudspeaker kernel, likely involving:

- driver ↔ acoustic coupling strength
- pressure/flow convention consistency
- radiator loading convention
- acoustic reaction force seen by the diaphragm

## Important process rules

- do not resume normal feature growth on this branch
- do not mix unrelated waveguide work into this debug thread
- prefer one small diagnostic experiment at a time
- revert rejected experiments after learning from them
- keep the clean branch green and separate

## Recommended next debug step

Suggested next bounded investigation:

- compare the standard front-radiator case with a no-front-radiator diagnostic case
- inspect whether the radiator shunt model is suppressing or mis-scaling the coupling
- continue using raw backend exports, not screenshots only

## Restart order for another AI or future session

Read in this order:

1. `docs/debug_closed_box_checkpoint.md`
2. `docs/debug_handover.md`
3. `docs/status.md`
4. `docs/current_scope.md`
5. `docs/session_handover.md`

Then run:

~~~bash
python debug/export_closed_box_compare.py
~~~

and continue from the documented findings instead of restarting the diagnosis from zero.
