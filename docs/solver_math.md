# Solver math

## Purpose
This document freezes the mathematical contract for the first numerical implementation of `os-lem`.

The goal is not to write a full acoustics textbook. The goal is to define one unambiguous linear frequency-domain formulation that two independent developers would implement in the same way.

This document follows the frozen v1 scope:

- one logical driver
- linear small-signal modeling
- frequency-domain solve
- node-based acoustic network
- supported acoustic element types:
  - `volume`
  - `duct`
  - `waveguide_1d`
  - `radiator`
- supported v1 `waveguide_1d` profile:
  - `conical`
- user-facing driver modes:
  - `ts_classic`
  - `em_explicit`
- canonical internal driver form:
  - `Re`
  - `Le`
  - `Bl`
  - `Mms`
  - `Cms`
  - `Rms`
  - `Sd`

---

## 1. Modeling assumptions

### 1.1 Physical scope
v1 assumes:

- linear acoustics
- linear electromechanical driver behavior
- quiescent medium
- fixed ambient air properties
- no turbulence model
- no thermal compression model
- no nonlinear suspension, motor, or inductance effects
- no structural cabinet vibration model
- no mutual radiation coupling between separate radiators in v1

### 1.2 Harmonic convention
The entire solver uses the harmonic convention

\[
e^{j\omega t}
\]

with angular frequency

\[
\omega = 2\pi f
\]

All impedances, admittances, transfer functions, phases, and post-processing rules in this document follow that convention.

### 1.3 Frozen default air constants
The frozen v1 reference-air constants are:

- density: \(\rho_0 = 1.2041\,\mathrm{kg/m^3}\)
- sound speed: \(c_0 = 343.2\,\mathrm{m/s}\)

The corresponding characteristic impedance is:

\[
Z_c = \rho_0 c_0
\]

These values are part of the v1 numerical baseline and are not left to implementation choice.

### 1.4 Pressure reference
All acoustic node pressures in v1 are **gauge pressures relative to ambient pressure**.

---

## 2. Canonical internal driver representation

The solver never works directly on mixed user schemas. After parsing, the driver is always represented internally by:

- \(R_e\) electrical DC resistance
- \(L_e\) voice-coil inductance
- \(Bl\) force factor
- \(M_{ms}\) moving mass
- \(C_{ms}\) mechanical compliance
- \(R_{ms}\) mechanical resistance
- \(S_d\) effective diaphragm area

All are in SI units.

### 2.1 Classical T/S normalization
If the user provides `model: ts_classic`, the parser must derive the canonical form before solving.

Using:

- resonance frequency \(f_s\)
- angular resonance \(\omega_s = 2\pi f_s\)
- equivalent acoustic compliance volume relation
  \[
  C_{ab} = \frac{V_{as}}{\rho_0 c_0^2}
  \]
- diaphragm mechanical compliance
  \[
  C_{ms} = \frac{C_{ab}}{S_d^2}
  \]
- moving mass from resonance
  \[
  M_{ms} = \frac{1}{\omega_s^2 C_{ms}}
  \]
- mechanical resistance from \(Q_{ms}\)
  \[
  R_{ms} = \frac{\omega_s M_{ms}}{Q_{ms}}
  \]
- force factor from \(Q_{es}\)
  \[
  Q_{es} = \frac{\omega_s M_{ms} R_e}{(Bl)^2}
  \quad \Rightarrow \quad
  Bl = \sqrt{\frac{\omega_s M_{ms} R_e}{Q_{es}}}
  \]

### 2.2 Classical-versus-explicit consistency tolerance
If both classical and explicit canonical fields are present, the parser compares the derived and declared canonical values using:

\[
|x_{declared} - x_{derived}| \le \max(\tau_{abs}, \tau_{rel}|x_{derived}|)
\]

with frozen v1 tolerances:

- \(\tau_{rel} = 5 \times 10^{-3}\)
- \(\tau_{abs} = 1 \times 10^{-12}\) in SI units

