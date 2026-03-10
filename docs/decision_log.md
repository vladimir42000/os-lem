# Decision log

This file records important project decisions so that the repository, not the chat, becomes the long-term memory of the project.

Format:

- Date
- Decision
- Status
- Reason

---

## 2026-03-09
**Decision:** Create an open command-line loudspeaker simulator inspired by Akabak 2.1 LEM.
**Status:** accepted
**Reason:** A scriptable and transparent LEM-style solver is feasible and useful for enclosure design, optimization, and later GUI work.

## 2026-03-09
**Decision:** v1 will focus on linear frequency-domain lumped / 1D acoustic simulation only.
**Status:** accepted
**Reason:** This is the most realistic path to a working kernel and matches the strongest immediate use cases.

## 2026-03-09
**Decision:** Do not target BEM or full Akabak 3 equivalence in v1.
**Status:** accepted
**Reason:** BEM and 3D acoustics would greatly increase complexity and slow progress before a validated core exists.

## 2026-03-09
**Decision:** Use Python as the main implementation language.
**Status:** accepted
**Reason:** Python gives the best balance of development speed, numerical tooling, plotting ecosystem, optimization compatibility, and future GUI options.

## 2026-03-09
**Decision:** CLI first, GUI later.
**Status:** accepted
**Reason:** Command-line workflows are easier to validate, automate, test, and integrate with optimization loops.

## 2026-03-09
**Decision:** Repository files are the project memory; chats are workspaces only.
**Status:** accepted
**Reason:** Long development cannot rely on chat history alone. Stable specs and logs are required.

## 2026-03-09
**Decision:** Organize development into a small number of focused threads.
**Status:** accepted
**Reason:** This keeps discussions manageable and reduces drift:
- master / roadmap
- solver physics
- implementation
- validation

## 2026-03-09
**Decision:** Prefer a general network philosophy rather than a Hornresp-like fixed topology.
**Status:** accepted
**Reason:** The software should remain flexible for arbitrary practical enclosure structures.

## 2026-03-09
**Decision:** Allow high-level horn / line shapes in user input, even if internally discretized.
**Status:** accepted
**Reason:** User convenience should not be sacrificed to internal solver simplicity.

## 2026-03-09
**Decision:** Pressure and volume-velocity inspection along 1D paths is a roadmap feature.
**Status:** accepted
**Reason:** This is highly valuable for resonator placement, line understanding, and future damping strategy work.

## 2026-03-09
**Decision:** Measured driver support is important but postponed until after the base kernel is stable.
**Status:** accepted
**Reason:** A trustworthy parametric kernel must exist before hybrid measured/parametric models are added.

## 2026-03-09
**Decision:** Advanced stuffing / porous-fill modeling is deferred.
**Status:** accepted
**Reason:** It is important but model-sensitive and should not block the first useful release.

## 2026-03-10
**Decision:** Freeze v1 to a single-driver, linear, frequency-domain, node-based electromechanical-acoustic solver for classic loudspeaker enclosure models.
**Status:** accepted
**Reason:** This is broad enough to be useful, but narrow enough to validate rigorously before adding multi-driver and measured-data complexity.

## 2026-03-10
**Decision:** The final v1 top-level schema is `meta`, `simulation`, `driver`, `elements`, `observations`, `output`.
**Status:** accepted
**Reason:** This is simple, readable, and sufficient for the first release.

## 2026-03-10
**Decision:** v1 uses explicit node-based acoustic connections.
**Status:** accepted
**Reason:** Node-based connectivity preserves the intended general-network philosophy and avoids fixed-topology restrictions.

## 2026-03-10
**Decision:** v1 accepts two user-facing driver input modes: `ts_classic` and `em_explicit`.
**Status:** accepted
**Reason:** Classical T/S parameters are widely available in datasheets, while explicit electromechanical parameters are better for advanced and validation use.

## 2026-03-10
**Decision:** The canonical internal driver representation is always `Re`, `Le`, `Bl`, `Mms`, `Cms`, `Rms`, `Sd`.
**Status:** accepted
**Reason:** The solver should operate on one normalized representation even if the user entered different accepted parameter sets.

## 2026-03-10
**Decision:** If classical and explicit driver fields are both present, the parser may accept the driver with a warning only if the derived and declared values are consistent within tolerance; otherwise it must raise an error.
**Status:** accepted
**Reason:** This preserves flexibility without silently accepting contradictory data.

## 2026-03-10
**Decision:** The supported v1 user-facing acoustic element types are `volume`, `duct`, `waveguide_1d`, and `radiator`.
**Status:** accepted
**Reason:** These primitives cover the first practically important enclosure classes while keeping implementation scope under control.

## 2026-03-10
**Decision:** `side_branch` and `resonator` are not primitive object types in v1; they are built by topology from the core elements.
**Status:** accepted
**Reason:** They are modeling patterns rather than fundamental primitives in a node-based network.

