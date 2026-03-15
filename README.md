# os-lem

Open, scriptable loudspeaker and enclosure simulator with a disciplined, test-first development style inspired by classic Akabak-era LEM workflows.

## Release status

Current release target:
- `v0.1.0` foundation release

This repository now contains a real, tested foundation release candidate.

It supports a narrow but useful coupled loudspeaker/enclosure kernel and is intentionally conservative about broader claims.

## What `v0.1.0` includes

Current validated foundation:

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
- preserved prototype/example frontend artifact in `examples/streamlit_frontend/app2.py`

## Explicit non-claims for `v0.1.0`

`os-lem` `v0.1.0` does **not** claim:

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

The Streamlit example is the maintained example path for the current release target and is intended to use the provisional `os_lem.api` facade.

`examples/streamlit_frontend/app2.py` is preserved as a prototype/example artifact and should not be interpreted as a frozen supported frontend surface.

## Documentation entry points

Start with:
- `docs/start_here.md`
- `docs/current_scope.md`
- `docs/release_strategy.md`
- `docs/release_plan.md`
- `docs/capability_matrix.md`
- `docs/frontend_api.md`

## Development model

This project uses:

- small, bounded patches
- green tests before and after changes
- milestone integration before release
- conservative capability claims

Current integration branch for the first release:
- `milestone/v0.1.0-foundation`

`main` is reserved for released/stable history.
