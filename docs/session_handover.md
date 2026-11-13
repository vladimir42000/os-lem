# Session handover

## Authorization and branch

User authorized autonomous coding, testing and development-branch publishing.
First-release scope is a working simulator plus a simple Studio workflow.
Current branch: codex/poc3-kernel-alignment, following checkpoint 47b0b1c.

## Completed bounded patch

Explicit graph-driver mapping preserves Mms and source voltage. Radiation
models are explicit and validated; a fixed POC3 graph retains all segmentation.
The legacy GDN13 driver conversion and historical POC3 diagnostic are unchanged.
See graph_explicit_driver_contract.md for the new contract and limitations.

Validation: 600 passed in 19.21s with Python 3.12, NumPy 2.5.4, SciPy 1.18.1.
Full POC3 grid: 533 points, 10–20000 Hz. Largest differences: impedance
2.5914e-12 ohm, mouth SPL 6.1818e-12 dB, total SPL 1.0311e-10 dB.
Seven new cases cover full-grid output equivalence, voltage scaling and mass
unit conversion, invalid mass/voltage values and unknown radiator models.

## Next action

Follow next_patch.md: bounded Studio workflow integration and real-kernel
failure handling. The final release is not ready and no background job is
running after the session ends.

## User environment

Chromebook kernel tests previously passed; Studio backend: 3 passed; frontend
production build passed. Remaining disk space last reported: 2.4 GB. Shared
Python venv is in sibling os-lem. Node 20.19.2, Python 3.13.5.
Repository writes work through the GitHub connector; no new login is needed.
