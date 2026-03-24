# os-lem frontend API

## Status

`os_lem.api` is a **provisional integration facade** for UI code, automation
scripts, and validation tools.

It exists to reduce frontend breakage when internal parser / assembly / solver
modules evolve.

It is intentionally narrower than the full kernel surface and should not yet be
marketed as a broad permanently frozen public API for every current and future
capability.

## Supported entry point

```python
from os_lem.api import run_simulation

result = run_simulation(model_dict, frequencies_hz)
```

## What the facade does

- accepts a Python dictionary matching the current model schema
- normalizes and validates that model
- assembles the system
- runs the current frequency sweep
- evaluates common observations into ready-to-plot outputs

## Current ready-to-plot conveniences

The returned `SimulationResult` provides:

- `frequencies_hz`
- `series[observation_id]` for evaluated observations
- `units[observation_id]`
- `warnings`
- `zin_complex_ohm`
- `zin_mag_ohm`
- `cone_velocity_m_per_s`
- `cone_displacement_m`
- `cone_excursion_mm`

## Current observation coverage in the facade

Currently exposed by `os_lem.api`:

- `input_impedance`
- `cone_velocity`
- `cone_displacement`
- `node_pressure`
- `spl`
- `spl_sum`
- `line_profile`
- `group_delay`
- `element_volume_velocity`
- `element_particle_velocity`

For `waveguide_1d` element observables, the current supported facade contract
requires `location: a` or `location: b` so the exported sign and local area are
explicit.

## Strategic caution

The facade is the preferred integration surface for currently validated box
workflows.

However, the project should remain cautious about over-freezing:

- full schema discovery promises
- all future transmission-line / waveguide behavior
- broad parity claims versus external tools

## Examples

The Streamlit example is expected to import the facade instead of calling raw
internal pipeline steps directly.
