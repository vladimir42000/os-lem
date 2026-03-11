# os-lem

Open, scriptable loudspeaker and enclosure simulator inspired by Akabak 2.1 style LEM workflows.

## Current status

This repository already contains the first narrow coupled solver path.

Implemented today:
- parser / normalizer for the frozen v1 subset
- primitive evaluators for:
  - `volume`
  - `duct`
  - `waveguide_1d`
  - `radiator`
- deterministic assembly for the currently supported coupled subset:
  - `volume`
  - `duct`
  - `radiator`
- coupled one-frequency electromechano-acoustic solve
- frequency sweep over the current coupled solve
- first outputs:
  - `input_impedance`
  - `cone_velocity`
  - `cone_displacement`
  - one-radiator far-field pressure
  - one-radiator `spl`

## Current scope boundary

The currently active assembled solver path supports:
- `volume`
- `duct`
- `radiator`

Important limitation:
- `waveguide_1d` exists as a primitive evaluator, but is **not yet assembled**
  into the coupled solver path

Also important:
- the active observation helpers currently live in `src/os_lem/solve.py`
- `src/os_lem/observe.py` is not yet the active public observation path

## Current development phase

Active work has now entered:

**Phase 3 — validation of the current solver path**

This phase is validation-first:
- mandatory internal physics sanity checks
- limited external comparison only for simple cases that truly overlap the
  currently supported solver scope

This is **not yet** a Hornresp-equivalent tool.

## Quick start

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -e ".[dev]"
    pytest -q

## Example files

Examples live under:
- `examples/free_air/model.yaml`
- `examples/closed_box/model.yaml`
- `examples/vented_box/model.yaml`
- `examples/line_basic/model.yaml`
- `examples/conical_line/model.yaml`

## Next planned phase after validation

After Phase 3 validation is complete, Phase 4 is planned to begin with:
- `waveguide_1d` assembly

That is the next real topology expansion step.
