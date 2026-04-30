# v0.9.0 acoustic graph IR for accepted 1D topologies

## 1. Milestone identity

Milestone name:

```text
v0.9.0 — bounded acoustic graph IR and compiler for accepted 1D loudspeaker topologies
```

This specification defines the first bounded os-lem acoustic graph IR contract for accepted 1D loudspeaker topologies. It is a specification-only step. It does not implement the graph compiler, does not change solver behavior, and does not change topology behavior.

The purpose of v0.9.0 is model-construction and consumption discipline, not new solver physics. The accepted solver and validation work already shows that os-lem can represent useful 1D loudspeaker cases when semantic mapping is hand-controlled. The remaining problem is that consumption still depends too much on case-specific mapping modules, reference helpers, one-off parity callables, and repeated semantic translation work.

The intended v0.9.0 flow is:

```text
user / template / Studio / optimizer
→ os-lem acoustic graph IR
→ graph validator
→ graph compiler
→ existing os-lem model/system
→ existing solver
→ stable result object
```

The acoustic graph IR is the canonical model-construction truth. Akabak syntax, HornResp syntax, UI templates, optimizer proposals, or handwritten Python dictionaries may later translate into graph IR, but they must not become the canonical model in this milestone.

## 2. Graph IR purpose

The graph IR is a human-authored and machine-authored intermediate representation for accepted 1D acoustic loudspeaker topologies. It must be expressible as YAML, JSON, or a Python dictionary without loss of meaning.

The first graph IR is intended to provide a shared consumption target for future templates, optimizer work, Studio work, tests, and case-specific reference definitions. It is not an arbitrary graph engine. It is a bounded representation for accepted 1D acoustic topologies that can be validated, compiled, and compared against existing hand-mapped os-lem reference cases.

The graph IR must preserve three boundaries:

1. authored intent, where a user, template, or import process states the intended acoustic topology;
2. validated graph truth, where os-lem accepts or rejects the model-construction semantics explicitly;
3. compiled solver model truth, where the existing os-lem model/system and solver execute the already-accepted physics path.

No graph IR consumer is allowed to silently guess topology meaning, source position, radiation convention, units, or SPL observable names.

## 3. Node model

A graph node represents an acoustic pressure node in the 1D network unless explicitly marked otherwise.

Each node must have:

- `id`: unique string within the graph;
- optional `label`: human-readable name;
- optional `metadata`: non-authoritative descriptive information.

Node IDs are stable semantic identifiers, not array indices. A compiler may assign internal indices, but those indices must not replace graph node identity in diagnostics or validation messages.

Duplicate node IDs are invalid. Elements may connect only to declared node IDs. A graph with an element connection to an unknown node is invalid. A graph with an unused node may be accepted only if the validator classifies it as harmless metadata or emits a warning; it must not silently alter topology.

Special external or reference nodes may be introduced later only by explicit specification. For this first spec, normal acoustic pressure nodes are sufficient for the accepted GDN13 offset-driver TQWT anchor.

## 4. Element model

Each graph element must have:

- `id`: unique string within the graph;
- `type`: known primitive element type;
- `nodes`: ordered node connection list with primitive-specific meaning;
- `parameters`: primitive-specific numeric and enumerated values;
- `units`: explicit units for dimensional values unless the primitive defines a canonical unit;
- optional `metadata`: non-authoritative provenance or labels.

Element IDs must be unique. Element type names must be known. Unknown element types are rejected. Required fields must be present. Numeric fields must be finite. Positive physical quantities such as length, area, volume, resistance, inductance, mass, and compliance must use valid positive values unless the primitive explicitly permits zero.

Element output and diagnostic names must be stable and unambiguous. An element may expose diagnostic output names, but those names must not conflict with global result fields such as `spl_total_diagnostic`, `spl_mouth`, or `zin_complex_ohm`.

## 5. Required initial primitive element types

The first IR covers only bounded primitives needed for accepted 1D loudspeaker cases.

### 5.1 `electrodynamic_driver`

Purpose: represent the electrical/acoustic driver transducer with explicit front and rear acoustic nodes.

Required fields:

- `id`
- `type: electrodynamic_driver`
- `nodes.front`
- `nodes.rear`
- `parameters.Sd`
- `parameters.Bl`
- `parameters.Cms`
- `parameters.Rms`
- `parameters.Mmd`
- `parameters.Re`
- `parameters.Le`

Required units:

- `Sd`: area, canonical internal interpretation in square meters;
- `Bl`: Tm;
- `Cms`: m/N;
- `Rms`: mechanical resistance in SI-compatible units used by the existing driver normalization path;
- `Mmd`: kg, with grams accepted only through explicit unit conversion;
- `Re`: ohm;
- `Le`: H, with mH accepted only through explicit unit conversion.

