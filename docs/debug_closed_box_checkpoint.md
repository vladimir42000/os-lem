# Closed-box debug checkpoint

## Purpose

This document freezes the current closed-box mismatch investigation state on branch:

- `debug/closed-box-mismatch`

The clean development branch of record remains:

- `feature/p5-patch02-minimal-waveguide-assembly`

This branch exists to preserve diagnostic artifacts, findings, and restart instructions without contaminating the clean feature branch.

## Why this debug branch exists

A side prototype (`examples/streamlit_frontend/`) exposed a serious physical mismatch in a canonical sealed-box loudspeaker case:

- SPL and excursion looked qualitatively plausible at first glance
- but input impedance stayed almost flat near `Re`
- Hornresp for the same case showed the expected strong sealed-box impedance peak

This indicated a core physics/coupling problem rather than a frontend-only plotting problem.

## Closed-box reference case

Reference parameters used for comparison:

- `Re = 5.80 ohm`
- `Le = 0.35 mH`
- `Fs = 34.00 Hz`
- `Qes = 0.42`
- `Qms = 4.10`
- `Vas = 55.00 l`
- `Sd = 132.00 cm2`
- `Vb = 18.00 l`

Reference YAML used in os-lem:

~~~yaml
meta:
  name: closed_box_demo
driver:
  id: drv1
  model: ts_classic
  Re: 5.8 ohm
  Le: 0.35 mH
  Fs: 34.0 Hz
  Qes: 0.42
  Qms: 4.1
  Vas: 55.0 l
  Sd: 132.0 cm2
  node_front: front
  node_rear: rear
elements:
- id: front_rad
  type: radiator
  node: front
  model: infinite_baffle_piston
  area: 132.0 cm2
- id: box
  type: volume
  node: rear
  value: 18.0 l
observations:
- id: zin
  type: input_impedance
  target: drv1
- id: spl
  type: spl
  target: front_rad
  distance: 1 m
- id: xcone
  type: cone_displacement
  target: drv1
~~~

## Hornresp reference behavior

Hornresp export preserved in:

- `debug/hornresp_closed_box_all.txt`

Observed reference behavior:

- strong impedance peak near about `68 Hz`
- peak magnitude around `60 ohm`
- displacement and SPL consistent with a normal sealed-box resonance

## Confirmed bug already found and fixed

A real bug was found in `ts_classic` canonicalization in `src/os_lem/driver.py`.

Previous incorrect relation:

- `Bl = sqrt(Re * Rms / Qes)`

Correct relation:

- `Bl = sqrt(w_s * Mms * Re / Qes)`

This bug was real and should remain part of future clean fixes if not already preserved elsewhere.

However, correcting `Bl` did **not** solve the main closed-box mismatch.

## What was tested

### 1. Raw backend export

A standalone backend debug script was created:

- `debug/export_closed_box_compare.py`

This bypasses Streamlit plotting and exports raw os-lem results for comparison with Hornresp.

### 2. `ts_classic` vs `em_explicit`

The same closed-box case was run with:

- `ts_classic`
- `em_explicit` using Hornresp-equivalent EM values

Result:

- both os-lem variants produced nearly identical wrong results

Conclusion:

- the remaining mismatch is **not mainly in `ts_classic` normalization**

### 3. Small rear volume vs very large rear volume

A comparison was made between:

- `18 L` rear volume
- `1000 m^3` rear volume as a near-free-rear diagnostic reference

Result:

- the rear volume does affect the solution
- but the effect is far too weak

Conclusion:

- the rear cavity is not fully disconnected
- but its feedback into the driver/electrical response is much too weak

### 4. Back-EMF sign experiment

A temporary local experiment flipped the electrical coupling sign in `src/os_lem/solve.py`.

Result:

- no meaningful improvement
- experiment reverted
- current branch is back to green tests

Conclusion:

- back-EMF sign is not the dominant remaining defect

## Main confirmed conclusions so far

The remaining mismatch is:

- not a frontend-only issue
- not mainly a `ts_classic` normalization issue
- not simply a disconnected rear box
- not caused by solving the wrong matrix
- not fixed by a simple back-EMF sign flip

Current leading diagnosis:

- the shared electromechanical-acoustic coupling is present but far too weak
- the most likely remaining defect class is a pressure/flow/coupling magnitude or convention problem
- likely around the shared driver-acoustic interaction or radiator/acoustic loading convention

## Current working hypothesis

Highest-priority suspects for next debugging session:

1. shared driver/acoustic coupling magnitude or convention
2. radiator pressure/volume-velocity loading convention
3. acoustic load reflection into the diaphragm force balance

## Files most relevant for future debugging

- `src/os_lem/driver.py`
- `src/os_lem/solve.py`
- `src/os_lem/elements/volume.py`
- `src/os_lem/elements/radiator.py`
- `debug/export_closed_box_compare.py`
- `debug/hornresp_closed_box_all.txt`

## Branch state

This debug branch should preserve:

- debug artifacts
- comparison script
- Hornresp reference export
- debug documentation and handover notes

It should **not** be treated as the normal feature-development branch.
