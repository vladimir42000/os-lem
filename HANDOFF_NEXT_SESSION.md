# os-lem handoff for next session

Repository:
- GitHub repo: https://github.com/vladimir42000/os-lem
- Current implementation language: Python
- Python package name: `os_lem`
- CLI first, GUI later

Current phase:
- project foundation and specification phase
- no implementation yet
- v1 contract has now been frozen at the documentation level

Frozen v1 highlights:
- single-driver linear frequency-domain node-based solver
- user-facing driver modes:
  - `ts_classic`
  - `em_explicit`
- internal canonical driver form:
  - `Re`, `Le`, `Bl`, `Mms`, `Cms`, `Rms`, `Sd`
- user-facing acoustic element types:
  - `volume`
  - `duct`
  - `waveguide_1d`
  - `radiator`
- `side_branch` and `resonator` are not primitive types; they are built by topology
- v1 `waveguide_1d` profile:
  - `conical`
- v1 radiator models:
  - `infinite_baffle_piston`
  - `unflanged_piston`
  - `flanged_piston`
- observations:
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
- parser accepts a small whitelist of common engineering units and normalizes internally to SI
- unknown fields and missing required fields are hard errors

Updated docs in this package:
- `README.md`
- `docs/vision.md`
- `docs/architecture.md`
- `docs/decision_log.md`
- `docs/input_format.md`
- `docs/roadmap.md`

Recommended next repo steps:
1. add `docs/solver_math.md`
2. add `docs/validation_plan.md`
3. create canonical example files under `examples/`
4. only then start implementation skeleton in `src/os_lem/`
