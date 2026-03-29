# Frontend handoff v1

This handoff is the minimal package an external frontend developer should read first.
It is intentionally independent of milestone-control documents.

## What to call

Use:

- `from os_lem.api import run_simulation, get_frontend_contract_v1`

Frontend code should:

1. read `get_frontend_contract_v1()` at startup or in CI to verify expected stable features
2. build models only from the stable subset documented in `docs/input_format.md`
3. use only the stable examples in `examples/frontend_contract_v1/` as contract references

## Stable examples

The canonical stable example bundle is:

- `examples/frontend_contract_v1/closed_box_minimal.yaml`
- `examples/frontend_contract_v1/conical_line_minimal.yaml`
- `examples/frontend_contract_v1/README.md`

These examples are the baseline integration targets for external frontend work.

## Stable vs experimental

Stable for frontend v1:

- the `run_simulation()` facade itself
- the manifest from `get_frontend_contract_v1()`
- the stable input subset and stable result surface documented in `docs/frontend_api.md`
- the two canonical example workflows

Experimental and not frozen for frontend v1:

- branching / recombination / split-merge topology openings
- any other newly landed v0.5.0 kernel topology work that is not promoted in the contract manifest

## Required update rule for future kernel patches

If a future patch changes:

- supported element types
- observation types
- result surface
- example-worthy workflows
- parser fields used by the facade

then that patch must do exactly one of these:

1. update the frontend contract manifest, frontend docs, and frontend tests
2. explicitly declare: `No frontend contract change`

## Minimal frontend integration pattern

1. call `get_frontend_contract_v1()`
2. choose a stable example as a reference fixture
3. call `run_simulation(model_dict, frequencies_hz)`
4. read `result.series`, `result.units`, `result.observation_types`, and the stable convenience properties
5. treat any topology not listed as stable as experimental
