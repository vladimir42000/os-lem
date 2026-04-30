# v0.9.0 GDN13 graph-defined parity checkpoint note

Patch name: `docs/v0.9.0-gdn13-graph-defined-parity-checkpoint-note`  
Branch: `proof/poc3-blh-benchmark-pass1`  
Base commit: `06be5b2` — Add GDN13 graph-defined low-frequency HornResp parity smoke

This checkpoint freezes the accepted meaning of the first graph-defined GDN13 low-frequency HornResp parity chain. It is a documentation checkpoint only. It records the accepted graph-defined parity semantics and the limits of the current result before any further graph IR expansion is considered.

## 1. Checkpoint identity

The accepted v0.9.0 graph chain has now crossed these bounded steps:

1. graph IR specification
2. graph validator skeleton
3. graph compiler skeleton
4. graph-to-handmapped construction equivalence
5. graph-vs-handmapped solver-output equivalence
6. graph-defined low-frequency HornResp parity

The accepted graph-defined GDN13 path is:

```text
GDN13 acoustic graph IR
→ os_lem.acoustic_graph_ir.validate_acoustic_graph_ir(graph)
→ os_lem.acoustic_graph_ir.compile_acoustic_graph_ir_to_model_dict(graph)
→ os_lem.api.run_simulation(model_dict, frequencies_hz)
→ bounded low-frequency HornResp comparison
```

The accepted callable names are:

- `validate_acoustic_graph_ir`
- `compile_acoustic_graph_ir_to_model_dict`
- `os_lem.api.run_simulation`

This checkpoint does not add implementation and does not alter the accepted graph path.

## 2. What is now accepted

The v0.9.0 acoustic graph IR path has now demonstrated, for one accepted anchor case, the full bounded chain from graph validation through graph compilation, solver execution, and low-frequency HornResp comparison.

The accepted anchor is the **GDN13 graph-defined offset-driver TQWT** case. In this case, the graph-defined construction preserves the previously accepted hand-mapped GDN13 interpretation closely enough to reproduce the accepted low-frequency HornResp parity gate.

This is an important model-construction checkpoint because the graph path is no longer only a structural representation. For this one case, the graph-defined route can reach the existing solver and preserve the already accepted low-frequency GDN13 parity semantics.

## 3. Accepted GDN13 topology meaning

The accepted GDN13 graph-defined interpretation is:

- driver/source tap at `S2`
- rear closed stub from `S1` to `S2`
- forward/open line from `S2` to `S3`
- parabolic profile for the accepted rear and forward acoustic line sections
- `2pi` mouth radiation at `S3`
- accepted GDN13 driver parameters from the current fixture:
  - `Sd = 82.00 cm2`
  - `Bl = 6.16 Tm`
  - `Cms = 1.01e-03 m/N`
  - `Rms = 0.49`
  - `Mmd = 8.50 g`
  - `Le = 1.00 mH`
  - `Re = 6.50 ohm`

The accepted section reading remains:

- rear closed stub: `S1 = 96.00 cm2` to `S2 = 98.06 cm2`, length `55.80 cm`
- forward/open line: `S2 = 98.06 cm2` to `S3 = 102.00 cm2`, length `106.46 cm`
- mouth radiation area: `102.00 cm2`
- radiation convention: `2pi`

This note does not replace the accepted hand-mapped GDN13 path by default. It records that the graph-defined path has now reproduced the accepted bounded low-frequency parity meaning for this one anchor case.

## 4. Accepted parity convention

The accepted graph-defined parity convention is:

- case: `GDN13 offset-driver TQWT`
- parity band: `frequency_hz <= 600.0`
- SPL reference: HornResp SPL column from the accepted GDN13 fixture
- SPL observable: os-lem `spl_total_diagnostic`
- impedance reference: HornResp `Ze` column from the accepted GDN13 fixture
- impedance observable: `abs(zin_complex_ohm)`
- mouth-only SPL is rejected as the HornResp SPL comparator for this case

The statement **mouth-only SPL is rejected** is part of the accepted convention. Mouth-only SPL may remain useful as diagnostic context, but it is not the accepted SPL comparator for the HornResp SPL column in this GDN13 offset-driver TQWT case.

## 5. Accepted low-frequency metrics

The accepted low-frequency SPL metrics for the graph-defined GDN13 path are:

- low-frequency SPL MAE: about `0.442 dB`
- low-frequency SPL RMS: about `0.985 dB`
- low-frequency SPL maximum absolute error: about `6.630 dB`
- low-frequency SPL parity passed: `true`

The accepted low-frequency impedance metrics for the graph-defined GDN13 path are:

- low-frequency impedance MAE: about `0.383 ohm`
- low-frequency impedance RMS: about `1.151 ohm`
- low-frequency impedance maximum absolute error: about `7.453 ohm`
- low-frequency impedance parity passed: `true`

These metrics are bounded to the accepted low-frequency parity band only. They must not be read as full-band parity.

## 6. Remaining full-band SPL limitation

Full-band SPL parity is not established.

The full-band SPL residual remains visible and non-trivial:

- full-band SPL MAE: about `4.532 dB`
- full-band SPL RMS: about `8.341 dB`
- full-band SPL maximum absolute error: about `37.137 dB`

These residuals remain part of the accepted limitation surface. They must not be hidden by the low-frequency pass result.

## 7. Explicit non-claims

This checkpoint does not establish:

- full-band SPL parity
- general HornResp parity
- full Akabak/HornResp replacement
- arbitrary graph engine maturity
- Studio consumption
- optimizer graph consumption
- Akabak parser support
- HornResp importer support
- topology optimization
- solver-core rewrite
- replacement of the accepted hand-mapped GDN13 path by default
- uncontrolled graph primitive expansion
- a new topology anchor beyond the accepted GDN13 offset-driver TQWT case

There is no Akabak/HornResp replacement claim in this checkpoint.

## 8. Scope guardrail for next work

This note freezes the accepted v0.9.0 graph-defined GDN13 low-frequency HornResp parity meaning before further graph IR expansion.

Any next graph expansion requires a separate Director gate. This note does not open the next implementation step by implication. It does not authorize broader graph primitive growth, general HornResp import, optimizer graph consumption, Studio graph emission, or replacement of the hand-mapped GDN13 reference path.