Behavior:

- all compared canonical values within tolerance: accept with warning
- one or more compared canonical values outside tolerance: hard error

These tolerances are parser policy, not solver numerics.

---

## 3. Nodes, topology, and ordering

### 3.1 Node semantics
Acoustic nodes are identified by symbolic names.

Frozen v1 rules:

- identical node names refer to the same acoustic node
- different node names refer to different acoustic nodes
- multiple elements may connect the same ordered or unordered node pair
- such multiple connections are valid and represent **parallel branches**

Examples:

- a `duct` ending at `n2` and a `volume` attached to `n2` share the same node
- two `duct` elements between `n1` and `n2` are parallel acoustic branches and both are assembled

### 3.2 Reference handling
There is **no user-declared special ground node** in v1.

Instead, the pressure reference is implicit. Shunt-type elements such as `volume` and `radiator` connect to the ambient pressure reference internally.

Names such as `0`, `gnd`, or `ground` have no special meaning unless the project explicitly introduces that feature in a future version.

### 3.3 Unknown ordering
The acoustic network is node-based. Its primary unknowns are complex acoustic node pressures:

\[
\mathbf{p} = [p_1, p_2, \dots, p_N]^T
\]

The frozen v1 node ordering rule is:

- acoustic nodes are ordered by **first appearance after parser normalization**

This rule is deterministic and is part of the contract for reproducible assembly.

### 3.4 Element traversal order
The frozen v1 element assembly order is:

- elements are assembled in **input-file order after parser normalization**

If multiple elements connect the same nodes, their contributions are added in that order.

### 3.5 Driver auxiliary unknowns
The single driver contributes two additional unknowns:

- electrical current \(I\)
- diaphragm velocity \(U\)

So the full v1 unknown vector is:

\[
\mathbf{x} =
\begin{bmatrix}
\mathbf{p} \\
I \\
U
\end{bmatrix}
\]

with dimension \(N + 2\).

### 3.6 Global linear system
At each frequency point, the solver assembles a complex linear system:

\[
\mathbf{A}(\omega)\,\mathbf{x}(\omega) = \mathbf{b}(\omega)
\]

where:

- \(\mathbf{A}(\omega)\) is the assembled complex system matrix
- \(\mathbf{x}(\omega)\) is the unknown vector
- \(\mathbf{b}(\omega)\) contains source terms

Each frequency is solved independently.

### 3.7 Matrix structure note
The coupled electromechanical-acoustic matrix is **not** assumed to be symmetric, Hermitian, or positive definite.

Implementations must therefore use a general complex linear solver and must not rely on symmetry-specific factorization or storage assumptions.

---

## 4. Driver equations

The driver is a coupled electromechanical two-sided acoustic source connected between:

- `node_front`
- `node_rear`

Let the front and rear acoustic pressures at the driver be:

\[
p_f, \quad p_r
\]

### 4.1 Positive direction of diaphragm motion
The frozen v1 sign convention is:

- positive diaphragm velocity \(U\) means motion **toward the front side**

This physical direction defines the acoustic injection signs below.

### 4.2 Electrical equation
The electrical loop equation is:

\[
V = (R_e + j\omega L_e) I + Bl\,U
\]

where:

- \(V\) is the imposed drive voltage phasor
- \(I\) is voice-coil current
- \(U\) is diaphragm velocity

### 4.3 Mechanical equation
The mechanical force balance is:

\[
Bl\,I = Z_m U + F_{ac}
\]

with mechanical impedance

\[
Z_m = R_{ms} + j\omega M_{ms} + \frac{1}{j\omega C_{ms}}
\]

and acoustic load force

\[
F_{ac} = S_d (p_f - p_r)
\]

Therefore the assembled mechanical equation is:

\[
Bl\,I - Z_m U - S_d(p_f - p_r) = 0
\]

### 4.4 Acoustic injection by diaphragm motion
Define the diaphragm volume velocity:

\[
Q_d = S_d U
\]

Then the driver contributes:

- front-node injection: \(+Q_d\)
- rear-node injection: \(-Q_d\)

This means:

- positive \(U\) injects positive volume velocity into the front acoustic node
- positive \(U\) extracts the same volume velocity from the rear acoustic node

This sign convention is frozen for v1.

---

## 5. Acoustic nodal formulation

The acoustic system is assembled using Kirchhoff-style volume-flow balance at each acoustic node.

For any node \(k\):

\[
\sum Q_{k,\text{out}} = 0
\]

The implementation may use either impedance or admittance forms internally, but the assembled equations must be mathematically equivalent to the element definitions below.

### 5.1 Topology grounding rule
Every acoustically connected component must have at least one valid **path to the pressure reference** through one or more branches that include a shunt-type boundary or compliance element.

In v1, examples of valid grounding elements are:

- `volume`
- `radiator`

A connected component built only from series-type elements and driver couplings, with no shunt path to reference, is invalid and must be rejected before solve.

---

## 6. Primitive element definitions

### 6.1 `volume`
A closed acoustic volume attached to one node is modeled as an acoustic compliance to reference.

For physical volume \(V\), the acoustic compliance is:

\[
C_a = \frac{V}{\rho_0 c_0^2}
\]

Its acoustic admittance is:

\[
Y_a = j\omega C_a
\]

If the node pressure is \(p\), the flow leaving the node and entering the compliance branch is:

\[
Q = Y_a p
\]

So a `volume` contributes a one-node shunt admittance \(+Y_a\) to the corresponding acoustic node equation.

---

### 6.2 `duct`
A v1 `duct` is a lumped two-node acoustic inertance element.

For duct length \(L\) and cross-sectional area \(S\), the acoustic mass is:

\[
M_a = \rho_0 \frac{L}{S}
\]

and the series acoustic impedance is:

\[
Z_a = j\omega M_a
\]

The volume flow from node \(a\) to node \(b\) is:

\[
Q_{ab} = \frac{p_a - p_b}{Z_a}
\]

The corresponding nodal flow equations are:

\[
Q_a = +\frac{1}{Z_a}p_a - \frac{1}{Z_a}p_b
\]

\[
Q_b = -\frac{1}{Z_a}p_a + \frac{1}{Z_a}p_b
\]

So the element contributes the standard two-node series admittance stamp with:

\[
Y_{ab} = \frac{1}{Z_a}
\]

and matrix entries:

\[
\begin{bmatrix}
+Y_{ab} & -Y_{ab} \\
-Y_{ab} & +Y_{ab}
\end{bmatrix}
\]

in the acoustic node-pressure subsystem.

#### 6.2.1 Duct losses
Viscous and thermal loss terms are deferred in v1.

---

### 6.3 `waveguide_1d`
A v1 `waveguide_1d` is a user-facing distributed acoustic line element with `profile: conical`.

#### 6.3.1 User-level meaning
The user specifies:

- `node_a`
- `node_b`
- total length \(L\)
- start area \(S_0\)
- end area \(S_L\)
- number of internal segments \(N_{seg}\)

#### 6.3.2 Frozen internal treatment in v1
The user-facing conical line is internally expanded into \(N_{seg}\) short uniform cylindrical subsegments.

The radius is assumed to vary linearly with axial position:

\[
r(x) = r_0 + \frac{r_L - r_0}{L}x
\]

where

\[
r_0 = \sqrt{\frac{S_0}{\pi}},
\qquad
r_L = \sqrt{\frac{S_L}{\pi}}
\]

For each subsegment, define:

- segment length \(\Delta x = L/N_{seg}\)
- midpoint position \(x_i = (i - 1/2)\Delta x\)
- local midpoint radius \(r_i = r(x_i)\)
- local area \(S_i = \pi r_i^2\)

The frozen v1 segmentation rule is therefore:

- **use midpoint area for each subsegment**