Compilation target: existing driver and coupled acoustic/electrical model path.

Unsupported options in the first spec:

- multi-coil drivers;
- nonlinear driver parameters;
- continuous driver position search;
- ambiguous front/rear node inference.

### 5.2 `horn_or_duct_segment`

Purpose: represent a 1D acoustic segment between two acoustic pressure nodes.

Required fields:

- `id`
- `type: horn_or_duct_segment`
- `nodes.start`
- `nodes.end`
- `parameters.length`
- `parameters.area_start`
- `parameters.area_end`
- `parameters.profile`

Required units:

- `length`: m or cm, canonical internal interpretation in meters;
- `area_start`, `area_end`: m² or cm², canonical internal interpretation in square meters.

Accepted initial profile names:

- `conical`
- `exponential`
- `tractrix`
- `hyperbolic`
- `parabolic`
- `lecleach`

Compilation target: existing segmented 1D waveguide/horn model discipline.

Unsupported options in the first spec:

- free-form area curves;
- arbitrary user-defined flare functions;
- 3D bends as physical geometry;
- automatic subdivision rules that change validation meaning silently.

### 5.3 `closed_acoustic_termination`

Purpose: represent a closed acoustic termination or bounded closed stub endpoint when a segment is terminated at a closed end.

Required fields:

- `id`
- `type: closed_acoustic_termination`
- `nodes.node`

Optional fields:

- `parameters.compliance` or chamber parameters may be introduced only where already supported by existing model/system behavior.

Compilation target: existing closed acoustic termination or chamber representation where available.

Unsupported options in the first spec:

- lossy wall models;
- porous termination;
- automatic chamber inference from labels.

### 5.4 `radiation_load`

Purpose: represent acoustic radiation from a graph node to an external acoustic radiation space.

Required fields:

- `id`
- `type: radiation_load`
- `nodes.node`
- `parameters.radiation_space`

Accepted initial `radiation_space` values:

- `2pi`

Later values may be specified only by explicit future contract.

Compilation target: existing radiation load representation and diagnostic SPL output path.

Unsupported options in the first spec:

- automatic radiation-space guessing;
- hidden distance/reference-pressure changes;
- broad directivity model selection;
- free-field/full-space substitution unless explicitly specified.

## 6. Units

The graph IR must reject unit ambiguity. A dimensional value may be represented as a number only when the field's canonical unit is explicitly specified by the primitive schema. Otherwise the value must carry a unit.

Supported first-spec units:

- length: `m`, `cm`; canonical internal interpretation: `m`;
- area: `m2`, `m^2`, `cm2`, `cm^2`; canonical internal interpretation: `m2`;
- volume: `m3`, `m^3`, `liter`, `liters`, `L`; canonical internal interpretation: `m3`;
- frequency: `Hz`;
- resistance: `ohm`;
- inductance: `H`, `mH`; canonical internal interpretation: `H`;
- mass for driver `Mmd`: `kg`, `g`; canonical internal interpretation: `kg`;
- compliance for driver `Cms`: `m/N`.

Unit strings not listed here are invalid in the first graph IR contract. Missing units are invalid where canonical units are not explicitly implied by the field schema. Mixed dimensional units inside one field are invalid.

## 7. Driver front/rear convention

The `electrodynamic_driver` primitive has exactly two acoustic nodes:

- `front`: the driver front acoustic node;
- `rear`: the driver rear acoustic node.

The electrical input convention follows the existing os-lem driver sign and impedance convention. The graph IR does not redefine driver physics. It only makes front/rear acoustic connectivity explicit.

A front acoustic load connects to `nodes.front`. A rear acoustic load connects to `nodes.rear`. A tapped or offset-driver TQWT case must not express the driver by a continuous position coordinate unless a later contract explicitly introduces such a primitive. It must express the driver by named graph node connectivity.

For the accepted GDN13 offset-driver TQWT case:

- the driver/source tap is at S2;
- S2 is the shared acoustic node between the rear closed stub and the forward/open line;
- the rear driver side is connected to the rear closed-stub side at S2 according to the accepted hand-mapped case interpretation;
- the forward/open line also begins at S2 and radiates at S3.

The exact compiled sign and coupling behavior must reproduce the accepted hand-mapped GDN13 result before the graph compiler becomes a general consumption path.

## 8. Radiation convention

A `radiation_load` element attaches to an acoustic node and states the radiation space explicitly.

The first accepted value is:

```yaml
radiation_space: 2pi
```

For a horn or TQWT mouth, `radiation_load` at the mouth node means that node radiates into the specified half-space. For the GDN13 anchor, S3 is the mouth node and uses 2π radiation.

