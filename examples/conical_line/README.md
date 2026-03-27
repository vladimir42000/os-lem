# Conical line example

This is the maintained v0.4.0 waveguide example.

It is intentionally narrow:
- one lossy conical `waveguide_1d`
- preserved endpoint observables (`element_volume_velocity`, `element_particle_velocity`)
- preserved internal observability through `line_profile` for `pressure`, `volume_velocity`, and `particle_velocity`
- summed SPL from the direct radiator and line mouth

What this example is for:
- smoke-checking the bounded lossy conical workflow
- demonstrating the current YAML surface for a practical TL / horn-style line
- giving one stable example that can be loaded through `os_lem.api.run_simulation`

What it does **not** claim:
- broad horn parity
- tapped-horn or branched-waveguide support
- broad AkAbak or Hornresp equivalence
- product-grade frontend maturity
