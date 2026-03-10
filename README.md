# os-lem

Open, scriptable loudspeaker and enclosure simulator inspired by Akabak 2.1 style LEM workflows.

## Session 4 status
This repository now includes the first implementation scaffold:

- modular Python package layout under `src/os_lem/`
- strict parser / normalizer for the frozen v1 input subset
- canonical driver normalization (`ts_classic` and `em_explicit`)
- primitive evaluators for:
  - `volume`
  - `duct`
  - `waveguide_1d` uniform-segment helper formulas
  - `radiator`
- canonical example YAML files
- primitive pytest coverage

## Current limitation
The full coupled acoustic-electromechanical solve is **not yet implemented** in this scaffold.
The current milestone is parser correctness plus primitive formula correctness.

## Quick start
Create a virtual environment and install:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