Driver/front radiation may be exposed diagnostically only if the existing solver result object already supports it. Diagnostic output names must remain explicit. The graph IR must not create an ambiguous generic SPL field.

## 9. Output observables

The compiled result object must use stable named outputs. The first expected names are:

- `frequency_hz`
- `zin_complex_ohm`
- `spl_total_diagnostic`
- `spl_mouth`
- `spl_driver_front_diagnostic`, where available
- `warnings`
- `unsupported_feature_diagnostics`

SPL output naming must avoid ambiguity. A field named only `spl` is not sufficient for graph compiler validation. When comparing to external references such as HornResp, the comparison target must name both the external reference column and the os-lem observable. For the accepted GDN13 case, HornResp SPL column is compared against `spl_total_diagnostic`; `spl_mouth` is explicitly rejected as the HornResp SPL comparator.

Warnings and unsupported-feature diagnostics must be machine-readable. The compiler must not silently substitute unsupported behavior.

## 10. Graph validation rules

The graph validator must reject or warn before compilation. Required first-spec checks include:

- unique graph node IDs;
- unique graph element IDs;
- known element types only;
- required fields present;
- valid node references for every element connection;
- finite numeric parameter values;
- positive lengths, areas, volumes, masses, compliances, resistances, and inductances where required;
- known units only;
- valid profile names only;
- valid radiation convention only;
- exactly defined driver front and rear nodes;
- no silently inferred driver source position;
- no silently inferred radiation load;
- unsupported graph structures rejected explicitly;
- no silent fallback to guessed topology.

The validator may allow non-authoritative metadata. Metadata must not change compiled topology or physics.

## 11. Graph-to-existing-model compilation target

At specification level, graph IR compiles to the existing os-lem model/system path. This does not imply a solver-core rewrite.

The first compiler target should reproduce accepted `model_dict` behavior where possible. Where the existing solver path uses another internal object or system representation, the graph compiler must still preserve the same semantics and result fields.

The graph compiler must be validated against existing hand-mapped reference cases before becoming a general consumption path. The first required validation anchor is the accepted GDN13 offset-driver TQWT case.

## 12. First validation anchor: GDN13 offset-driver TQWT

The first required validation anchor is:

```text
graph-defined GDN13 offset-driver TQWT must reproduce the accepted hand-mapped GDN13 offset TQWT result.
```

Accepted GDN13 graph interpretation:

- driver/source tap at S2;
- rear closed stub:
  - S1 = 96.00 cm²
  - S2 = 98.06 cm²
  - length = 55.80 cm
- forward/open line:
  - S2 = 98.06 cm²
  - S3 = 102.00 cm²
  - length = 106.46 cm
- profile: `parabolic`
- S3 mouth radiation: `2pi`
- accepted driver parameters:
  - Sd = 82.00 cm²
  - Bl = 6.16 Tm
  - Cms = 1.01E-03 m/N
  - Rms = 0.49
  - Mmd = 8.50 g
  - Le = 1.00 mH
  - Re = 6.50 ohm

Validation target:

- graph-generated result must reproduce the accepted hand-mapped GDN13 result;
- low-frequency SPL comparison uses `spl_total_diagnostic`;
- mouth-only SPL remains rejected as the HornResp SPL comparator;
- impedance result remains aligned with accepted reference;
- full-band SPL parity is not claimed by this anchor unless separately established by later validation.

This anchor uses accepted 64f8dbb/d2e429c GDN13 interpretation and low-frequency parity meaning as the semantic baseline for future graph compiler validation.

## 13. Unsupported features and explicit non-goals

This specification does not authorize:

- graph compiler implementation;
- arbitrary graph engine behavior;
- topology optimization;
- optimizer topology mutation;
- Studio redesign;
- Akabak parser;
- HornResp importer;
- full Akabak/HornResp replacement claim;
- solver-core rewrite;
- public promotion;
- uncontrolled primitive expansion;
- resonator/general branch growth unless later explicitly specified;
- arbitrary free-form expansion functions;
- continuous source-position semantics;
- multiple resonator-slot semantics;
- new acoustic primitive implementation;
- new parity claim.

This spec is only the contract for the bounded graph IR direction and its first validation anchor.

## 14. Future extension path

Future work may be separately authorized to build on this IR contract:

- templates may later generate graph IR;
- Studio may later emit graph IR;
- optimizer may later mutate graph IR under explicit constraints;
- Akabak or HornResp importers may later translate into graph IR;
- graph compiler implementation may later compile validated graph IR into the existing os-lem model/system.

None of these implementation tracks are opened by this patch. Any future extension must preserve the same authority boundary: graph IR is canonical model-construction truth, the graph validator rejects unsupported semantics, the graph compiler targets the existing solver path, and result observables remain explicitly named.