This is a deliberate engineering approximation, not an exact conical-wave solution.

#### 6.3.3 Uniform subsegment transfer matrix
For one uniform subsegment with area \(S\), length \(\ell\), and wavenumber

\[
k = \omega / c_0
\]

define the volume-velocity state vector:

\[
\begin{bmatrix}
p_1 \\
Q_1
\end{bmatrix}
=
\mathbf{T}(\ell,S)
\begin{bmatrix}
p_2 \\
Q_2
\end{bmatrix}
\]

with

\[
\mathbf{T}(\ell,S)=
\begin{bmatrix}
\cos(k\ell) & j Z_c^{(a)} \sin(k\ell) \\
j \dfrac{1}{Z_c^{(a)}} \sin(k\ell) & \cos(k\ell)
\end{bmatrix}
\]

where the acoustic characteristic impedance referred to volume velocity is:

\[
Z_c^{(a)} = \frac{\rho_0 c_0}{S}
\]

#### 6.3.4 Equivalent two-port admittance form for one uniform segment
For one uniform lossless segment,

\[
\begin{bmatrix}
Q_1 \\
Q_2
\end{bmatrix}
=
\mathbf{Y}_{seg}
\begin{bmatrix}
p_1 \\
p_2
\end{bmatrix}
\]

with

\[
\mathbf{Y}_{seg} =
\begin{bmatrix}
- j \dfrac{1}{Z_c^{(a)}} \cot(k\ell) & + j \dfrac{1}{Z_c^{(a)}} \csc(k\ell) \\
+ j \dfrac{1}{Z_c^{(a)}} \csc(k\ell) & - j \dfrac{1}{Z_c^{(a)}} \cot(k\ell)
\end{bmatrix}
\]

The internal port convention is:

- \(Q_1\) is flow **into** the segment at end 1
- \(Q_2\) is flow **into** the segment at end 2

#### 6.3.5 Cylindrical special case
If \(S_0 = S_L\), the conical profile degenerates to a cylindrical line. The same segmentation rule still applies.

#### 6.3.6 Waveguide losses
The current distributed-loss extension is frozen as:

- `waveguide_1d` only
- user-specified attenuation coefficient \(lpha\) in nepers per meter
- segmented conical or cylindrical geometry using the current midpoint-area approximation
- no automatic thermo-viscous derivation
- no exact broad horn-parity claim beyond this bounded segmented model

For the cylindrical special case, the implementation should still match the exact cylindrical lossy reference:

\[
\gamma = lpha + jrac{\omega}{c_0}
\]

\[
Z_c^{(a)} = rac{
ho_0 c_0}{S}
\]

\[
\mathbf{T}_{cyl,loss}(\ell) =
egin{bmatrix}
\cosh(\gamma \ell) & Z_c^{(a)}\sinh(\gamma \ell) \
\dfrac{1}{Z_c^{(a)}}\sinh(\gamma \ell) & \cosh(\gamma \ell)
\end{bmatrix}
\]

\[
\mathbf{Y}_{cyl,loss}(\ell) =
egin{bmatrix}
\dfrac{1}{Z_c^{(a)}}\coth(\gamma \ell) & -\dfrac{1}{Z_c^{(a)}}\operatorname{csch}(\gamma \ell) \
-\dfrac{1}{Z_c^{(a)}}\operatorname{csch}(\gamma \ell) & \dfrac{1}{Z_c^{(a)}}\coth(\gamma \ell)
\end{bmatrix}
\]

When `loss` is absent or zero, the current implementation must reduce exactly to the corresponding current lossless behavior for the same geometry.

For a lossy conical `waveguide_1d`, the current solver applies the same complex propagation constant
\(\gamma = lpha + j\omega/c_0\) to each internally segmented uniform subsection while retaining the existing midpoint-area conical approximation.
This is a bounded practical engineering extension of the current segmented line model, not a claim of exact closed-form lossy conical-wave theory.

---

