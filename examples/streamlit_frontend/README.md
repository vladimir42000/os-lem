# Streamlit frontend examples

This directory contains Streamlit-based example applications for `os-lem`.

## Current intended roles

### `app.py`
This is the current maintained example path for the `v0.1.0` milestone.

It is the preferred example because it uses the provisional `os_lem.api` facade instead of importing the low-level parser / assembly / solve pipeline directly.

### `app2.py`
This file is preserved from exploratory validation work.

It is kept because it may still be useful for:
- validation workflows
- UI exploration
- local experimentation
- comparison against earlier frontend ideas

However, it must be interpreted cautiously:

- it is a preserved prototype, not a frozen supported UI surface
- it may depend more directly on low-level internals than `app.py`
- it must not be used to broaden public claims about API stability or product maturity

## Release posture

For the `v0.1.0` foundation release:

- `app.py` is the maintained example path
- `app2.py` is preserved as a prototype/example artifact
- neither file implies a product-grade GUI claim

## Development caution

Do not mix broad frontend redesign with kernel work in one patch.

If `app2.py` is ever modernized to use `os_lem.api` consistently, that should happen in its own bounded follow-up patch.
