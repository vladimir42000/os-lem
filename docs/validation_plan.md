# Validation plan

## Purpose
This document defines how `os-lem` v1 will be checked before and during the first implementation.

The goal is to make sure the frozen v1 contract is implemented consistently, transparently, and with enough rigor that the first public solver is trustworthy for its declared scope.

---

## 1. Validation philosophy

Validation is split into five layers:

1. schema and normalization validation
2. primitive-physics validation
3. integrated reference-model validation
4. observation validation
5. numerical robustness validation

This order is intentional.

---

## 2. Frozen tolerance policy for validation comparisons

Unless a test case explicitly states otherwise, complex-valued validation comparisons use:

\[
|z_{test} - z_{ref}| \le \max(\tau_{abs}, \tau_{rel}|z_{ref}|)
\]

with frozen default validation tolerances:

- \(\tau_{rel} = 1 \times 10^{-6}\)
- \(\tau_{abs} = 1 \times 10^{-12}\)

This rule applies to complex quantities directly, not to separately compared magnitude and phase, unless a specific test says otherwise.

---

## 3. Acceptance principles

A feature is not considered validated merely because a plot “looks right”.

Each validation case should define:

- what is being tested
- the expected qualitative behavior
- the expected quantitative result or tolerance
- what type of failure it should detect

When an exact closed-form value is not practical, the validation target may be one of:

- agreement with a frozen formula in the spec
- agreement with a hand-derived reference computation
- agreement with a trusted external simulator for a case within shared scope
- convergence under internal refinement

---

## 4. Layer A - Parser and normalization validation

### A1. Required-field enforcement
Missing required fields are hard errors.

### A2. Unknown-field rejection
Unknown fields are hard errors.

### A3. Unit normalization
Equivalent models written in accepted engineering units must normalize to identical SI internal values.

This test should be implemented explicitly by constructing equivalent inputs in multiple accepted units and comparing the normalized internal values, not just the final plotted outputs.

### A4. Driver canonicalization
Equivalent `ts_classic` and `em_explicit` inputs must produce the same canonical internal driver within the frozen tolerance rule.

### A5. Mixed classical-plus-explicit consistency behavior

- consistent values: accepted with warning
- inconsistent values: rejected

### A6. Topology sanity checks
Reject at least:

- duplicate ids
- missing observation targets
- disconnected floating acoustic subnetworks
- acoustically connected components lacking a valid shunt path to reference
- `driver.node_front == driver.node_rear` in the same acoustic node
- negative or zero physical parameters where the schema forbids them

### A7. Parallel-path legality
Multiple branches connecting the same node pair are valid and must be preserved as parallel elements during normalization and assembly.

This test exists to make parallel-path support explicit and non-accidental.

---

## 5. Layer B - Primitive physics validation

### B1. `volume` compliance branch
Verify:

\[
Y_a = j\omega C_a
\]

Failure modes caught:

- wrong \(j\omega\) sign
- wrong normalization by \(\rho_0 c_0^2\)
- unit mistakes in liters or m³

### B2. `duct` inertance branch
Verify:

\[
Q = \frac{p_a - p_b}{j\omega M_a}
\quad \text{with} \quad
M_a = \rho_0 L/S
\]

Failure modes caught:

- wrong sign
- wrong area dependence
- wrong node ordering

### B3. Parallel-duct equivalence
Create one case with two identical ducts in parallel between the same nodes.

The reference comparison is a single equivalent duct with half the inertance:

\[
M_{eq} = \frac{M_a}{2}
\]

This test exists specifically to catch wrong parallel assembly behavior.

### B4. Uniform line subsegment formula
For one uniform cylindrical segment, verify transfer-matrix and equivalent nodal-admittance forms agree numerically.

Failure modes caught:

- algebra mistakes in conversion
- wrong characteristic impedance convention
- wrong \(\cot\) or \(\csc\) sign

### B5. `waveguide_1d` cylindrical degeneration test
A conical guide with equal endpoint areas must match the cylindrical special case behavior.

### B6. Segmentation refinement test for `waveguide_1d`
For at least one official conical line case, refine the segment count, for example:

- 4
- 8
- 16
- 32
- 64

and require convergence of:

- endpoint pressure/flow relation
- line-profile shape
- selected observation peaks

Frozen v1 convergence metric for the official reference case:

- compare 32 versus 64 segments
- require input-impedance magnitude difference below 2% across the official validation band
- require main resonance or notch frequencies to shift by less than 1%
- require line-profile pressure-magnitude difference below 5% at the official sampled points, excluding points whose reference magnitude is below \(10^{-9}\) in SI pressure units