## 2026-03-10
**Decision:** The supported v1 `waveguide_1d` profile is `conical`.
**Status:** accepted
**Reason:** The word `linear` is ambiguous. `conical` clearly defines that the equivalent circular radius varies linearly with axial position.

## 2026-03-10
**Decision:** In v1, `waveguide_1d` with `profile: conical` covers both expanding / contracting conical sections and the cylindrical special case when `area_start == area_end`.
**Status:** accepted
**Reason:** This avoids unnecessary duplication of object types.

## 2026-03-10
**Decision:** The supported v1 radiator models are `infinite_baffle_piston`, `unflanged_piston`, and `flanged_piston`.
**Status:** accepted
**Reason:** These provide useful first-order termination coverage without reaching into full 3D radiation complexity.

## 2026-03-10
**Decision:** Radiators remain explicit separate elements rather than implicit endpoint options.
**Status:** accepted
**Reason:** This allows independent observation of driver, port, and line-mouth contributions, as well as later complex summation.

## 2026-03-10
**Decision:** Phase is not a separate observation type in v1. It is an exported attribute of complex-valued observations.
**Status:** accepted
**Reason:** This keeps the observation system cleaner and avoids redundant requests.

## 2026-03-10
**Decision:** v1 supports both individual radiator SPL observations and complex summed SPL observations.
**Status:** accepted
**Reason:** Driver and port contributions must be inspectable independently and also combined with phase interaction.

## 2026-03-10
**Decision:** The supported v1 observation types are `input_impedance`, `spl`, `spl_sum`, `cone_displacement`, `cone_velocity`, `element_volume_velocity`, `element_particle_velocity`, `node_pressure`, `line_profile`, and `group_delay`.
**Status:** accepted
**Reason:** This covers the main engineering outputs needed for classic enclosure work and line inspection.

## 2026-03-10
**Decision:** Group delay in v1 is computed from the unwrapped phase of a named complex observation using numerical differentiation with respect to frequency.
**Status:** accepted
**Reason:** This gives a clear and reproducible convention for exported results.

## 2026-03-10
**Decision:** The input parser will support a small controlled whitelist of convenient engineering units while normalizing everything internally to SI.
**Status:** accepted
**Reason:** Pure SI is clean internally, but common loudspeaker data is often expressed in cm, cm², liters, and ms.

## 2026-03-10
**Decision:** Unknown fields and missing required fields are hard errors in v1.
**Status:** accepted
**Reason:** A strict schema is better for early validation and avoids silent mistakes.

## 2026-03-10
**Decision:** Ambient medium customization is deferred; v1 uses default air constants.
**Status:** accepted
**Reason:** This keeps the first solver contract smaller while preserving future extensibility.

## 2026-03-10
**Decision:** Freeze the v1 harmonic convention to \(e^{j\omega t}\).
**Status:** accepted
**Reason:** All impedances, coupling equations, phase, and group-delay definitions must share one sign convention.

## 2026-03-10
**Decision:** The v1 unknown vector is acoustic node pressures plus driver current and diaphragm velocity.
**Status:** accepted
**Reason:** This keeps acoustics node-based while making the single-driver electromechanical coupling explicit and easy to validate.

## 2026-03-10
**Decision:** In v1, `volume` is a one-node shunt acoustic compliance, `duct` is a lumped two-node acoustic inertance, and `waveguide_1d` is internally expanded into segmented uniform lossless line sections.
**Status:** accepted
**Reason:** These definitions are simple, implementable, and sufficient for the first validated solver kernel.

## 2026-03-10
**Decision:** `spl_sum` is defined as a complex pressure sum before dB conversion.
**Status:** accepted
**Reason:** Summing dB values is physically wrong and would make driver-port or multi-radiator interference impossible to represent correctly.

## 2026-03-10
**Decision:** `line_profile` is a first-class v1 validation target and must be reconstructed from the solved internal line states.
**Status:** accepted
**Reason:** Internal pressure and velocity inspection is one of the main motivations for the project and must not remain an undefined post-processing detail.

## 2026-03-10
**Decision:** The exact formula library for the supported radiator models is intentionally left open until explicitly pinned by validation-oriented review, but the solver contract already requires each radiator to provide both a one-port boundary impedance and an observation transfer relation.
**Status:** accepted
**Reason:** The implementation interface must be fixed now, while the exact radiation formulas still deserve adversarial review before coding.

## 2026-03-10
**Decision:** The v1 validation strategy is layered: parser and normalization first, primitive physics second, integrated reference models third, observations fourth, and numerical robustness throughout.
**Status:** accepted
**Reason:** This reduces the risk of debugging full examples while basic schema, sign, or normalization mistakes are still hidden underneath.

## 2026-03-10
**Decision:** At least one official `waveguide_1d` validation case must include a segment-refinement convergence study.
**Status:** accepted
**Reason:** The v1 conical line model relies on internal segmentation, so convergence under refinement is a release-critical correctness check.

