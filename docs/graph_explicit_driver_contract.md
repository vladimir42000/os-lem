# Explicit graph driver and POC3 alignment

The graph compiler accepts `model: em_explicit` on an electrodynamic_driver.
Its parameters require exactly one of `Mms_kg` or `Mms_g`, representing the
moving mass expected by the existing solver. It does not infer Mms from Mmd or
add/subtract radiation mass. Mmd fields are rejected on this path.

The remaining parameters are Sd_cm2/Sd_m2, Bl_Tm, Cms_m_per_N,
Rms_Ns_per_m/Rms, Re_ohm, Le_mH/Le_H. Optional positive numeric
source_voltage_rms defaults to 2.83 V. Explicit parameters pass directly to
the existing em_explicit solver driver, avoiding a T/S conversion round trip.

Omitting model, or choosing ts_classic, retains the historical Mmd-based graph
conversion and its air constants for compatibility with GDN13. Mms fields are
rejected there. This is a legacy conversion convention, not a general assertion
that dry moving mass and loaded moving mass are interchangeable. An explicit
source_voltage_rms is now preserved on that path too.

A radiation_load may specify model: infinite_baffle_piston or unflanged_piston.
The historical default is unflanged_piston. Unknown models fail validation.
Waveguide segments already survive compilation when present in graph input.
The old POC3 construction helper omitted them; the new fixed fixture includes
4, 36 and 12 segments, and explicit radiator models from the hand-written model.

## Reproducible internal comparison

Fixture: proof/poc3_blh_benchmark_pass1/graph_explicit.json.
Authority: proof/poc3_blh_benchmark_pass1/model.yaml.
Test: tests/graph/test_poc3_explicit_graph_alignment.py.

The fixture passes through the public compiler and simulation API. Native
impedance, mouth SPL and summed SPL are compared without changing the emitted
model. An additional run requests the same observations as the authority to
compare front SPL and cone displacement. The full reference grid has 533
points from 10 to 20000 Hz.

Impedance uses rtol=1e-9, atol=1e-10 ohm; native SPL uses an absolute 1e-8 dB
tolerance. These allow floating-point roundoff and unit conversion, not physical
model disagreement. The additional series comparison uses rtol=1e-9,
atol=1e-10. Observed maxima in the validated environment: 2.60e-12 ohm,
6.19e-12 dB mouth SPL, 1.04e-10 dB summed SPL (rounded upward).
Doubling input voltage preserves impedance and adds 20*log10(2) dB to mouth SPL.

The existing legacy-helper diagnostic remains intentionally unchanged. Its
historical non-equivalence result does not describe the new explicit fixture.
No chamber is invented: POC3's throat chamber remains a waveguide. Separate
existing chamber compiler/mapping tests remain part of the full suite.

This establishes internal equivalence for one fixture only, not measured
accuracy, Hornresp/Akabak parity, or general graph-topology support.