This is a release blocker.

### B6a. Minimal cylindrical lossy line checkpoint
For the supported cylindrical lossy `waveguide_1d` case, verify:

- `loss = 0` reproduces the current lossless cylindrical behavior
- the reduced two-port admittance matches the exact cylindrical lossy reference
- pressure, volume-velocity, and particle-velocity profiles match the exact cylindrical lossy reference
- increasing loss reduces transmitted pressure magnitude for an otherwise fixed case

This checkpoint is only for the currently frozen cylindrical lossy boundary. It must not be presented as broad lossy horn or transmission-line parity.

### B7. Radiator boundary impedance formula tests
For each radiator model, compare the implemented boundary impedance against the frozen formulas in `docs/radiator_models.md` at a small set of dimensionless sample points.

Minimum required sample strategy:

- low \(ka\)
- mid-band \(ka\)
- upper validated-band \(ka\)

At minimum test points should include representative values such as:

- \(ka = 0.05\)
- \(ka = 0.2\)
- \(ka = 0.5\)
- \(ka = 1.0\)
- \(ka = 2.0\) for the pipe-end Padé models

The implementation must match the frozen formula evaluator within numerical tolerance.

### B8. Radiator low-frequency inertive and passivity behavior
Independently of the formula-match test, verify that:

- the imaginary part of the radiator impedance is positive and mass-like at low frequency
- the small-\(ka\) reactance slope matches the frozen end-correction constant for the flanged and unflanged pipe-end models
- \(\Re\{Z_{rad}\} \ge 0\) within numerical tolerance at all tested sample points

This catches sign errors even if a copied formula is accidentally conjugated or otherwise misinterpreted.

---

## 6. Layer C - Integrated reference models

### C1. Free-air driver
Model the driver with front and rear radiators and no enclosure loading.

Expected behavior:

- one main impedance resonance near \(f_s\)
- cone velocity rises toward resonance and falls away from it according to the electromechanical model

This case validates the core electromechanical coupling before box loading is added.

### C2. Symmetric front/rear radiation sign test
Create a symmetric front/rear setup and verify that the driver contributes equal-magnitude opposite-sign acoustic injections at the two attached nodes.

The reference expectation is that front and rear acoustic responses follow the frozen driver sign convention and do not collapse into an in-phase same-side result.

This test exists specifically to catch front/rear sign mistakes.

### C3. Closed box
Expected behavior:

- system resonance shifts above free-air resonance
- impedance shows the expected sealed-box peak shape
- cone excursion is reduced below system resonance compared with free air

### C4. Vented box
Expected behavior:

- double impedance peak
- minimum between peaks near box tuning
- vent velocity dominates near tuning
- cone excursion is reduced near tuning

### C5. `spl_sum` cancellation case
Create an official case where two radiator contributions partially cancel at some frequency.

This can be a vented-box example near tuning or another topology with controlled phase opposition.

This test exists specifically to expose any wrong dB-domain summation.

### C6. Straight line / TQWP-style case
Expected behavior:

- standing-wave structure appears in `line_profile`
- changing line length shifts modal structure in the expected direction

### C7. Conical line comparison case
For a moderate conical flare, require:

- smooth response change when flare ratio changes
- convergence under segmentation refinement
- no unphysical discontinuous artifacts caused by implementation errors

### C8. Chained waveguide continuity case
Use at least two connected `waveguide_1d` elements with different flare rates joined at one acoustic node.

Require at the junction:

- pressure continuity through the shared node
- volume-velocity conservation through the assembled node balance

This test exists to catch assembly mistakes in connected distributed elements.

### C9. Side-branch topology built from primitives
Use a main line plus a branch built from core elements.

Expected behavior:

- a notch or suppression feature appears in the expected band
- branch placement and tuning shift the feature in the expected direction

---

## 7. Layer D - Observation validation

### D1. `input_impedance`
Verify exported impedance equals \(V/I\).

### D2. `cone_velocity` and `cone_displacement`
Verify:

\[
X = U/(j\omega)
\]

### D3. `element_volume_velocity`
Verify the exported value matches the actual solved branch or local endpoint flow with the frozen reporting sign convention.

Required subcases:

- one `duct`
- one `radiator`
- one `waveguide_1d` with `location: a`
- one `waveguide_1d` with `location: b`

### D4. Node-order reversal invariance
For a `duct` and for a `waveguide_1d`, create two equivalent models with swapped endpoint labels.

Require:

- physical predictions such as `input_impedance`, `spl`, and `spl_sum` remain unchanged
- the reported signed element flow changes exactly according to the frozen reporting convention
- the `line_profile` x-axis reverses consistently without changing the underlying physics

### D5. `element_particle_velocity`
Verify:

\[
v = Q/S
\]

using the frozen local area rule for each supported target type.

### D6. `node_pressure`
Verify the exported value equals the solved node pressure in the state vector.

### D7. `spl`
Verify that exported SPL is the dB conversion of the same complex observation pressure computed from the frozen radiator observation transfer.

### D8. `spl_sum`
Verify that:

\[
p_{sum} = p_1 + p_2 + \cdots
\]

before dB conversion.

Include at least one partial-cancellation case.

### D9. `group_delay`
Verify the exported group delay matches an independently recomputed result using the frozen unwrapping rule and frozen discrete stencil.

Include at least one case with a sharp phase transition so the phase unwrapping is actually exercised.

### D10. `line_profile`
Verify:

- profile endpoints match the solved endpoint states
- continuity holds across internal segment boundaries within numerical tolerance
- reversing endpoint order reverses the x-axis convention consistently

---

## 8. Layer E - Numerical robustness validation

### E1. Frequency-grid reproducibility
Repeated runs with the same input must produce identical results.

### E2. Resolution sensitivity
A moderately refined frequency grid must not change the qualitative interpretation of the main results.

### E3. Singular and near-singular detection
Invalid or ill-posed models must fail clearly.

Required subcases:

- disconnected floating acoustic subnetwork
- no shunt path to pressure reference in an acoustic component
- illegal zero area or zero length if schema validation misses them
- degenerate driver coupling topology

### E4. Very-low-frequency behavior
Add at least one official test sweep that reaches a sufficiently low frequency to verify the \(\omega \to 0\) behavior of:

- cone displacement
- cone velocity
- input impedance
- radiator reactance sign

### E5. Exact DC rejection
The solver must reject \(f = 0\) and negative frequencies with clear errors.

### E6. High-Q / lossless sensitivity note
Because v1 intentionally defers internal damping models for ducts and lines, some idealized topologies can be very sharp or strongly grid-sensitive near resonance.

The validation plan does **not** hide this by adding undocumented numerical damping.

Instead, the project must:

- document where the topology is intentionally lossless
- compare nearby-grid behavior honestly
- reject only truly singular or ill-posed models

---

## 9. External reference strategy

Preferred reference hierarchy:

1. exact formula frozen in the spec
2. hand-derived reference calculation
3. trusted external simulator within overlapping scope
4. internal convergence study

Potential comparison targets for overlapping cases:

- textbook sealed-box relations
- textbook Helmholtz tuning estimates
- Akabak 2.1 LEM cases when topology and assumptions are matched carefully
- Hornresp for simple line or vented cases only when the modeled assumptions actually match

External comparisons must document assumption mismatches explicitly.

---

## 10. Release-gating validation set for first implementation

Mandatory before the first public implementation is called usable:

### Parser and normalization
- A1 through A7

### Primitive checks
- B1 through B8

### Integrated cases
- C1 through C9

### Observation checks
- D1 through D10

### Robustness checks
- E1 through E6

---

## 11. Validation artifacts to store in the repo

The repository should contain, as development progresses:

- input example files used for validation
- reference outputs or formula evaluators
- short notes describing the purpose of each validation case
- plots only as supporting evidence, not as the sole proof
- regression tests wherever numerical comparison is stable enough

Suggested future structure:

```text
examples/
  free_air/
  closed_box/
  vented_box/
  line_basic/
  side_branch/

tests/
  parser/
  normalization/
  primitives/
  integration/
  observations/
```

---

## 12. Remaining non-blocking implementation choices

After this revision, the main remaining implementation choices are routine rather than architectural, for example:

1. exact user-facing error-message wording
2. optional warning policy outside first validated radiator bands
3. exact regression-test packaging and file layout

These are not blockers for starting implementation.

---

## 13. Summary

The updated validation strategy now explicitly targets the major failure modes identified during external review:

1. radiator formulas are pinned and matched quantitatively
2. front/rear driver sign is tested explicitly
3. node-order reversal semantics are tested explicitly
4. `spl_sum` cancellation is tested explicitly
5. very-low-frequency behavior is tested explicitly
6. parallel-path assembly is tested explicitly
7. segmentation refinement remains a release blocker for line models

If this discipline is followed, the first public `os-lem` kernel can remain narrow in scope while still being technically trustworthy.