## 2026-03-10
**Decision:** All acoustic node pressures are gauge pressures relative to ambient.
**Status:** accepted
**Reason:** This removes ambiguity in the nodal state definition and in reference-boundary interpretation.

## 2026-03-10
**Decision:** The exported sign convention for ordered element volume velocity is positive from `node_a` to `node_b`.
**Status:** accepted
**Reason:** This prevents observation-level ambiguity and forces consistent reporting across implementations.

## 2026-03-10
**Decision:** `waveguide_1d` endpoint flow and particle-velocity observations require explicit endpoint selection via `location: a | b`.
**Status:** accepted
**Reason:** A distributed two-port does not have a single unique endpoint flow quantity, so the observation API must state which local endpoint quantity is meant.

## 2026-03-10
**Decision:** `spl` is frozen in v1 as an on-axis far-field radiator observation with explicit distance input.
**Status:** accepted
**Reason:** This removes hidden default-angle ambiguity and keeps the first observation contract implementable.

## 2026-03-10
**Decision:** The default v1 drive convention is a real positive 2.83 V RMS source unless explicitly overridden.
**Status:** accepted
**Reason:** Example reproducibility requires a frozen source convention.

## 2026-03-10
**Decision:** The canonical-driver parser consistency check uses relative tolerance 5e-3 and absolute tolerance 1e-12 SI.
**Status:** accepted
**Reason:** Parser acceptance behavior must be reproducible and tolerant of normal engineering rounding without masking real inconsistency.

## 2026-03-10
**Decision:** Every acoustically connected component must have at least one valid shunt path to the pressure reference.
**Status:** accepted
**Reason:** This avoids floating acoustic subnetworks and singular matrix assembly.

## 2026-03-10
**Decision:** The coupled system matrix must be treated as a general complex matrix; no symmetry or Hermitian assumptions are allowed.
**Status:** accepted
**Reason:** The pressure-current-velocity block formulation is not guaranteed to preserve symmetry, and implementation must not accidentally choose the wrong solver class.

## 2026-03-10
**Decision:** Group delay uses a frozen discrete stencil: centered difference for interior points and one-sided difference at the sweep endpoints.
**Status:** accepted
**Reason:** Group-delay output must be numerically reproducible across implementations.

## 2026-03-10
**Decision:** The exact v1 radiator formulas are frozen in `docs/radiator_models.md`.
**Status:** accepted
**Reason:** Radiator behavior was the largest remaining correctness gap after the initial spec pass and had to be pinned before implementation.

## 2026-03-10
**Decision:** Freeze v1 reference-air constants to rho0 = 1.2041 kg/m^3 and c0 = 343.2 m/s.
**Status:** accepted
**Reason:** Numerical validation and reproducibility require fixed medium constants.

## 2026-03-10
**Decision:** Acoustic node identity is name-based, and multiple elements may connect the same node pair as parallel branches.
**Status:** accepted
**Reason:** This removes topology ambiguity and makes parallel-path assembly explicit.

## 2026-03-10
**Decision:** Acoustic nodes are ordered by first appearance after parser normalization, and elements are assembled in normalized input-file order.
**Status:** accepted
**Reason:** Deterministic ordering is required for reproducible assembly and debugging.

## 2026-03-10
**Decision:** There is no special user-declared ground node in v1; shunt elements connect implicitly to the pressure reference.
**Status:** accepted
**Reason:** The solver uses an implicit acoustic reference and should not overload ordinary node names with hidden behavior.

## 2026-03-10
**Decision:** Positive diaphragm velocity means motion toward the front side.
**Status:** accepted
**Reason:** The driver sign convention must be physically interpretable as well as algebraically frozen.

## 2026-03-10
**Decision:** Machine-readable complex observations export in Cartesian form by default.
**Status:** accepted
**Reason:** Cartesian export is unambiguous and avoids phase-wrap ambiguity in downstream tools.

## 2026-03-10
**Decision:** Exact DC is forbidden in the v1 solver; only strictly positive frequencies are valid.
**Status:** accepted
**Reason:** The frozen formulation contains 1/(j omega) terms and is not a DC formulation.

## 2026-03-10
**Decision:** The frozen default validation comparison rule for complex values uses rel_tol = 1e-6 and abs_tol = 1e-12.
**Status:** accepted
**Reason:** Validation outcomes must be reproducible across implementations.

## 2026-03-10
**Decision:** The frozen v1 segmentation rule for conical waveguide_1d elements uses midpoint area per subsegment.
**Status:** accepted
**Reason:** This removes the last remaining discretization ambiguity for the v1 line model.

## 2026-03-10
**Decision:** No undocumented damping or loss regularization may be injected to rescue singular or ill-conditioned models.
**Status:** accepted
**Reason:** Numerical failure must be reported honestly rather than hidden behind untracked physics changes.