### 6.4 `radiator`
A v1 `radiator` is a one-port acoustic boundary element attached to one acoustic node.

It has two roles:

1. it terminates the acoustic network through a radiation impedance
2. it provides the transfer needed to compute far-field SPL observations

The exact frozen v1 formulas are defined in `docs/radiator_models.md`.

At the network boundary, a radiator attached to a node with pressure \(p\) is represented as a shunt acoustic admittance

\[
Y_{rad}(\omega) = \frac{1}{Z_{rad}(\omega)}
\]

so that the node flow contribution is:

\[
Q = Y_{rad} p
\]

---

## 7. System assembly details

Let the acoustic subsystem contain \(N\) node pressures.

The full system is ordered as:

\[
\mathbf{x} =
\begin{bmatrix}
p_1 \\
\vdots \\
p_N \\
I \\
U
\end{bmatrix}
\]

The assembled matrix may be written blockwise as:

\[
\begin{bmatrix}
\mathbf{A}_{pp} & \mathbf{A}_{pI} & \mathbf{A}_{pU} \\
\mathbf{A}_{Ip} & A_{II} & A_{IU} \\
\mathbf{A}_{Up} & A_{UI} & A_{UU}
\end{bmatrix}
\begin{bmatrix}
\mathbf{p} \\
I \\
U
\end{bmatrix}
=
\begin{bmatrix}
\mathbf{0} \\
V \\
0
\end{bmatrix}
\]

where:

- \(\mathbf{A}_{pp}\) is the assembled acoustic nodal matrix from `volume`, `duct`, segmented `waveguide_1d`, and `radiator`
- \(\mathbf{A}_{pU}\) contains diaphragm volume-velocity injection coupling
- \(\mathbf{A}_{Up}\) contains acoustic loading of the diaphragm
- \(A_{II} = R_e + j\omega L_e\)
- \(A_{IU} = Bl\)
- \(A_{UI} = Bl\)
- \(A_{UU} = -Z_m\)

The frozen driver-coupling coefficients are:

- front-node acoustic equation: add \(+S_d U\)
- rear-node acoustic equation: add \(-S_d U\)
- mechanical equation coefficient of \(p_f\): \(-S_d\)
- mechanical equation coefficient of \(p_r\): \(+S_d\)
- mechanical equation coefficient of \(I\): \(+Bl\)
- mechanical equation coefficient of \(U\): \(-Z_m\)

---

## 8. Excitation and frequency domain

### 8.1 Voltage drive
v1 uses a linear voltage source drive on the single driver.

The frozen v1 source convention is:

- source phasor is real and positive
- source magnitude is RMS
- example and CLI default magnitude is **2.83 V RMS** unless explicitly overridden

User-supplied complex voltage sources are out of scope for v1.

### 8.2 Frequency-domain requirement
The frozen v1 formulation is valid only for strictly positive frequencies:

\[
f > 0
\]

Therefore:

- \(f = 0\) must be rejected with a clear error
- negative frequencies must be rejected with a clear error

Very low positive frequencies are allowed, but exact DC is not part of the v1 solve contract because the formulation contains \(1/(j\omega)\) terms.

---

## 9. Observation formulas

This section freezes how solved unknowns become exported engineering results.

### 9.1 Flow sign convention for reporting
Whenever `os-lem` exports an element volume velocity with ordered endpoints, the positive direction is **from `node_a` to `node_b`**.

This is a reporting convention and must not change with internal matrix sign choices.

### 9.2 Input impedance
For the single driver:

\[
Z_{in}(\omega) = \frac{V(\omega)}{I(\omega)}
\]

### 9.3 Cone velocity
Cone velocity is the solved diaphragm velocity:

\[
U(\omega)
\]

### 9.4 Cone displacement
With the \(e^{j\omega t}\) convention:

\[
U = j\omega X
\quad \Rightarrow \quad
X(\omega) = \frac{U(\omega)}{j\omega}
\]

### 9.5 Element volume velocity
For a target element, export the complex through-flow associated with that element.

