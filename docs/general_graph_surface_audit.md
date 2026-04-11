# v0.6.0 General Graph Surface Audit

Status: source-level audit artifact only.

Intent:
- freeze the current truthful general graph/compiler surface for supported 1D LEM physics
- distinguish the primitive core from legal couplings, generic graph capability, and recipe-specific recognized families
- make explicit what current source truth does and does not justify about arbitrary graph authoring

Audit basis:
- working line used for this audit: `proof/poc3-blh-benchmark-pass1`
- observed head at handoff: `e8e994d`
- suite at handoff: `318 passed`
- source inspection basis: current `src/os_lem` inventory used for the source-grounded primitive/coupling reply that this artifact freezes

## 1. Primitive inventory

### 1.1 Exact low-level primitive counts

Current low-level component primitive count:
- total component primitives: **5**
- acoustic element primitives only: **4**
- driver primitives: **1**

Exact current primitive set:
1. `Driver`
2. `VolumeElement`
3. `DuctElement`
4. `Waveguide1DElement`
5. `RadiatorElement`

These are defined at normalized-model / source level and form the reusable primitive core.

### 1.2 Exact subtype counts

Current `waveguide_1d` profile subtype count:
- **1** supported profile
  - `conical`

Current radiator model subtype count:
- **3** supported models
  - `infinite_baffle_piston`
  - `flanged_piston`
  - `unflanged_piston`

No other low-level element families are present in the current primitive core.

## 2. Legal couplings

### 2.1 Exact primitive-level legal couplings

Current primitive-level legal couplings are:

#### Driver coupling
- legal form: one driver coupling exactly two acoustic nodes
- source shape: `Driver(node_front, node_rear)`
- explicit enforced rule:
  - `node_front != node_rear`

#### One-node shunt couplings
- `VolumeElement(node)`
- `RadiatorElement(node)`

These act as shunts from one acoustic node to acoustic reference.

#### Two-node branch couplings
- `DuctElement(node_a, node_b)`
- `Waveguide1DElement(node_a, node_b)`

These act as acoustic branches between two acoustic nodes.

### 2.2 Exact topology legality rules enforced today

Current explicit topology legality rules enforced in source:
- driver front and rear nodes must differ
- every acoustic connected component must contain at least one valid shunt path to reference, meaning at least one:
  - `VolumeElement`, or
  - `RadiatorElement`

This is the current hard validity boundary for assembled acoustic graph connectivity.

### 2.3 Exact caveat: forms not explicitly rejected today

The following branch self-loop forms are not currently clearly rejected by explicit topology validation:
- `DuctElement(node_a == node_b)`
- `Waveguide1DElement(node_a == node_b)`

This does **not** mean they are intended or semantically supported authoring forms.
It means only that current validation does not appear to carry an explicit rejection rule for them at parse/topology level.

So the truthful statement is:
- driver self-loop is explicitly rejected
- branch self-loop forms are currently not explicitly rejected
- branch self-loop forms therefore remain a source-level caveat, not a supported authoring promise

## 3. Generic graph capabilities

The current generic graph surface supported by source is a nodal acoustic graph built from the primitive core above.

### 3.1 Current generic capabilities

Current generic capabilities include:
- one driver coupled across two acoustic nodes
- arbitrary mixes of shunt elements on acoustic nodes:
  - volumes
  - radiators
- arbitrary mixes of branch elements between nodes:
  - ducts
  - waveguide_1d elements

### 3.2 True-junction capability

True junctions are generic today.

Current explicit assembled representation:
- `AcousticJunction`

Truthful meaning:
- one node may carry more than two incident branch elements
- this is part of the generic graph surface, not only a recipe trick

### 3.3 Parallel-branch capability

Parallel branches are generic today.

Current explicit assembled representation:
- `ParallelBranchBundle`

Truthful meaning:
- multiple branch elements may connect the same acoustic node pair
- this is part of the generic graph surface, not only a recipe trick

### 3.4 What this does and does not justify

What this **does** justify:
- the current kernel has a real generic nodal graph core for supported 1D LEM physics
- the core truthfully supports shunts, branches, junctions, and parallel branch bundles
- recognized recipes are built on top of that generic graph surface

What this **does not** justify:
- it does **not** justify claiming fully open arbitrary graph authoring as a stable supported user-facing surface
- it does **not** justify claiming every graph expressible by the primitive types has accepted semantic support
- it does **not** justify claiming every topologically valid graph already has an accepted benchmark or observability contract
- it does **not** justify treating source-permitted-but-unconstrained forms as production-safe authoring commitments

So the truthful boundary is:
- **generic graph core exists**
- **arbitrary graph authoring surface is not yet frozen as a stable public contract**

## 4. Recipe-specific recognized families

Recipe-specific recognized families are named, bounded topology / contract / observability carriers layered on top of the generic primitive graph core.

They are **not** new low-level primitives.
They are **not** evidence of a separate solver family for each case.
They are bounded recognized subgraph families carried explicitly for validation, observability, and stable family semantics.

### 4.1 Exact recognized-family count

Current recipe-specific recognized-family count:
- **25**

### 4.2 Exact recognized-family inventory

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

### 4.3 Truthful architectural distinction

Current truthful architectural distinction is:
- **primitive core** = low-level reusable components and legal primitive couplings
- **generic graph capability** = junctions / parallel branches / nodal composition on that primitive core
- **recipe layer** = named bounded topology / contract / observability carriers recognized on top of that core

This distinction must remain explicit in future authoring-surface work.

## Bottom-line audit statement

Current repo truth supports the following bounded claim:
- os-lem today has a real generic 1D acoustic graph core for the currently supported primitive inventory
- current source also carries a recipe-specific recognized-family layer above that core
- the existence of the generic graph core does **not** yet justify claiming an unrestricted stable arbitrary-graph authoring surface

This artifact is therefore the truthful baseline for any future work on:
- authoring-surface expansion
- compiler-surface exposure
- recipe-to-generic unification claims
- graph UI or external graph contract work
