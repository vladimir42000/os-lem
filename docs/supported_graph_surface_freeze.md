# Supported Graph Surface Freeze (v0.6.0)

## Status

This document freezes the truthful currently supported general graph/compiler surface for current 1D LEM physics.

It distinguishes explicitly between:
- the primitive core
- legal couplings
- generic graph capabilities justified by source truth
- recipe-specific recognized carriers
- caveats and non-promises

This freeze is a source-truth boundary. It is **not** a promise that arbitrary authored graphs beyond this boundary are supported.

## 1. Primitive inventory

### Exact primitive counts

Current low-level component primitive inventory:
- **1 driver primitive**
- **4 acoustic element primitives**
- **5 total low-level primitives** if the driver is counted

### Exact primitive list

#### Driver primitive
- `Driver`

#### Acoustic element primitives
- `VolumeElement`
- `DuctElement`
- `Waveguide1DElement`
- `RadiatorElement`

### Exact subtype counts

#### `waveguide_1d` profiles
- supported profile count: **1**
- supported profile list:
  - `conical`

#### radiator models
- supported radiator model count: **3**
- supported radiator model list:
  - `infinite_baffle_piston`
  - `flanged_piston`
  - `unflanged_piston`

## 2. Legal couplings

### Exact primitive-level legal couplings

#### Driver coupling
- legal form: `Driver(node_front, node_rear)`
- couples exactly **two acoustic nodes**
- explicit enforced rule:
  - `node_front != node_rear`

#### One-node shunt couplings
- `VolumeElement(node)`
- `RadiatorElement(node)`

These act as acoustic shunts from one node to reference.

#### Two-node branch couplings
- `DuctElement(node_a, node_b)`
- `Waveguide1DElement(node_a, node_b)`

These act as acoustic branches between two acoustic nodes.

### Exact topology legality rules enforced today

Current source truth explicitly enforces:
- driver front and rear nodes must differ
- every acoustic connected component must contain at least one shunt path to reference
- in current repo truth, shunt-to-reference means at least one:
  - `volume`
  - or `radiator`

### Exact caveat: currently not-explicitly-rejected branch self-loops

Current parser/topology validation does **not** clearly and explicitly reject:
- `duct.node_a == duct.node_b`
- `waveguide_1d.node_a == waveguide_1d.node_b`

Therefore:
- these forms are **not justified as supported authored usage**
- their non-rejection is a validation caveat, **not** a support claim

## 3. Generic graph capabilities currently justified by repo truth

The current generic graph/compiler surface supports the following at source level:
- one driver coupled to distinct front/rear acoustic nodes
- arbitrary mixes of shunt elements on acoustic nodes:
  - volumes
  - radiators
- arbitrary mixes of branch elements between acoustic nodes:
  - ducts
  - `waveguide_1d`
- true acoustic junctions at nodes with more than two incident branches
- parallel branch bundles between the same node pair

### Generic reusable graph/compiler entities
- `Driver`
- `VolumeElement`
- `DuctElement`
- `Waveguide1DElement`
- `RadiatorElement`
- `AcousticJunction`
- `ParallelBranchBundle`
- `AssembledElement`
- `AssembledSystem`

### What this generic surface **does** justify

Repo truth currently justifies:
- source-grounded use of the above primitives and couplings
- generic 1D nodal acoustic graph assembly using those primitives
- benchmark work and bounded recipe work that stays inside this primitive/coupling surface

## 4. Recipe-specific recognized carriers

These are recognized bounded topology / contract / observability carriers.

They are **not** new primitives.
They are **not** evidence that arbitrary authored graphs with similar shapes are fully supported generically.

### Exact count
- current recipe-specific recognized carrier count: **25**

### Current recognized carrier list
1. `BranchedHornSkeleton`
2. `DirectPlusBranchedRearPathSkeleton`
3. `DirectPlusBranchedRearPathContributionContract`
4. `DirectPlusSplitMergeRearPathSkeleton`
5. `DirectPlusSplitMergeRearPathContributionContract`
6. `DirectPlusBranchedSplitMergeRearPathSkeleton`
7. `DirectPlusBranchedSplitMergeRearPathFrontChamberThroatSideCouplingSkeleton`
8. `DirectPlusBranchedSplitMergeRearPathFrontChamberThroatSideContributionContract`
9. `DirectPlusBranchedSplitMergeRearPathContributionContract`
10. `RecombinationTopology`
11. `SplitMergeHornSkeleton`
12. `TappedDriverSkeleton`
13. `OffsetTapTopology`
14. `RearChamberTappedSkeleton`
15. `RearChamberPortInjectionTopology`
16. `ThroatChamberTopology`
17. `BlindThroatSideSegmentTopology`
18. `DriverFrontChamberTopology`
19. `FrontChamberThroatSideCouplingTopology`
20. `DirectFrontRadiationTopology`
21. `DualRadiatorTopology`
22. `BackLoadedHornSkeleton`
23. `FrontRearRadiationSumObservability`
24. `RearRadiationDelayPathObservability`
25. `FrontRearRadiationContributionObservability`

## 5. Explicit distinction: generic core vs recipe layer

### Generic graph/compiler surface
This is the truthful reusable source-grounded core:
- low-level primitives
- legal primitive couplings
- junction and parallel-bundle assembly behavior
- connected-component legality rule

### Recipe-specific recognized layer
This is the current bounded recognized-family layer:
- named topology skeletons
- named contribution / observability carriers
- bounded regression-friendly family recognition

## 6. Caveats and non-promises

### Explicit non-promises

Current repo truth does **not** yet justify promising:
- arbitrary authored graph support beyond the frozen primitive/coupling surface
- arbitrary multi-driver authored graphs
- support for unsupported branch self-loop authored forms
- unsupported physics outside the current 1D LEM surface
- treating recipe-recognized families as proof of fully generic authoring freedom for all similar graphs

### Multi-driver caveat

Current freeze does **not** elevate multi-driver arbitrary authored graphs to supported generic authoring status.
If future work needs that claim, it must be justified explicitly by repo truth.

### Unsupported-physics caveat

This freeze is limited to current 1D LEM physics as supported on the current source line.
It does not promise unsupported losses, unsupported higher-dimensional effects, or unsupported physics outside the present surface.

## 7. Practical authoring boundary

### What is safe to say today

It is truthful to say:
- the kernel has a real generic primitive/coupling core
- the kernel also has a recognized recipe layer above that core
- benchmark-led work may rely on this frozen distinction

### What is not yet safe to say today

It is **not** yet truthful to say:
- that arbitrary graph authoring is fully supported just because the primitive set exists
- that every non-self-contradictory graph made from these primitives is already a supported authored product surface
- that recipe-carried families automatically imply fully general authored equivalents

## 8. Freeze result

The truthful current repo boundary is therefore:
- **supported generically:** primitive core + legal couplings + generic junction/parallel graph assembly
- **supported but still recipe-carried:** recognized bounded topology / contract / observability families
- **not yet promised for authoring:** arbitrary authored graphs outside the explicit source-grounded supported surface
