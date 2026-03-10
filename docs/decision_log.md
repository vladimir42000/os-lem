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