Frozen v1 rules:

- `duct`: report \(Q_{ab}\), positive from `node_a` to `node_b`
- `radiator`: report the branch flow leaving the acoustic node and entering the radiation boundary
- `waveguide_1d`: the observation **must** specify `location: a` or `location: b`

For `waveguide_1d`, using the internal two-port convention from Section 6.3.4:

- \(Q_{export,a} = +Q_1\)
- \(Q_{export,b} = -Q_2\)

so that both reported endpoint values use the common positive direction from `node_a` toward `node_b`.

### 9.6 Element particle velocity
Particle velocity is derived from element volume velocity divided by the relevant local cross-sectional area:

\[
v(\omega) = \frac{Q(\omega)}{S}
\]

Frozen v1 area rules:

- `duct`: use the duct cross-sectional area
- `radiator`: use the radiator piston area
- `waveguide_1d`: use the local endpoint area selected by `location: a` or `location: b`

### 9.7 Node pressure
Node pressure is directly the solved complex pressure phasor at the named acoustic node.

### 9.8 Complex export baseline
The frozen v1 machine-readable default for complex observations is Cartesian export:

- real part
- imaginary part

Magnitude and phase may be derived or additionally exported, but Cartesian form is the baseline representation.

### 9.9 SPL from one radiator
A v1 `spl` observation is an **on-axis far-field** pressure observation from a named radiator.

Frozen v1 rules:

- `distance_m` is required
- angular directivity is not user-exposed in v1
- the radiator model provides the transfer from radiator branch flow to on-axis far-field pressure

Then SPL is:

\[
\text{SPL}(\omega) = 20 \log_{10}\left(\frac{|p_{obs}(\omega)|}{p_{ref}}\right)
\]

with acoustic reference pressure:

\[
p_{ref} = 20\,\mu\text{Pa}
\]

### 9.10 Complex SPL summation
For `spl_sum`, individual radiator observation pressures are summed as complex pressures before conversion to dB:

\[
p_{sum}(\omega) = \sum_{m=1}^{M} p_{obs,m}(\omega)
\]

then

\[
\text{SPL}_{sum}(\omega) = 20 \log_{10}\left(\frac{|p_{sum}(\omega)|}{p_{ref}}\right)
\]

Summing dB values is explicitly forbidden.

### 9.11 Phase export
Phase is not a separate observation type in v1.

For every complex-valued exported observation, phase may be exported as an attribute derived from the complex result.

### 9.12 Group delay
Group delay is defined from the unwrapped phase of a named complex observation:

\[
\tau_g(\omega) = -\frac{d\phi(\omega)}{d\omega}
\]

The frozen discrete v1 stencil is:

for interior points \(i = 1, \dots, N-2\),

\[
\tau_{g,i} = - \frac{\phi_{i+1} - \phi_{i-1}}{\omega_{i+1} - \omega_{i-1}}
\]

for the first point,

\[
\tau_{g,0} = - \frac{\phi_1 - \phi_0}{\omega_1 - \omega_0}
\]

for the last point,

\[
\tau_{g,N-1} = - \frac{\phi_{N-1} - \phi_{N-2}}{\omega_{N-1} - \omega_{N-2}}
\]

The frozen v1 phase-unwrapping rule is the standard adjacent-jump correction with threshold \(\pi\):

- if \(\Delta\phi > \pi\), subtract \(2\pi\)
- if \(\Delta\phi < -\pi\), add \(2\pi\)
- apply cumulatively along the sweep order

This rule is frozen for v1.

---

## 10. Line-profile reconstruction

`line_profile` is an important v1 observation for understanding resonances and resonator placement.

For a target `waveguide_1d` and requested frequency \(f_0\):

1. solve the global model at \(f_0\)
2. recover the complex pressures and endpoint flows of each internal waveguide segment
3. reconstruct the requested field quantity along the segmented line
4. resample to the requested number of output points if needed

