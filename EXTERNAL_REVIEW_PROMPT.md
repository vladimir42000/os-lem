# External review prompt for another AI

You are reviewing the design documents of an open-source loudspeaker simulator project called `os-lem`.

The project is intentionally in the specification phase. No implementation is started yet. The goal of this review is not to propose a different project. The goal is to find mathematical ambiguities, missing constraints, hidden contradictions, weak validation logic, and anything that could cause two competent developers to implement different solvers from the same docs.

## Project scope
Please assume the following frozen v1 scope:

- one logical driver only
- linear small-signal frequency-domain solver
- node-based acoustic network
- user-facing driver modes:
  - `ts_classic`
  - `em_explicit`
- canonical internal driver representation:
  - `Re`
  - `Le`
  - `Bl`
  - `Mms`
  - `Cms`
  - `Rms`
  - `Sd`
- supported acoustic element types:
  - `volume`
  - `duct`
  - `waveguide_1d`
  - `radiator`
- `side_branch` and `resonator` are not primitive object types; they are built by topology
- supported v1 `waveguide_1d` profile:
  - `conical`
- supported v1 radiator models:
  - `infinite_baffle_piston`
  - `unflanged_piston`
  - `flanged_piston`
- supported observation types:
  - `input_impedance`
  - `spl`
  - `spl_sum`
  - `cone_displacement`
  - `cone_velocity`
  - `element_volume_velocity`
  - `element_particle_velocity`
  - `node_pressure`
  - `line_profile`
  - `group_delay`
- `phase` is not a separate observation type; it is exported for complex observations
- parser accepts a small whitelist of engineering units and normalizes internally to SI
- unknown fields and missing required fields are hard errors

## Review task
Read the attached documents and critique them as a technical reviewer.

Please focus on:

1. sign conventions and equation consistency
2. whether the unknown vector and matrix assembly are fully defined
3. whether `volume`, `duct`, `waveguide_1d`, and `radiator` are defined precisely enough for implementation
4. whether the `waveguide_1d` segmented conical treatment is mathematically sound for v1
5. whether `spl`, `spl_sum`, `line_profile`, and `group_delay` are defined unambiguously
6. whether the validation plan is strong enough to catch likely implementation mistakes
7. whether any important numerical edge cases or topology edge cases are missing
8. whether any part of the spec would allow two developers to produce meaningfully different behavior
9. what should be frozen before implementation starts
10. what is acceptable to leave intentionally deferred

## Output format requested
Please answer in five sections:

### 1. Strong points
What is already well specified and likely to help implementation succeed?

### 2. Ambiguities or risks
What is underdefined, internally inconsistent, or risky?

### 3. Likely mathematical mistakes or hidden traps
Point to any equations, conventions, or modeling choices that look suspicious or incomplete.

### 4. Validation weaknesses
What tests are missing, circular, too weak, or not targeted enough?

### 5. Concrete recommended changes
List the changes you would make before implementation begins.

## Important review behavior
- Be critical, not polite.
- Do not rewrite the whole project.
- Do not suggest adding large new scope unless a missing point is truly blocking correctness.
- Distinguish clearly between:
  - must fix before implementation
  - should fix soon
  - acceptable to defer
- If you think a choice is acceptable but not ideal, say so explicitly.
