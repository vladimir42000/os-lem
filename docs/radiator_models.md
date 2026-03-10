# Radiator models

## Purpose
This document freezes the exact v1 radiator formulas.

A v1 radiator model returns two things:

1. a boundary acoustic impedance \(Z_{rad}(\omega) = p / Q\) used in the network solve
2. an on-axis far-field observation transfer \(H_Q(\omega, r)\) such that
   \[
   p_{obs}(\omega, r) = H_Q(\omega, r)\,Q_{rad}(\omega)
   \]

Here:

- \(p\) is the radiator node pressure
- \(Q\) is the radiator branch volume velocity
- \(Q_{rad}\) is positive in the same sign convention used by the branch equation
- \(r\) is the required observation distance for `spl`
- \(k = \omega / c_0\)
- \(S\) is radiator area
- \(a = \sqrt{S/\pi}\) is the equivalent circular radius

This document freezes engineering v1 formulas, not the final word on acoustic radiation theory.

---

## 1. Shared observation transfer rules

### 1.1 `spl` geometry in v1
A v1 `spl` observation is:

- on-axis
- far-field
- single-distance only

No user-facing angle parameter exists in v1.

### 1.2 Half-space and full-space transfers
For the far-field observation transfer, v1 uses the following source-strength relations:

#### Half-space transfer
Used by:

- `infinite_baffle_piston`
- `flanged_piston`

\[
H_{half}(\omega, r) = \frac{j\omega\rho_0}{2\pi r} e^{-jkr}
\]

so that

\[
p_{obs}(\omega, r) = H_{half}(\omega, r)\,Q_{rad}(\omega)
\]

#### Full-space transfer
Used by:

- `unflanged_piston`

\[
H_{full}(\omega, r) = \frac{j\omega\rho_0}{4\pi r} e^{-jkr}
\]

so that

\[
p_{obs}(\omega, r) = H_{full}(\omega, r)\,Q_{rad}(\omega)
\]

### 1.3 Scope note
In v1, the boundary impedance model and the far-field transfer model are frozen together as an engineering contract, but they are not claimed to be a full unified 3D radiation solution for all geometries.

This is acceptable for v1 because `os-lem` is a one-dimensional lumped / waveguide electroacoustic solver, not a full BEM/FEM radiation solver.

---

## 2. `infinite_baffle_piston`

### 2.1 Boundary impedance
The v1 boundary impedance is the baffled circular piston radiation impedance written in acoustic form.

Define

\[
x = 2ka
\]

and the dimensionless normalized radiation impedance

\[
z_{baf}(x) = R_1(x) + j X_1(x)
\]

with

\[
R_1(x) = 1 - \frac{2 J_1(x)}{x}
\]

and

\[
X_1(x) = \frac{2 H_1(x)}{x}
\]

where:

- \(J_1\) is the Bessel function of the first kind, order 1
- \(H_1\) is the Struve function of order 1

Then the acoustic boundary impedance is

\[
Z_{rad}(\omega) = \frac{\rho_0 c_0}{S} z_{baf}(2ka)
\]

### 2.2 Frozen Struve approximation
To avoid making special-function support a blocker for the first implementation, v1 freezes the Aarts-Janssen approximation for \(H_1\):

\[
H_1(z) \approx \frac{2}{\pi} - J_0(z)
+ \left(\frac{16}{\pi^2} - 1\right) \frac{\sin z}{z}
+ \left(\frac{12}{\pi} - \frac{36}{\pi^2}\right) \frac{1 - \cos z}{z^2}
\]

with the removable-singularity handling:

- at \(z = 0\), use \(H_1(0) = 0\)
- for very small \(|z|\), the implementation must avoid raw division-by-zero in the approximation expression

v1 freezes this approximation exactly as written. Implementations must not substitute a different Struve evaluator unless that decision is explicitly reopened.

### 2.3 Observation transfer
The frozen v1 observation transfer is the half-space transfer:

\[
p_{obs}(\omega, r) = \frac{j\omega\rho_0}{2\pi r} e^{-jkr} Q_{rad}(\omega)
\]

