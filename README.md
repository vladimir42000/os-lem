# os-lem

Open, scriptable loudspeaker and enclosure simulator with a disciplined, test-first development style inspired by classic Akabak-era LEM workflows.

## Release posture

Latest released version:
- `v0.1.0` on `main`

Current active planning target:
- `v0.2.0` — offset-line observation-contract stabilization

Current green suite on the uploaded working line:
- `108 passed`

This repository already contains a real released foundation. Current work is focused on turning the long observation/debug cycle into one bounded, documented next milestone rather than opening broad new feature scope.

## What `v0.1.0` includes

Released foundation:

- one-driver coupled electro-mechano-acoustic solve
- frequency sweep
- assembled elements:
  - `volume`
  - `duct`
  - `radiator`
  - minimal `waveguide_1d`
- classical outputs:
  - input impedance
  - cone velocity
  - cone displacement
  - one-radiator far-field pressure
  - one-radiator SPL
- current minimal waveguide observability subset:
  - endpoint flow export
  - endpoint particle-velocity export
  - minimal `line_profile` export for `pressure`
  - minimal `line_profile` export for `volume_velocity`
  - minimal `line_profile` export for `particle_velocity`
- cylindrical distributed loss for `waveguide_1d` within the currently frozen cylindrical-loss boundary
- provisional `os_lem.api` integration facade
- maintained Streamlit example path in `examples/streamlit_frontend/app.py`

## Current `v0.2.0` planning intent

The current repo truth from the extended debug line is:

- `front/raw` is broadly credible
- the remaining mismatch is localized to `mouth/port` observable semantics
- the next supported move is one bounded observation-layer patch
- the preferred first candidate is `mouth_directivity_only`
- `front` semantics must remain unchanged during that patch

This is not yet a released claim. It is the current development hypothesis that defines the next bounded technical patch.

## Explicit non-claims for the current project state

`os-lem` still does **not** claim:

- broad Hornresp parity
- broad AkAbak parity
- mature transmission-line support
- broad horn / line workflow coverage
- conical lossy `waveguide_1d`
- thermo-viscous auto-derived losses
- stable long-term public API
- product-grade GUI/frontend
- multi-driver support
- passive radiator support
- crossover-network maturity

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Example files

Examples live under:
- `examples/closed_box/model.yaml`
- `examples/vented_box/model.yaml`
- `examples/streamlit_frontend/app.py`

The Streamlit example is the maintained example path for the current released baseline and uses the provisional `os_lem.api` facade.

## Documentation entry points

Start with:
- `docs/doc_index.md`
- `docs/start_here.md`
- `docs/current_scope.md`
- `docs/milestone_charter.md`
- `docs/release_strategy.md`
- `docs/release_plan.md`
- `docs/capability_matrix.md`
- `docs/book_contract.md`

## Development model

This project uses:

- small, bounded patches
- green tests before and after changes
- milestone integration before release
- conservative capability claims
- repo docs as long-term project memory
- the parallel book as explanatory companion, not repo truth

Recommended next governance branch:
- `chore/v0.2.0-docs-reset`

Recommended next technical patch after this docs reset:
- `fix/v0.2.0-mouth-directivity-only`
