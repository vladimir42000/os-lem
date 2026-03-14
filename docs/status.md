# os-lem status

## Current development status

- Active branch: `feature/p5-patch02-minimal-waveguide-assembly`
- Current known good commit before this patch: `7b1a47b`
- Current known local test status after this patch: `pending local verification after ts_classic Bl normalization fix`
- Current phase state: **Phase 5 active**
- Previous phase checkpoint: **Phase 4 closed at corrective checkpoint**

## Current validated implemented subset

The currently assembled and validated subset is:

- `volume`
- `duct`
- `radiator`
- minimal assembled `waveguide_1d`

`waveguide_1d` is now assembled as a reduced two-port branch contribution in the
current solver path.

## What Phase 4 delivered

Session 4 closed with a narrow corrective checkpoint:

- diagnostic investigation isolated a real solver sign-convention bug
- driver front / rear acoustic coupling signs were corrected in `src/os_lem/solve.py`
- frozen numerical reference outputs were refreshed to the corrected solver
- Phase 3 validation tests were updated so they remain meaningful under the corrected solver baseline
- a real vented-box comparison artifact improved confidence in the corrected behavior
- no topology expansion was performed during Phase 4

## What Phase 5 has delivered so far

The first bounded Phase 5 implementation patch is complete:

- `waveguide_1d` now assembles as a branch element
- the acoustic matrix now accepts `waveguide_1d` as a reduced two-port branch stamp
- a minimal coupled solve with `waveguide_1d` is covered by focused tests

The next bounded Phase 5 validation follow-up is also complete:

- internal validation for assembled `waveguide_1d` was strengthened
- constant-area waveguide behavior is covered by a segmentation-invariance sanity test
- conical waveguide behavior is covered by a segmentation-refinement sanity test

The bounded Phase 5 waveguide observability follow-ups now complete are:

- waveguide endpoint flow export
- waveguide endpoint particle-velocity export
- minimal `waveguide_1d` `line_profile` export for `pressure`
- minimal `waveguide_1d` `line_profile` export for `volume_velocity`
- minimal `waveguide_1d` `line_profile` export for `particle_velocity`

The first bounded cylindrical-loss implementation follow-up is now complete:

- user-specified distributed loss is supported for cylindrical `waveguide_1d` only
- lossless behavior is preserved when `loss` is absent or zero
- lossy cylindrical profile reconstruction works for `pressure`, `volume_velocity`, and `particle_velocity`

The full repository suite was green at `90 passed` before this debug checkpoint; local post-fix verification must refresh that number.

A bounded post-Phase-5 debug correction is now required before further feature planning:

- `ts_classic` driver canonicalization had an incorrect `Bl` derivation
- the bug suppressed the motional contribution in canonical sealed-box input impedance
- the fix is a solver-correctness checkpoint, not frontend work
- focused regression coverage is required for canonical normalization; sealed-box impedance behavior remains under active debug after this fix

## Current project interpretation

The corrected solver baseline from Phase 4 remains the accepted development baseline.

This does **not** freeze a claim of universal Hornresp parity. It freezes a narrower conclusion:

- Session 4 successfully identified and corrected one real implementation bug
- Phase 5 has resumed bounded topology expansion on top of that corrected baseline
- the first assembled `waveguide_1d` path now has focused internal validation support
- bounded first waveguide observability is now real in the repo
- cross-profile internal validation is now stronger for the current waveguide profile outputs
- the first minimal cylindrical distributed-loss extension is now real in the repo
- future work should proceed from the corrected solver and current green test suite

## Immediate next objective

Complete the bounded `ts_classic` motor-normalization correction and re-freeze repo truth before selecting any new Phase 5 feature patch.

Recommended next step:
1. correct `ts_classic` canonical `Bl` derivation
2. land focused regression tests for canonical normalization
3. rerun the full repository suite
4. continue the separate sealed-box / bass-reflex impedance debug track because the `Bl` correction alone does not fully restore the expected impedance hump
5. only then reconstruct the next single bounded Phase 5 planning step

Still deferred:
- conical lossy `waveguide_1d`
- thermo-viscous auto-derived losses
- broad external parity claims

## Explicitly out of scope right now

- broad refactor
- multi-driver expansion
- forcing broad external parity claims
- unsupported horn / line validation claims
