# OS-LEM status

## Release objective

Working simulator plus a simple Studio workflow, with autonomous development
and publishing authorized by the user. This branch is not a final release.
Released baseline remains v0.3.0 on main; main is unchanged.

## Current working line

Branch: codex/poc3-kernel-alignment. Previous checkpoint: 47b0b1c.

- Diagnostic radiation fix is retained.
- Explicit graph drivers preserve Mms and voltage directly, with unambiguous
  mass-field validation. Legacy GDN13 driver behavior remains unchanged.
- Explicit graph radiator models are preserved and validated.
- New fixed POC3 graph includes all waveguide segment counts.
- New graph matches the hand-written POC3 model over 533 reference frequencies
  (10–20000 Hz), within numerical tolerances; see graph_explicit_driver_contract.md.
- Full kernel suite: 600 passed, Python 3.12, NumPy 2.5.4, SciPy 1.18.1.
- Historical POC3 construction helper still has its diagnostic-only status.
- Studio installation/build and three backend tests passed on the Chromebook;
  interactive simulation, parameter changes and save/load remain to be verified.

No external accuracy or final-release claim is made. No new flare family or
optimizer work is introduced.