### 10.1 Pressure and volume velocity inside one uniform segment
Within one uniform segment, the local pressure and volume velocity are obtained from the standard forward/backward wave solution or equivalently from the transfer-matrix relation referenced to one segment endpoint.

If \(x\) is measured from the segment's left endpoint:

\[
\begin{bmatrix}
p(x) \\
Q(x)
\end{bmatrix}
=
\mathbf{T}(x,S)
\begin{bmatrix}
p(0) \\
Q(0)
\end{bmatrix}
\]

with the same uniform-segment transfer matrix as defined earlier.

Particle velocity is then:

\[
v(x) = \frac{Q(x)}{S}
\]

using the local segment area \(S\).

### 10.2 Output quantities
The v1 `line_profile` observation supports:

- `pressure`
- `volume_velocity`
- `particle_velocity`

The exported x-coordinate is axial distance along the user-facing `waveguide_1d` from `node_a` to `node_b`.

---

## 11. Units

All internal computation is performed in SI units.

The parser may accept a controlled whitelist of engineering units, but they must all normalize before any of the equations in this document are evaluated.

---

## 12. Numerical requirements

### 12.1 Frequency-by-frequency deterministic solve
Each frequency point is solved independently with deterministic ordering of unknowns and elements.

### 12.2 Singular-model detection
If the assembled system is singular or numerically ill-posed at a requested frequency, the solver must fail clearly rather than silently producing garbage.

### 12.3 No hidden topology repair
The solver must not invent missing nodes, implicit closures, or other hidden topology corrections. Invalid models are parser or validation errors.

### 12.4 No undocumented damping regularization
The solver must not inject hidden loss or damping terms to make a problematic model “work”.

If a requested frequency point is singular or too ill-conditioned for a reliable solve, that must be reported explicitly.

### 12.5 Reproducible observation definitions
The same model file must always produce the same observation meaning. No observation may depend on arbitrary internal ordering.

---

## 13. Explicit non-goals of this math contract

This document does not yet freeze:

- distributed loss models for lines or ducts
- measured-driver hybrid equations
- multi-driver matrix structure
- ambient medium customization beyond the frozen reference-air defaults
- off-axis SPL or explicit directivity modeling
- mutual radiation coupling between separate radiators

---

## 14. Summary of frozen v1 math choices

The following are fixed for v1 unless the project explicitly reopens them in the decision log:

1. harmonic convention is \(e^{j\omega t}\)
2. all acoustic node pressures are gauge pressures relative to ambient
3. default air constants are \(\rho_0 = 1.2041\,\mathrm{kg/m^3}\) and \(c_0 = 343.2\,\mathrm{m/s}\)
4. node identity is name-based and parallel branches are allowed
5. acoustic nodes are ordered by first appearance after parser normalization
6. elements are assembled in input-file order after parser normalization
7. the single driver adds unknowns \(I\) and \(U\)
8. positive \(U\) means diaphragm motion toward the front side
9. the driver acoustic force is \(S_d(p_f - p_r)\)
10. diaphragm volume velocity is \(Q_d = S_d U\)
11. `volume` is a shunt acoustic compliance
12. `duct` is a lumped two-node acoustic inertance
13. `waveguide_1d` is internally expanded into segmented uniform lossless line sections using midpoint area per subsegment
14. the reporting sign convention for ordered element flow is `node_a -> node_b`
15. `waveguide_1d` endpoint flow observations require explicit `location`
16. `spl` is an on-axis far-field radiator observation with required distance
17. complex observations export in Cartesian form by default
18. `spl_sum` is a complex pressure sum, never a dB sum
19. `group_delay` uses the frozen phase-unwrapping rule and discrete derivative stencil above
20. internal computation is SI-only after parser normalization
21. the topology grounding rule is mandatory
22. exact DC is forbidden; only \(f > 0\) is valid
23. no hidden damping regularization is allowed

This is the mathematical baseline for the first solver implementation and for the validation plan.
