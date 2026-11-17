# Tuning workshop acoustic extensions

These additions extend the experimental API; the frozen v1 contract is not redefined.

## Amplifier

Optional driver `series_resistance_ohm` defaults to zero, must be finite and nonnegative, and enters the electrical equation as Re + Rs + jωLe. TS conversion continues to use the driver Re alone. Source voltage is the open-circuit RMS amplifier voltage. Reported input impedance Vs/I includes Rs. This is an ideal voltage source with frequency-independent series resistance, not an amplifier clipping/thermal model.

## Stuffing

Optional waveguide `flow_resistivity` is in Pa·s/m², finite and nonnegative. Zero retains the air-line equations. Positive values apply Miki's rigid-frame equivalent-fluid model throughout that waveguide's cross-section. With exp(+jωt), x=f/σ:

- Zc = (ρc/S)[1 + (0.070 − j0.107)x^-0.632]
- γ = α + (ω/c)[0.160 x^-0.618 + j(1 + 0.109 x^-0.618)]

Source: Yasushi Miki (1990), *Acoustical properties of porous materials—Modifications of Delany-Bazley models*, equations 30–34, https://doi.org/10.1250/ast.11.19 .

The existing `loss` adds uniform attenuation α; do not double-count material loss. The same material law is used for nodal assembly, endpoint flow, and internal pressure/flow profiles. Density is not a universal substitute for flow resistivity. Studio converts its user-calibrated density law into section resistivities. The kernel warns about unvalidated extrapolation outside 0.01 ≤ f/σ ≤ 1. This is not a wall-lining model and does not include moving fibres, porous-frame resonances or thermal/nonlinear power effects.

## Acoustic group delay

A `group_delay` observation can now target `spl` or `spl_sum`: the derivative uses their complex pressure, never the angle of dB magnitudes. Other targets must be complex. Units remain seconds; Studio converts to milliseconds. Acoustic free-space flight time is excluded, matching the existing radiator observation contract. Deep cancellation nulls can make delay ill-conditioned; derivative sampling and phase unwrapping limit interpretation there.

## Performance and checks

Waveguide segment assembly is vectorized; internal chain elimination uses pivoted SciPy banded LU instead of dense LU. Segment count and frequency grid are unchanged. One local 600-frequency uniform TL sweep went from 0.479 s to 0.162 s (about 3×); maximum SPL difference was 7.35e-10 dB. This is a local observation, not a guaranteed Chromebook speedup.

`tests/test_workshop_physics.py` checks analytic uniform porous two-ports, dense/banded equivalence, Miki SI coefficients/passivity, amplifier resistance without TS alteration, acoustic delay/distance convention, zero-resistivity compatibility and invalid resistivities. External Hornresp/Akabak validation is outstanding.
