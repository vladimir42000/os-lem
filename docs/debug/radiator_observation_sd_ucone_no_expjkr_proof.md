# Proof checkpoint — radiator observation via `Sd * u_cone` without explicit `exp(-jkr)`

Status: proof branch only. This is **not** a release claim, **not** a merge instruction, and **not** an accepted fix.

## Purpose

Freeze one bounded proof patch that tests the remaining untested observation-path combination on top of the current candidate branch:

`p_obs = j·ω·ρ₀ / (Ω·r) · Sd · u_cone`

with the explicit propagation factor `exp(-jkr)` still omitted from the exported observation transfer.

## What this proof changes

- Keeps the current no-`exp(-jkr)` observation-transfer helper unchanged.
- Changes solver-side observation reconstruction from `node_pressure / z_rad` to `Sd * u_cone`.
- Updates only the directly affected tests.

## Why this proof exists

The current candidate branch improved the AkAbak front-only pressure-phase mismatch substantially by removing the explicit propagation term, but it still reconstructs radiator observation from `node_pressure / z_rad`.

This proof checks whether the remaining choice of observation source matters once the propagation convention has already been switched.

## Acceptance rule

Compare only against the same AkAbak front-only gate used for the candidate branch.