---

## 3. `flanged_piston`

### 3.1 Boundary impedance
The v1 boundary impedance is the causal low-order Padé approximation for the plane-wave radiation impedance of an infinitely flanged circular pipe end.

Define

\[
x = ka
\]

and the dimensionless normalized radiation impedance

\[
z_{fl}(x) = \frac{j(d_1 - n_1)x + d_2 x^2}{2 - j(d_1 + n_1)x - d_2 x^2}
\]

with frozen coefficients:

- \(n_1 = 0.182\)
- \(d_1 = 1.825\)
- \(d_2 = 0.649\)

Then

\[
Z_{rad}(\omega) = \frac{\rho_0 c_0}{S} z_{fl}(ka)
\]

These rounded coefficient values are themselves part of the frozen v1 contract. Implementations must use exactly these numbers unless the project explicitly revises them.

### 3.2 Low-frequency behavior check
The formula above reproduces the standard low-frequency flanged end-correction constant

\[
\eta = 0.8216
\]

through the small-\(ka\) reactance slope.

### 3.3 Observation transfer
The frozen v1 observation transfer is the half-space transfer:

\[
p_{obs}(\omega, r) = \frac{j\omega\rho_0}{2\pi r} e^{-jkr} Q_{rad}(\omega)
\]

### 3.4 Validated range
This model is part of the official v1 validation set over approximately:

\[
ka \le 2
\]

---

## 4. `unflanged_piston`

### 4.1 Boundary impedance
The v1 boundary impedance is the causal low-order Padé approximation for the plane-wave radiation impedance of an unflanged circular pipe end.

Define

\[
x = ka
\]

and the dimensionless normalized radiation impedance

\[
z_{un}(x) = \frac{j(d_1 - n_1)x + d_2 x^2}{2 - j(d_1 + n_1)x - d_2 x^2}
\]

with frozen coefficients:

- \(n_1 = 0.167\)
- \(d_1 = 1.393\)
- \(d_2 = 0.457\)

Then

\[
Z_{rad}(\omega) = \frac{\rho_0 c_0}{S} z_{un}(ka)
\]

These rounded coefficient values are themselves part of the frozen v1 contract. Implementations must use exactly these numbers unless the project explicitly revises them.

### 4.2 Low-frequency behavior check
The formula above reproduces the standard low-frequency unflanged end-correction constant

\[
\eta = 0.6133
\]

through the small-\(ka\) reactance slope.

### 4.3 Observation transfer
The frozen v1 observation transfer is the full-space transfer:

\[
p_{obs}(\omega, r) = \frac{j\omega\rho_0}{4\pi r} e^{-jkr} Q_{rad}(\omega)
\]

### 4.4 Validated range
This model is part of the official v1 validation set over approximately:

\[
ka \le 2
\]

---

## 5. Summary table

| model | boundary impedance basis | observation transfer | validated band |
|---|---|---|---|
| `infinite_baffle_piston` | baffled circular piston | half-space | project validation cases define practical band |
| `flanged_piston` | causal Padé flanged pipe-end model | half-space | \(ka \le 2\) |
| `unflanged_piston` | causal Padé unflanged pipe-end model | full-space | \(ka \le 2\) |

---

## 6. Frozen implementation notes

The following are frozen for v1 implementation consistency:

1. baffled piston uses the normalized impedance with argument \(2ka\)
2. flanged and unflanged pipe-end Padé models use argument \(ka\)
3. the rounded Padé coefficients written in this document are the frozen project coefficients
4. implementations may warn when a radiator is used outside its first validated \(ka\) band, but such warnings are not mandatory for v1 correctness

---

## 7. References behind the frozen v1 formulas

The v1 formulas are based on:

- baffled piston radiation impedance written via Bessel and Struve functions
- Aarts-Janssen approximation for the Struve function \(H_1\)
- Silva, Kergomard, Mallaroni, and Norris causal Padé approximations for flanged and unflanged pipe-end radiation impedance

The project freezes these specific engineering formulas for implementation consistency.
