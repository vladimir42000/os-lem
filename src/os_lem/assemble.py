"""Minimal coupled assembly scaffolding for Session 6.

This module does not yet build the final complex system matrix.
Its job in Patch 1 is only to transform a validated NormalizedModel into a
deterministic assembled representation that later solver stages can consume.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .errors import ValidationError
from .model import NormalizedModel


ElementKind = Literal["volume", "duct", "radiator", "waveguide_1d"]


@dataclass(slots=True, frozen=True)
class AcousticJunction:
    """Deterministic true-junction bundle at one interior acoustic node.

    This is the next bounded topology opening for v0.5.0: one acoustic node may
    carry more than two incident branch elements. The solver already stamps the
    individual branches directly into the nodal matrix; this structure makes the
    supported true-junction case explicit in assembled topology introspection.
    """

    node: int
    node_name: str
    incident_element_ids: tuple[str, ...]
    incident_element_kinds: tuple[ElementKind, ...]


@dataclass(slots=True, frozen=True)
class ParallelBranchBundle:
    """Deterministic parallel-branch bundle between one acoustic node pair.

    This is the bounded split/recombine topology opening for v0.5.0: multiple
    branch elements may connect the same two acoustic nodes and are treated as a
    single assembled bundle for topology introspection while the solver continues
    to stamp the individual branch admittances directly into the nodal matrix.
    """

    node_a: int
    node_b: int
    node_names: tuple[str, str]
    element_ids: tuple[str, ...]
    element_kinds: tuple[ElementKind, ...]


@dataclass(slots=True, frozen=True)
class BranchedHornSkeleton:
    """One bounded horn-like branching skeleton carried by the assembled system.

    Supported in this patch: exactly one stem branch from the driver rear node
    into a three-branch acoustic junction, followed by two branch legs that each
    terminate at a leaf mouth node carrying exactly one radiator.

    This is intentionally not a general graph framework. It only makes one real
    branched horn-like topology explicit so the current repo-native solver path
    can exercise and validate it end to end.
    """

    rear_node: int
    rear_node_name: str
    junction_node: int
    junction_node_name: str
    stem_element_id: str
    stem_element_kind: ElementKind
    branch_element_ids: tuple[str, str]
    branch_element_kinds: tuple[ElementKind, ElementKind]
    mouth_nodes: tuple[int, int]
    mouth_node_names: tuple[str, str]
    mouth_radiator_ids: tuple[str, str]


@dataclass(slots=True, frozen=True)
class RecombinationTopology:
    """One bounded recombination topology carried by the assembled system.

    Supported in this patch: exactly two upstream branch legs between the same
    split and merge nodes, followed by one shared downstream exit branch to one
    leaf mouth node carrying exactly one radiator.

    This keeps the opening narrow and explicit. It is not a general graph
    engine; it only records the first real merge-into-shared-exit case needed
    for tapped-horn-class topology growth.
    """

    split_node: int
    split_node_name: str
    merge_node: int
    merge_node_name: str
    upstream_bundle_element_ids: tuple[str, str]
    upstream_bundle_element_kinds: tuple[ElementKind, ElementKind]
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str




@dataclass(slots=True, frozen=True)
class SplitMergeHornSkeleton:
    """One bounded dual-junction split/merge horn-like skeleton.

    Supported in this patch: exactly one stem branch from the driver rear node
    into a split junction, exactly two parallel waveguide legs between that
    split junction and a merge junction, then one shared exit branch to a leaf
    mouth node carrying exactly one radiator.

    This keeps the opening narrow and explicit. It is not a general graph
    engine; it only records one minimal split/merge horn-like path needed for
    tapped-horn-class topology growth.
    """

    rear_node: int
    rear_node_name: str
    split_node: int
    split_node_name: str
    merge_node: int
    merge_node_name: str
    stem_element_id: str
    stem_element_kind: ElementKind
    leg_element_ids: tuple[str, str]
    leg_element_kinds: tuple[ElementKind, ElementKind]
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str


@dataclass(slots=True, frozen=True)
class TappedDriverSkeleton:
    """One bounded tapped-driver skeleton carried by the assembled system.

    Supported in this patch: exactly one split/merge horn skeleton where the
    single driver rear couples at the upstream rear node and the single driver
    front is tapped directly into the merge junction. The merge junction then
    feeds one shared downstream exit branch to one leaf mouth radiator.

    This keeps the opening narrow and explicit. It is not a general tapped-horn
    framework; it only records one real tapped-driver topology case that the
    current solver path can already exercise end to end.
    """

    rear_node: int
    rear_node_name: str
    split_node: int
    split_node_name: str
    merge_node: int
    merge_node_name: str
    tapped_node: int
    tapped_node_name: str
    stem_element_id: str
    stem_element_kind: ElementKind
    leg_element_ids: tuple[str, str]
    leg_element_kinds: tuple[ElementKind, ElementKind]
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str


@dataclass(slots=True, frozen=True)
class OffsetTapTopology:
    """One bounded offset-tap topology carried by the assembled system.

    Supported in this patch: exactly one stem branch from the driver rear node
    into a split junction, one direct main leg to a merge junction, one tapped
    side leg split into upstream and downstream waveguides with the driver front
    node coupled at the interior tap node, then one shared downstream exit
    branch to a leaf mouth node carrying exactly one radiator.

    This keeps the opening narrow and explicit. It is not a general graph
    engine; it only records one minimal offset-tap horn path needed for more
    realistic tapped-horn-class topology growth while preserving the older
    tapped_driver_skeleton surface as a backward-compatible subset.
    """

    rear_node: int
    rear_node_name: str
    split_node: int
    split_node_name: str
    tap_node: int
    tap_node_name: str
    merge_node: int
    merge_node_name: str
    stem_element_id: str
    stem_element_kind: ElementKind
    main_leg_element_id: str
    main_leg_element_kind: ElementKind
    tapped_upstream_element_id: str
    tapped_upstream_element_kind: ElementKind
    tapped_downstream_element_id: str
    tapped_downstream_element_kind: ElementKind
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str


@dataclass(slots=True, frozen=True)
class RearChamberTappedSkeleton:
    """One bounded rear-chamber tapped horn-like skeleton.

    Supported in this patch: exactly one rear chamber volume on the driver rear
    node behind one offset-tap horn path. The single driver rear couples into
    that rear chamber node, the single driver front couples at an interior tap
    node on the side leg, and the path then merges into one shared downstream
    exit branch and one mouth radiator.

    This keeps the opening narrow and explicit. It is not a general rear-volume
    graph framework; it only records one minimally more physical tapped-horn-
    class skeleton on top of the already opened offset-tap topology.
    """

    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    split_node: int
    split_node_name: str
    tap_node: int
    tap_node_name: str
    merge_node: int
    merge_node_name: str
    stem_element_id: str
    stem_element_kind: ElementKind
    main_leg_element_id: str
    main_leg_element_kind: ElementKind
    tapped_upstream_element_id: str
    tapped_upstream_element_kind: ElementKind
    tapped_downstream_element_id: str
    tapped_downstream_element_kind: ElementKind
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str


@dataclass(slots=True, frozen=True)
class RearChamberPortInjectionTopology:
    """One bounded rear-chamber port-injection tapped topology.

    Supported in this patch: exactly one rear chamber volume on the driver rear
    node, one explicit rear-port injection branch from that rear chamber node to
    one intermediate injection node, one stem branch from the injection node to
    a split junction, then one offset-tap horn path that merges into one shared
    downstream exit branch and one mouth radiator.

    This keeps the opening narrow and explicit. It is not a general tapped-horn
    graph framework; it only records one first explicit rear-port injection case
    on top of the already opened rear-chamber tapped and offset-tap paths.
    """

    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    injection_node: int
    injection_node_name: str
    port_injection_element_id: str
    port_injection_element_kind: ElementKind
    stem_element_id: str
    stem_element_kind: ElementKind
    split_node: int
    split_node_name: str
    tap_node: int
    tap_node_name: str
    merge_node: int
    merge_node_name: str
    main_leg_element_id: str
    main_leg_element_kind: ElementKind
    tapped_upstream_element_id: str
    tapped_upstream_element_kind: ElementKind
    tapped_downstream_element_id: str
    tapped_downstream_element_kind: ElementKind
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str


@dataclass(slots=True, frozen=True)
class ThroatChamberTopology:
    """One bounded rear-port-injected throat-chamber tapped topology.

    Supported in this patch: exactly one rear chamber volume on the driver rear
    node, one explicit rear-port injection branch to an intermediate injection
    node, one dedicated throat chamber volume on a distinct throat node reached
    through one throat-entry branch, then one stem branch into an offset-tap
    horn path that merges into one shared downstream exit branch and one mouth
    radiator.

    This keeps the opening narrow and explicit. It is not a general tapped-horn
    graph framework; it only records one first dedicated throat-chamber case on
    top of the already opened rear-port injection and rear-chamber tapped paths.
    """

    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    injection_node: int
    injection_node_name: str
    port_injection_element_id: str
    port_injection_element_kind: ElementKind
    throat_node: int
    throat_node_name: str
    throat_chamber_element_id: str
    throat_chamber_element_kind: ElementKind
    throat_entry_element_id: str
    throat_entry_element_kind: ElementKind
    stem_element_id: str
    stem_element_kind: ElementKind
    split_node: int
    split_node_name: str
    tap_node: int
    tap_node_name: str
    merge_node: int
    merge_node_name: str
    main_leg_element_id: str
    main_leg_element_kind: ElementKind
    tapped_upstream_element_id: str
    tapped_upstream_element_kind: ElementKind
    tapped_downstream_element_id: str
    tapped_downstream_element_kind: ElementKind
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str

@dataclass(slots=True, frozen=True)
class BlindThroatSideSegmentTopology:
    """One bounded throat-chamber topology with one blind throat-side segment.

    Supported in this patch: exactly one rear chamber volume on the driver rear
    node, one explicit rear-port injection branch to an intermediate injection
    node, one dedicated throat chamber volume on a distinct throat node, one
    blind throat-side waveguide segment terminating at a blind leaf node, then
    one stem branch into an offset-tap horn path that merges into one shared
    downstream exit branch and one mouth radiator.

    This keeps the opening narrow and explicit. It is not a general tapped-horn
    graph framework; it only records one first dedicated blind throat-side
    segment case on top of the already opened throat-chamber path.
    """

    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    injection_node: int
    injection_node_name: str
    port_injection_element_id: str
    port_injection_element_kind: ElementKind
    throat_node: int
    throat_node_name: str
    throat_chamber_element_id: str
    throat_chamber_element_kind: ElementKind
    throat_entry_element_id: str
    throat_entry_element_kind: ElementKind
    blind_node: int
    blind_node_name: str
    blind_segment_element_id: str
    blind_segment_element_kind: ElementKind
    stem_element_id: str
    stem_element_kind: ElementKind
    split_node: int
    split_node_name: str
    tap_node: int
    tap_node_name: str
    merge_node: int
    merge_node_name: str
    main_leg_element_id: str
    main_leg_element_kind: ElementKind
    tapped_upstream_element_id: str
    tapped_upstream_element_kind: ElementKind
    tapped_downstream_element_id: str
    tapped_downstream_element_kind: ElementKind
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str


@dataclass(slots=True, frozen=True)
class DriverFrontChamberTopology:
    """One bounded driver-front-chamber throat-side topology.

    Supported in this patch: exactly one rear chamber volume on the driver rear
    node, one explicit rear-port injection branch to an intermediate injection
    node, one dedicated throat chamber volume on a distinct throat node, one
    blind throat-side waveguide segment terminating at a blind leaf node, one
    dedicated driver-front chamber volume on a distinct front node, one front
    coupling branch from that front chamber into the interior tap node, then one
    stem branch into the tapped horn path that merges into one shared downstream
    exit branch and one mouth radiator.

    This keeps the opening narrow and explicit. It is not a general tapped-horn
    graph framework; it only records one first dedicated driver-front chamber
    case on top of the already opened blind throat-side path.
    """

    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    injection_node: int
    injection_node_name: str
    port_injection_element_id: str
    port_injection_element_kind: ElementKind
    throat_node: int
    throat_node_name: str
    throat_chamber_element_id: str
    throat_chamber_element_kind: ElementKind
    throat_entry_element_id: str
    throat_entry_element_kind: ElementKind
    blind_node: int
    blind_node_name: str
    blind_segment_element_id: str
    blind_segment_element_kind: ElementKind
    front_chamber_node: int
    front_chamber_node_name: str
    front_chamber_element_id: str
    front_chamber_element_kind: ElementKind
    front_coupling_element_id: str
    front_coupling_element_kind: ElementKind
    stem_element_id: str
    stem_element_kind: ElementKind
    split_node: int
    split_node_name: str
    tap_node: int
    tap_node_name: str
    merge_node: int
    merge_node_name: str
    main_leg_element_id: str
    main_leg_element_kind: ElementKind
    tapped_upstream_element_id: str
    tapped_upstream_element_kind: ElementKind
    tapped_downstream_element_id: str
    tapped_downstream_element_kind: ElementKind
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str


@dataclass(slots=True, frozen=True)
class FrontChamberThroatSideCouplingTopology:
    """One bounded front-chamber / throat-side coupling topology.

    Supported in this patch: exactly one rear chamber volume on the driver rear
    node, one explicit rear-port injection branch to an intermediate injection
    node, one dedicated throat chamber volume on a distinct throat node, one
    blind throat-side path split into an upstream and downstream segment, one
    dedicated driver-front chamber volume on a distinct front node, one front
    coupling branch from that front chamber into the interior throat-side
    coupling node, then one stem branch into the tapped horn path that merges
    into one shared downstream exit branch and one mouth radiator.

    This keeps the opening narrow and explicit. It is not a general tapped-horn
    graph framework; it only records one first dedicated front-chamber /
    throat-side coupling case on top of the already opened driver-front chamber
    and blind throat-side path.
    """

    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    injection_node: int
    injection_node_name: str
    port_injection_element_id: str
    port_injection_element_kind: ElementKind
    throat_node: int
    throat_node_name: str
    throat_chamber_element_id: str
    throat_chamber_element_kind: ElementKind
    throat_entry_element_id: str
    throat_entry_element_kind: ElementKind
    throat_side_node: int
    throat_side_node_name: str
    blind_upstream_element_id: str
    blind_upstream_element_kind: ElementKind
    blind_node: int
    blind_node_name: str
    blind_downstream_element_id: str
    blind_downstream_element_kind: ElementKind
    front_chamber_node: int
    front_chamber_node_name: str
    front_chamber_element_id: str
    front_chamber_element_kind: ElementKind
    front_coupling_element_id: str
    front_coupling_element_kind: ElementKind
    stem_element_id: str
    stem_element_kind: ElementKind
    split_node: int
    split_node_name: str
    tap_node: int
    tap_node_name: str
    merge_node: int
    merge_node_name: str
    main_leg_element_id: str
    main_leg_element_kind: ElementKind
    tapped_upstream_element_id: str
    tapped_upstream_element_kind: ElementKind
    tapped_downstream_element_id: str
    tapped_downstream_element_kind: ElementKind
    shared_exit_element_id: str
    shared_exit_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str



@dataclass(slots=True, frozen=True)
class DirectFrontRadiationTopology:
    """One bounded direct-front-radiation topology.

    Supported in this patch: exactly one single driver with one direct front
    radiator on the driver front node, one rear chamber volume on the driver
    rear node, one explicit rear-port injection branch to an intermediate
    injection node, one dedicated throat chamber volume on a distinct throat
    node, one blind throat-side path split into upstream and downstream
    segments, then one direct rear horn path to one leaf mouth node carrying
    exactly one mouth radiator.

    This keeps the opening narrow and explicit. It is not a general graph
    framework; it only records one first direct-front-radiation motif on top of
    the already opened rear-path / chamber / throat-side vocabulary.
    """

    front_node: int
    front_node_name: str
    front_radiator_id: str
    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    injection_node: int
    injection_node_name: str
    port_injection_element_id: str
    port_injection_element_kind: ElementKind
    throat_node: int
    throat_node_name: str
    throat_chamber_element_id: str
    throat_chamber_element_kind: ElementKind
    throat_entry_element_id: str
    throat_entry_element_kind: ElementKind
    throat_side_node: int
    throat_side_node_name: str
    blind_upstream_element_id: str
    blind_upstream_element_kind: ElementKind
    blind_node: int
    blind_node_name: str
    blind_downstream_element_id: str
    blind_downstream_element_kind: ElementKind
    rear_path_element_id: str
    rear_path_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str



@dataclass(slots=True, frozen=True)
class DualRadiatorTopology:
    """One bounded dual-radiator topology in one shared assembly.

    Supported in this patch: exactly one single driver with one explicit direct
    front radiator on the driver front node and one explicit rear-path mouth
    radiator on the leaf mouth node, while the rear acoustic path still carries
    one rear chamber, one rear-port injection branch, one throat chamber, one
    blind throat-side path, and one rear horn path to the mouth.

    This keeps the opening narrow and explicit. It is not a broad graph
    framework; it only records one first two-radiator-in-one-assembly motif on
    top of the already opened direct-front-radiation path.
    """

    front_node: int
    front_node_name: str
    front_radiator_id: str
    rear_node: int
    rear_node_name: str
    rear_chamber_element_id: str
    rear_chamber_element_kind: ElementKind
    injection_node: int
    injection_node_name: str
    port_injection_element_id: str
    port_injection_element_kind: ElementKind
    throat_node: int
    throat_node_name: str
    throat_chamber_element_id: str
    throat_chamber_element_kind: ElementKind
    throat_entry_element_id: str
    throat_entry_element_kind: ElementKind
    throat_side_node: int
    throat_side_node_name: str
    blind_upstream_element_id: str
    blind_upstream_element_kind: ElementKind
    blind_node: int
    blind_node_name: str
    blind_downstream_element_id: str
    blind_downstream_element_kind: ElementKind
    rear_path_element_id: str
    rear_path_element_kind: ElementKind
    mouth_node: int
    mouth_node_name: str
    mouth_radiator_id: str

@dataclass(slots=True, frozen=True)
class AssembledElement:
    """Topology-resolved element entry.

    For shunt elements, node_b is None.
    For branch elements, node_a and node_b are both integers.
    """

    id: str
    kind: ElementKind
    node_a: int
    node_b: int | None
    payload: object


@dataclass(slots=True, frozen=True)
class AssembledSystem:
    """Deterministic assembled representation of the supported acoustic network."""

    node_order: tuple[str, ...]
    node_index: dict[str, int]
    driver_front_index: int
    driver_rear_index: int
    shunt_elements: tuple[AssembledElement, ...]
    branch_elements: tuple[AssembledElement, ...]
    parallel_branch_bundles: tuple[ParallelBranchBundle, ...]
    acoustic_junctions: tuple[AcousticJunction, ...]
    branched_horn_skeletons: tuple[BranchedHornSkeleton, ...]
    recombination_topologies: tuple[RecombinationTopology, ...]
    split_merge_horn_skeletons: tuple[SplitMergeHornSkeleton, ...]
    tapped_driver_skeletons: tuple[TappedDriverSkeleton, ...]
    offset_tap_topologies: tuple[OffsetTapTopology, ...]
    rear_chamber_tapped_skeletons: tuple[RearChamberTappedSkeleton, ...]
    rear_chamber_port_injection_topologies: tuple[RearChamberPortInjectionTopology, ...]
    throat_chamber_topologies: tuple[ThroatChamberTopology, ...]
    blind_throat_side_segment_topologies: tuple[BlindThroatSideSegmentTopology, ...]
    driver_front_chamber_topologies: tuple[DriverFrontChamberTopology, ...]
    front_chamber_throat_side_coupling_topologies: tuple[FrontChamberThroatSideCouplingTopology, ...]
    direct_front_radiation_topologies: tuple[DirectFrontRadiationTopology, ...]
    dual_radiator_topologies: tuple[DualRadiatorTopology, ...]


def _require_known_node(node: str, node_index: dict[str, int], *, context: str) -> int:
    try:
        return node_index[node]
    except KeyError as exc:
        raise ValidationError(f"{context} refers to unknown node {node!r}") from exc


def _collect_parallel_branch_bundles(
    branch_elements: list[AssembledElement],
    node_order: tuple[str, ...],
) -> tuple[ParallelBranchBundle, ...]:
    grouped: dict[tuple[int, int], list[AssembledElement]] = {}

    for element in branch_elements:
        assert element.node_b is not None
        key = (min(element.node_a, element.node_b), max(element.node_a, element.node_b))
        grouped.setdefault(key, []).append(element)

    bundles: list[ParallelBranchBundle] = []
    for (node_a, node_b), elements in grouped.items():
        if len(elements) < 2:
            continue
        bundles.append(
            ParallelBranchBundle(
                node_a=node_a,
                node_b=node_b,
                node_names=(node_order[node_a], node_order[node_b]),
                element_ids=tuple(element.id for element in elements),
                element_kinds=tuple(element.kind for element in elements),
            )
        )

    return tuple(bundles)


def _collect_acoustic_junctions(
    branch_elements: list[AssembledElement],
    node_order: tuple[str, ...],
) -> tuple[AcousticJunction, ...]:
    incident: dict[int, list[AssembledElement]] = {}

    for element in branch_elements:
        incident.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        incident.setdefault(element.node_b, []).append(element)

    junctions: list[AcousticJunction] = []
    for node, elements in incident.items():
        if len(elements) < 3:
            continue
        junctions.append(
            AcousticJunction(
                node=node,
                node_name=node_order[node],
                incident_element_ids=tuple(element.id for element in elements),
                incident_element_kinds=tuple(element.kind for element in elements),
            )
        )

    return tuple(junctions)


def _other_branch_node(element: AssembledElement, node: int) -> int:
    assert element.node_b is not None
    if element.node_a == node:
        return element.node_b
    if element.node_b == node:
        return element.node_a
    raise ValueError(f"element {element.id!r} is not incident on node index {node}")


def _collect_branched_horn_skeletons(
    *,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[BranchedHornSkeleton, ...]:
    branch_by_id = {element.id: element for element in branch_elements}

    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    skeletons: list[BranchedHornSkeleton] = []

    for junction in acoustic_junctions:
        if len(junction.incident_element_ids) != 3:
            continue

        incident_elements = [branch_by_id[element_id] for element_id in junction.incident_element_ids]
        stem_candidates = [
            element
            for element in incident_elements
            if _other_branch_node(element, junction.node) == driver_rear_index
        ]
        if len(stem_candidates) != 1:
            continue

        stem = stem_candidates[0]
        branch_legs = [element for element in incident_elements if element.id != stem.id]
        if len(branch_legs) != 2:
            continue

        mouth_nodes: list[int] = []
        mouth_node_names: list[str] = []
        mouth_radiator_ids: list[str] = []
        supported = True

        for branch in branch_legs:
            mouth_node = _other_branch_node(branch, junction.node)
            if len(branch_incidence.get(mouth_node, [])) != 1:
                supported = False
                break
            mouth_radiators = radiators_by_node.get(mouth_node, [])
            if len(mouth_radiators) != 1:
                supported = False
                break
            mouth_nodes.append(mouth_node)
            mouth_node_names.append(node_order[mouth_node])
            mouth_radiator_ids.append(mouth_radiators[0].id)

        if not supported:
            continue

        skeletons.append(
            BranchedHornSkeleton(
                rear_node=driver_rear_index,
                rear_node_name=node_order[driver_rear_index],
                junction_node=junction.node,
                junction_node_name=junction.node_name,
                stem_element_id=stem.id,
                stem_element_kind=stem.kind,
                branch_element_ids=(branch_legs[0].id, branch_legs[1].id),
                branch_element_kinds=(branch_legs[0].kind, branch_legs[1].kind),
                mouth_nodes=(mouth_nodes[0], mouth_nodes[1]),
                mouth_node_names=(mouth_node_names[0], mouth_node_names[1]),
                mouth_radiator_ids=(mouth_radiator_ids[0], mouth_radiator_ids[1]),
            )
        )

    return tuple(skeletons)


def _collect_recombination_topologies(
    *,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    parallel_branch_bundles: tuple[ParallelBranchBundle, ...],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[RecombinationTopology, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    recombinations: list[RecombinationTopology] = []

    for bundle in parallel_branch_bundles:
        if len(bundle.element_ids) != 2:
            continue

        bundle_id_set = set(bundle.element_ids)
        topology: RecombinationTopology | None = None

        for merge_node, split_node in ((bundle.node_a, bundle.node_b), (bundle.node_b, bundle.node_a)):
            junction = junction_by_node.get(merge_node)
            if junction is None or len(junction.incident_element_ids) != 3:
                continue

            incident_ids = tuple(junction.incident_element_ids)
            if not bundle_id_set.issubset(incident_ids):
                continue

            shared_exit_ids = [element_id for element_id in incident_ids if element_id not in bundle_id_set]
            if len(shared_exit_ids) != 1:
                continue

            shared_exit = branch_by_id[shared_exit_ids[0]]
            mouth_node = _other_branch_node(shared_exit, merge_node)
            if len(branch_incidence.get(mouth_node, [])) != 1:
                continue

            mouth_radiators = radiators_by_node.get(mouth_node, [])
            if len(mouth_radiators) != 1:
                continue

            topology = RecombinationTopology(
                split_node=split_node,
                split_node_name=node_order[split_node],
                merge_node=merge_node,
                merge_node_name=node_order[merge_node],
                upstream_bundle_element_ids=(bundle.element_ids[0], bundle.element_ids[1]),
                upstream_bundle_element_kinds=(bundle.element_kinds[0], bundle.element_kinds[1]),
                shared_exit_element_id=shared_exit.id,
                shared_exit_element_kind=shared_exit.kind,
                mouth_node=mouth_node,
                mouth_node_name=node_order[mouth_node],
                mouth_radiator_id=mouth_radiators[0].id,
            )
            break

        if topology is not None:
            recombinations.append(topology)

    return tuple(recombinations)


def _collect_split_merge_horn_skeletons(
    *,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    parallel_branch_bundles: tuple[ParallelBranchBundle, ...],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[SplitMergeHornSkeleton, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    skeletons: list[SplitMergeHornSkeleton] = []

    for bundle in parallel_branch_bundles:
        if len(bundle.element_ids) != 2:
            continue
        if any(kind != "waveguide_1d" for kind in bundle.element_kinds):
            continue

        node_a, node_b = bundle.node_a, bundle.node_b
        junction_a = junction_by_node.get(node_a)
        junction_b = junction_by_node.get(node_b)
        if junction_a is None or junction_b is None:
            continue
        if len(junction_a.incident_element_ids) != 3 or len(junction_b.incident_element_ids) != 3:
            continue

        bundle_ids = set(bundle.element_ids)
        other_a_ids = [eid for eid in junction_a.incident_element_ids if eid not in bundle_ids]
        other_b_ids = [eid for eid in junction_b.incident_element_ids if eid not in bundle_ids]
        if len(other_a_ids) != 1 or len(other_b_ids) != 1:
            continue

        other_a = branch_by_id[other_a_ids[0]]
        other_b = branch_by_id[other_b_ids[0]]

        candidates = [
            (node_a, junction_a.node_name, other_a, node_b, junction_b.node_name, other_b),
            (node_b, junction_b.node_name, other_b, node_a, junction_a.node_name, other_a),
        ]

        for split_node, split_name, stem, merge_node, merge_name, shared_exit in candidates:
            if stem.kind != "waveguide_1d" or shared_exit.kind != "waveguide_1d":
                continue
            if _other_branch_node(stem, split_node) != driver_rear_index:
                continue

            mouth_node = _other_branch_node(shared_exit, merge_node)
            if len(branch_incidence.get(mouth_node, [])) != 1:
                continue

            mouth_radiators = radiators_by_node.get(mouth_node, [])
            if len(mouth_radiators) != 1:
                continue

            skeletons.append(
                SplitMergeHornSkeleton(
                    rear_node=driver_rear_index,
                    rear_node_name=node_order[driver_rear_index],
                    split_node=split_node,
                    split_node_name=split_name,
                    merge_node=merge_node,
                    merge_node_name=merge_name,
                    stem_element_id=stem.id,
                    stem_element_kind=stem.kind,
                    leg_element_ids=(bundle.element_ids[0], bundle.element_ids[1]),
                    leg_element_kinds=(bundle.element_kinds[0], bundle.element_kinds[1]),
                    shared_exit_element_id=shared_exit.id,
                    shared_exit_element_kind=shared_exit.kind,
                    mouth_node=mouth_node,
                    mouth_node_name=node_order[mouth_node],
                    mouth_radiator_id=mouth_radiators[0].id,
                )
            )
            break

    return tuple(skeletons)


def _collect_tapped_driver_skeletons(
    *,
    driver_front_index: int,
    shunt_elements: list[AssembledElement],
    split_merge_horn_skeletons: tuple[SplitMergeHornSkeleton, ...],
) -> tuple[TappedDriverSkeleton, ...]:
    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    skeletons: list[TappedDriverSkeleton] = []
    for skeleton in split_merge_horn_skeletons:
        if driver_front_index != skeleton.merge_node:
            continue
        if radiators_by_node.get(driver_front_index):
            continue
        skeletons.append(
            TappedDriverSkeleton(
                rear_node=skeleton.rear_node,
                rear_node_name=skeleton.rear_node_name,
                split_node=skeleton.split_node,
                split_node_name=skeleton.split_node_name,
                merge_node=skeleton.merge_node,
                merge_node_name=skeleton.merge_node_name,
                tapped_node=skeleton.merge_node,
                tapped_node_name=skeleton.merge_node_name,
                stem_element_id=skeleton.stem_element_id,
                stem_element_kind=skeleton.stem_element_kind,
                leg_element_ids=skeleton.leg_element_ids,
                leg_element_kinds=skeleton.leg_element_kinds,
                shared_exit_element_id=skeleton.shared_exit_element_id,
                shared_exit_element_kind=skeleton.shared_exit_element_kind,
                mouth_node=skeleton.mouth_node,
                mouth_node_name=skeleton.mouth_node_name,
                mouth_radiator_id=skeleton.mouth_radiator_id,
            )
        )

    return tuple(skeletons)




def _collect_offset_tap_topologies(
    *,
    driver_front_index: int,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[OffsetTapTopology, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    topologies: list[OffsetTapTopology] = []

    for split_junction in acoustic_junctions:
        if len(split_junction.incident_element_ids) != 3:
            continue

        incident = [branch_by_id[element_id] for element_id in split_junction.incident_element_ids]
        stem_candidates = [
            element
            for element in incident
            if element.kind == "waveguide_1d" and _other_branch_node(element, split_junction.node) == driver_rear_index
        ]
        if len(stem_candidates) != 1:
            continue

        stem = stem_candidates[0]
        non_stem = [element for element in incident if element.id != stem.id]
        if len(non_stem) != 2:
            continue

        for tapped_upstream in non_stem:
            if tapped_upstream.kind != "waveguide_1d":
                continue

            tap_node = _other_branch_node(tapped_upstream, split_junction.node)
            if tap_node != driver_front_index:
                continue
            if radiators_by_node.get(tap_node):
                continue

            tap_incident = branch_incidence.get(tap_node, [])
            if len(tap_incident) != 2:
                continue

            tapped_downstream_candidates = [
                element for element in tap_incident if element.id != tapped_upstream.id and element.kind == "waveguide_1d"
            ]
            if len(tapped_downstream_candidates) != 1:
                continue

            tapped_downstream = tapped_downstream_candidates[0]
            merge_node = _other_branch_node(tapped_downstream, tap_node)
            merge_junction = junction_by_node.get(merge_node)
            if merge_junction is None or len(merge_junction.incident_element_ids) != 3:
                continue

            main_leg_candidates = [
                element
                for element in non_stem
                if element.id != tapped_upstream.id
                and element.kind == "waveguide_1d"
                and _other_branch_node(element, split_junction.node) == merge_node
            ]
            if len(main_leg_candidates) != 1:
                continue
            main_leg = main_leg_candidates[0]

            merge_ids = set(merge_junction.incident_element_ids)
            if main_leg.id not in merge_ids or tapped_downstream.id not in merge_ids:
                continue

            shared_exit_ids = [
                element_id
                for element_id in merge_junction.incident_element_ids
                if element_id not in {main_leg.id, tapped_downstream.id}
            ]
            if len(shared_exit_ids) != 1:
                continue

            shared_exit = branch_by_id[shared_exit_ids[0]]
            if shared_exit.kind != "waveguide_1d":
                continue

            mouth_node = _other_branch_node(shared_exit, merge_node)
            if mouth_node in {driver_rear_index, driver_front_index, split_junction.node}:
                continue
            if len(branch_incidence.get(mouth_node, [])) != 1:
                continue

            mouth_radiators = radiators_by_node.get(mouth_node, [])
            if len(mouth_radiators) != 1:
                continue

            topologies.append(
                OffsetTapTopology(
                    rear_node=driver_rear_index,
                    rear_node_name=node_order[driver_rear_index],
                    split_node=split_junction.node,
                    split_node_name=split_junction.node_name,
                    tap_node=tap_node,
                    tap_node_name=node_order[tap_node],
                    merge_node=merge_node,
                    merge_node_name=node_order[merge_node],
                    stem_element_id=stem.id,
                    stem_element_kind=stem.kind,
                    main_leg_element_id=main_leg.id,
                    main_leg_element_kind=main_leg.kind,
                    tapped_upstream_element_id=tapped_upstream.id,
                    tapped_upstream_element_kind=tapped_upstream.kind,
                    tapped_downstream_element_id=tapped_downstream.id,
                    tapped_downstream_element_kind=tapped_downstream.kind,
                    shared_exit_element_id=shared_exit.id,
                    shared_exit_element_kind=shared_exit.kind,
                    mouth_node=mouth_node,
                    mouth_node_name=node_order[mouth_node],
                    mouth_radiator_id=mouth_radiators[0].id,
                )
            )
            break

    return tuple(topologies)


def _collect_rear_chamber_tapped_skeletons(
    *,
    shunt_elements: list[AssembledElement],
    offset_tap_topologies: tuple[OffsetTapTopology, ...],
) -> tuple[RearChamberTappedSkeleton, ...]:
    volumes_by_node: dict[int, list[AssembledElement]] = {}
    radiators_by_node: dict[int, list[AssembledElement]] = {}

    for element in shunt_elements:
        if element.kind == "volume":
            volumes_by_node.setdefault(element.node_a, []).append(element)
        elif element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    skeletons: list[RearChamberTappedSkeleton] = []
    for topology in offset_tap_topologies:
        rear_volumes = volumes_by_node.get(topology.rear_node, [])
        if len(rear_volumes) != 1:
            continue
        if radiators_by_node.get(topology.rear_node):
            continue

        rear_chamber = rear_volumes[0]
        skeletons.append(
            RearChamberTappedSkeleton(
                rear_node=topology.rear_node,
                rear_node_name=topology.rear_node_name,
                rear_chamber_element_id=rear_chamber.id,
                rear_chamber_element_kind=rear_chamber.kind,
                split_node=topology.split_node,
                split_node_name=topology.split_node_name,
                tap_node=topology.tap_node,
                tap_node_name=topology.tap_node_name,
                merge_node=topology.merge_node,
                merge_node_name=topology.merge_node_name,
                stem_element_id=topology.stem_element_id,
                stem_element_kind=topology.stem_element_kind,
                main_leg_element_id=topology.main_leg_element_id,
                main_leg_element_kind=topology.main_leg_element_kind,
                tapped_upstream_element_id=topology.tapped_upstream_element_id,
                tapped_upstream_element_kind=topology.tapped_upstream_element_kind,
                tapped_downstream_element_id=topology.tapped_downstream_element_id,
                tapped_downstream_element_kind=topology.tapped_downstream_element_kind,
                shared_exit_element_id=topology.shared_exit_element_id,
                shared_exit_element_kind=topology.shared_exit_element_kind,
                mouth_node=topology.mouth_node,
                mouth_node_name=topology.mouth_node_name,
                mouth_radiator_id=topology.mouth_radiator_id,
            )
        )

    return tuple(skeletons)



def _collect_rear_chamber_port_injection_topologies(
    *,
    driver_front_index: int,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[RearChamberPortInjectionTopology, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    volumes_by_node: dict[int, list[AssembledElement]] = {}
    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "volume":
            volumes_by_node.setdefault(element.node_a, []).append(element)
        elif element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    topologies: list[RearChamberPortInjectionTopology] = []

    rear_volumes = volumes_by_node.get(driver_rear_index, [])
    if len(rear_volumes) != 1:
        return ()
    if radiators_by_node.get(driver_rear_index):
        return ()

    rear_incident = branch_incidence.get(driver_rear_index, [])
    if len(rear_incident) != 1:
        return ()

    rear_port = rear_incident[0]
    if rear_port.kind != "waveguide_1d":
        return ()

    injection_node = _other_branch_node(rear_port, driver_rear_index)
    if injection_node == driver_front_index:
        return ()
    if radiators_by_node.get(injection_node):
        return ()

    injection_incident = branch_incidence.get(injection_node, [])
    if len(injection_incident) != 2:
        return ()

    stem_candidates = [
        element
        for element in injection_incident
        if element.id != rear_port.id and element.kind == "waveguide_1d"
    ]
    if len(stem_candidates) != 1:
        return ()

    stem = stem_candidates[0]
    split_node = _other_branch_node(stem, injection_node)
    split_junction = junction_by_node.get(split_node)
    if split_junction is None or len(split_junction.incident_element_ids) != 3:
        return ()

    incident = [branch_by_id[element_id] for element_id in split_junction.incident_element_ids]
    if stem.id not in {element.id for element in incident}:
        return ()

    non_stem = [element for element in incident if element.id != stem.id]
    if len(non_stem) != 2:
        return ()

    for tapped_upstream in non_stem:
        if tapped_upstream.kind != "waveguide_1d":
            continue

        tap_node = _other_branch_node(tapped_upstream, split_node)
        if tap_node != driver_front_index:
            continue
        if radiators_by_node.get(tap_node):
            continue

        tap_incident = branch_incidence.get(tap_node, [])
        if len(tap_incident) != 2:
            continue

        tapped_downstream_candidates = [
            element
            for element in tap_incident
            if element.id != tapped_upstream.id and element.kind == "waveguide_1d"
        ]
        if len(tapped_downstream_candidates) != 1:
            continue

        tapped_downstream = tapped_downstream_candidates[0]
        merge_node = _other_branch_node(tapped_downstream, tap_node)
        merge_junction = junction_by_node.get(merge_node)
        if merge_junction is None or len(merge_junction.incident_element_ids) != 3:
            continue

        main_leg_candidates = [
            element
            for element in non_stem
            if element.id != tapped_upstream.id
            and element.kind == "waveguide_1d"
            and _other_branch_node(element, split_node) == merge_node
        ]
        if len(main_leg_candidates) != 1:
            continue
        main_leg = main_leg_candidates[0]

        merge_ids = set(merge_junction.incident_element_ids)
        if main_leg.id not in merge_ids or tapped_downstream.id not in merge_ids:
            continue

        shared_exit_ids = [
            element_id
            for element_id in merge_junction.incident_element_ids
            if element_id not in {main_leg.id, tapped_downstream.id}
        ]
        if len(shared_exit_ids) != 1:
            continue

        shared_exit = branch_by_id[shared_exit_ids[0]]
        if shared_exit.kind != "waveguide_1d":
            continue

        mouth_node = _other_branch_node(shared_exit, merge_node)
        if mouth_node in {driver_rear_index, driver_front_index, injection_node, split_node}:
            continue
        if len(branch_incidence.get(mouth_node, [])) != 1:
            continue

        mouth_radiators = radiators_by_node.get(mouth_node, [])
        if len(mouth_radiators) != 1:
            continue

        rear_chamber = rear_volumes[0]
        topologies.append(
            RearChamberPortInjectionTopology(
                rear_node=driver_rear_index,
                rear_node_name=node_order[driver_rear_index],
                rear_chamber_element_id=rear_chamber.id,
                rear_chamber_element_kind=rear_chamber.kind,
                injection_node=injection_node,
                injection_node_name=node_order[injection_node],
                port_injection_element_id=rear_port.id,
                port_injection_element_kind=rear_port.kind,
                stem_element_id=stem.id,
                stem_element_kind=stem.kind,
                split_node=split_node,
                split_node_name=node_order[split_node],
                tap_node=tap_node,
                tap_node_name=node_order[tap_node],
                merge_node=merge_node,
                merge_node_name=node_order[merge_node],
                main_leg_element_id=main_leg.id,
                main_leg_element_kind=main_leg.kind,
                tapped_upstream_element_id=tapped_upstream.id,
                tapped_upstream_element_kind=tapped_upstream.kind,
                tapped_downstream_element_id=tapped_downstream.id,
                tapped_downstream_element_kind=tapped_downstream.kind,
                shared_exit_element_id=shared_exit.id,
                shared_exit_element_kind=shared_exit.kind,
                mouth_node=mouth_node,
                mouth_node_name=node_order[mouth_node],
                mouth_radiator_id=mouth_radiators[0].id,
            )
        )
        break

    return tuple(topologies)


def _collect_throat_chamber_topologies(
    *,
    driver_front_index: int,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[ThroatChamberTopology, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    volumes_by_node: dict[int, list[AssembledElement]] = {}
    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "volume":
            volumes_by_node.setdefault(element.node_a, []).append(element)
        elif element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    rear_volumes = volumes_by_node.get(driver_rear_index, [])
    if len(rear_volumes) != 1:
        return ()
    if radiators_by_node.get(driver_rear_index):
        return ()

    rear_incident = branch_incidence.get(driver_rear_index, [])
    if len(rear_incident) != 1:
        return ()
    rear_port = rear_incident[0]
    if rear_port.kind != "waveguide_1d":
        return ()

    injection_node = _other_branch_node(rear_port, driver_rear_index)
    if injection_node == driver_front_index:
        return ()
    if radiators_by_node.get(injection_node) or volumes_by_node.get(injection_node):
        return ()

    injection_incident = branch_incidence.get(injection_node, [])
    if len(injection_incident) != 2:
        return ()

    throat_entry_candidates = [
        element
        for element in injection_incident
        if element.id != rear_port.id and element.kind == "waveguide_1d"
    ]
    if len(throat_entry_candidates) != 1:
        return ()
    throat_entry = throat_entry_candidates[0]

    throat_node = _other_branch_node(throat_entry, injection_node)
    if throat_node in {driver_rear_index, driver_front_index, injection_node}:
        return ()
    if radiators_by_node.get(throat_node):
        return ()
    throat_volumes = volumes_by_node.get(throat_node, [])
    if len(throat_volumes) != 1:
        return ()

    throat_incident = branch_incidence.get(throat_node, [])
    if len(throat_incident) != 2:
        return ()

    stem_candidates = [
        element
        for element in throat_incident
        if element.id != throat_entry.id and element.kind == "waveguide_1d"
    ]
    if len(stem_candidates) != 1:
        return ()
    stem = stem_candidates[0]

    split_node = _other_branch_node(stem, throat_node)
    split_junction = junction_by_node.get(split_node)
    if split_junction is None or len(split_junction.incident_element_ids) != 3:
        return ()

    incident = [branch_by_id[element_id] for element_id in split_junction.incident_element_ids]
    if stem.id not in {element.id for element in incident}:
        return ()

    non_stem = [element for element in incident if element.id != stem.id]
    if len(non_stem) != 2:
        return ()

    topologies: list[ThroatChamberTopology] = []
    for tapped_upstream in non_stem:
        if tapped_upstream.kind != "waveguide_1d":
            continue

        tap_node = _other_branch_node(tapped_upstream, split_node)
        if tap_node != driver_front_index:
            continue
        if radiators_by_node.get(tap_node) or volumes_by_node.get(tap_node):
            continue

        tap_incident = branch_incidence.get(tap_node, [])
        if len(tap_incident) != 2:
            continue

        tapped_downstream_candidates = [
            element
            for element in tap_incident
            if element.id != tapped_upstream.id and element.kind == "waveguide_1d"
        ]
        if len(tapped_downstream_candidates) != 1:
            continue
        tapped_downstream = tapped_downstream_candidates[0]

        merge_node = _other_branch_node(tapped_downstream, tap_node)
        merge_junction = junction_by_node.get(merge_node)
        if merge_junction is None or len(merge_junction.incident_element_ids) != 3:
            continue

        main_leg_candidates = [
            element
            for element in non_stem
            if element.id != tapped_upstream.id
            and element.kind == "waveguide_1d"
            and _other_branch_node(element, split_node) == merge_node
        ]
        if len(main_leg_candidates) != 1:
            continue
        main_leg = main_leg_candidates[0]

        merge_ids = set(merge_junction.incident_element_ids)
        if main_leg.id not in merge_ids or tapped_downstream.id not in merge_ids:
            continue

        shared_exit_ids = [
            element_id
            for element_id in merge_junction.incident_element_ids
            if element_id not in {main_leg.id, tapped_downstream.id}
        ]
        if len(shared_exit_ids) != 1:
            continue
        shared_exit = branch_by_id[shared_exit_ids[0]]
        if shared_exit.kind != "waveguide_1d":
            continue

        mouth_node = _other_branch_node(shared_exit, merge_node)
        if mouth_node in {driver_rear_index, injection_node, throat_node, split_node, driver_front_index}:
            continue
        if len(branch_incidence.get(mouth_node, [])) != 1:
            continue

        mouth_radiators = radiators_by_node.get(mouth_node, [])
        if len(mouth_radiators) != 1:
            continue

        topologies.append(
            ThroatChamberTopology(
                rear_node=driver_rear_index,
                rear_node_name=node_order[driver_rear_index],
                rear_chamber_element_id=rear_volumes[0].id,
                rear_chamber_element_kind=rear_volumes[0].kind,
                injection_node=injection_node,
                injection_node_name=node_order[injection_node],
                port_injection_element_id=rear_port.id,
                port_injection_element_kind=rear_port.kind,
                throat_node=throat_node,
                throat_node_name=node_order[throat_node],
                throat_chamber_element_id=throat_volumes[0].id,
                throat_chamber_element_kind=throat_volumes[0].kind,
                throat_entry_element_id=throat_entry.id,
                throat_entry_element_kind=throat_entry.kind,
                stem_element_id=stem.id,
                stem_element_kind=stem.kind,
                split_node=split_node,
                split_node_name=node_order[split_node],
                tap_node=tap_node,
                tap_node_name=node_order[tap_node],
                merge_node=merge_node,
                merge_node_name=node_order[merge_node],
                main_leg_element_id=main_leg.id,
                main_leg_element_kind=main_leg.kind,
                tapped_upstream_element_id=tapped_upstream.id,
                tapped_upstream_element_kind=tapped_upstream.kind,
                tapped_downstream_element_id=tapped_downstream.id,
                tapped_downstream_element_kind=tapped_downstream.kind,
                shared_exit_element_id=shared_exit.id,
                shared_exit_element_kind=shared_exit.kind,
                mouth_node=mouth_node,
                mouth_node_name=node_order[mouth_node],
                mouth_radiator_id=mouth_radiators[0].id,
            )
        )
        break

    return tuple(topologies)


def _collect_blind_throat_side_segment_topologies(
    *,
    driver_front_index: int,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[BlindThroatSideSegmentTopology, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    volumes_by_node: dict[int, list[AssembledElement]] = {}
    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "volume":
            volumes_by_node.setdefault(element.node_a, []).append(element)
        elif element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    rear_volumes = volumes_by_node.get(driver_rear_index, [])
    if len(rear_volumes) != 1:
        return ()
    if radiators_by_node.get(driver_rear_index):
        return ()

    rear_incident = branch_incidence.get(driver_rear_index, [])
    if len(rear_incident) != 1:
        return ()
    rear_port = rear_incident[0]
    if rear_port.kind != "waveguide_1d":
        return ()

    injection_node = _other_branch_node(rear_port, driver_rear_index)
    if injection_node == driver_front_index:
        return ()
    if radiators_by_node.get(injection_node) or volumes_by_node.get(injection_node):
        return ()

    injection_incident = branch_incidence.get(injection_node, [])
    if len(injection_incident) != 2:
        return ()

    throat_entry_candidates = [
        element
        for element in injection_incident
        if element.id != rear_port.id and element.kind == "waveguide_1d"
    ]
    if len(throat_entry_candidates) != 1:
        return ()
    throat_entry = throat_entry_candidates[0]

    throat_node = _other_branch_node(throat_entry, injection_node)
    if throat_node in {driver_rear_index, driver_front_index, injection_node}:
        return ()
    if radiators_by_node.get(throat_node):
        return ()
    throat_volumes = volumes_by_node.get(throat_node, [])
    if len(throat_volumes) != 1:
        return ()

    throat_incident = branch_incidence.get(throat_node, [])
    if len(throat_incident) != 3:
        return ()

    remaining = [element for element in throat_incident if element.id != throat_entry.id and element.kind == "waveguide_1d"]
    if len(remaining) != 2:
        return ()

    topologies: list[BlindThroatSideSegmentTopology] = []
    for blind_segment in remaining:
        blind_node = _other_branch_node(blind_segment, throat_node)
        if blind_node in {driver_rear_index, injection_node, driver_front_index}:
            continue
        if len(branch_incidence.get(blind_node, [])) != 1:
            continue
        if radiators_by_node.get(blind_node) or volumes_by_node.get(blind_node):
            continue

        stem_candidates = [element for element in remaining if element.id != blind_segment.id]
        if len(stem_candidates) != 1:
            continue
        stem = stem_candidates[0]
        if stem.kind != "waveguide_1d":
            continue

        split_node = _other_branch_node(stem, throat_node)
        split_junction = junction_by_node.get(split_node)
        if split_junction is None or len(split_junction.incident_element_ids) != 3:
            continue

        incident = [branch_by_id[element_id] for element_id in split_junction.incident_element_ids]
        if stem.id not in {element.id for element in incident}:
            continue

        non_stem = [element for element in incident if element.id != stem.id]
        if len(non_stem) != 2:
            continue

        for tapped_upstream in non_stem:
            if tapped_upstream.kind != "waveguide_1d":
                continue

            tap_node = _other_branch_node(tapped_upstream, split_node)
            if tap_node != driver_front_index:
                continue
            if radiators_by_node.get(tap_node) or volumes_by_node.get(tap_node):
                continue

            tap_incident = branch_incidence.get(tap_node, [])
            if len(tap_incident) != 2:
                continue

            tapped_downstream_candidates = [
                element
                for element in tap_incident
                if element.id != tapped_upstream.id and element.kind == "waveguide_1d"
            ]
            if len(tapped_downstream_candidates) != 1:
                continue
            tapped_downstream = tapped_downstream_candidates[0]

            merge_node = _other_branch_node(tapped_downstream, tap_node)
            merge_junction = junction_by_node.get(merge_node)
            if merge_junction is None or len(merge_junction.incident_element_ids) != 3:
                continue

            main_leg_candidates = [
                element
                for element in non_stem
                if element.id != tapped_upstream.id
                and element.kind == "waveguide_1d"
                and _other_branch_node(element, split_node) == merge_node
            ]
            if len(main_leg_candidates) != 1:
                continue
            main_leg = main_leg_candidates[0]

            merge_ids = set(merge_junction.incident_element_ids)
            if main_leg.id not in merge_ids or tapped_downstream.id not in merge_ids:
                continue

            shared_exit_ids = [
                element_id
                for element_id in merge_junction.incident_element_ids
                if element_id not in {main_leg.id, tapped_downstream.id}
            ]
            if len(shared_exit_ids) != 1:
                continue
            shared_exit = branch_by_id[shared_exit_ids[0]]
            if shared_exit.kind != "waveguide_1d":
                continue

            mouth_node = _other_branch_node(shared_exit, merge_node)
            if mouth_node in {driver_rear_index, injection_node, throat_node, blind_node, split_node, driver_front_index}:
                continue
            if len(branch_incidence.get(mouth_node, [])) != 1:
                continue

            mouth_radiators = radiators_by_node.get(mouth_node, [])
            if len(mouth_radiators) != 1:
                continue

            topologies.append(
                BlindThroatSideSegmentTopology(
                    rear_node=driver_rear_index,
                    rear_node_name=node_order[driver_rear_index],
                    rear_chamber_element_id=rear_volumes[0].id,
                    rear_chamber_element_kind=rear_volumes[0].kind,
                    injection_node=injection_node,
                    injection_node_name=node_order[injection_node],
                    port_injection_element_id=rear_port.id,
                    port_injection_element_kind=rear_port.kind,
                    throat_node=throat_node,
                    throat_node_name=node_order[throat_node],
                    throat_chamber_element_id=throat_volumes[0].id,
                    throat_chamber_element_kind=throat_volumes[0].kind,
                    throat_entry_element_id=throat_entry.id,
                    throat_entry_element_kind=throat_entry.kind,
                    blind_node=blind_node,
                    blind_node_name=node_order[blind_node],
                    blind_segment_element_id=blind_segment.id,
                    blind_segment_element_kind=blind_segment.kind,
                    stem_element_id=stem.id,
                    stem_element_kind=stem.kind,
                    split_node=split_node,
                    split_node_name=node_order[split_node],
                    tap_node=tap_node,
                    tap_node_name=node_order[tap_node],
                    merge_node=merge_node,
                    merge_node_name=node_order[merge_node],
                    main_leg_element_id=main_leg.id,
                    main_leg_element_kind=main_leg.kind,
                    tapped_upstream_element_id=tapped_upstream.id,
                    tapped_upstream_element_kind=tapped_upstream.kind,
                    tapped_downstream_element_id=tapped_downstream.id,
                    tapped_downstream_element_kind=tapped_downstream.kind,
                    shared_exit_element_id=shared_exit.id,
                    shared_exit_element_kind=shared_exit.kind,
                    mouth_node=mouth_node,
                    mouth_node_name=node_order[mouth_node],
                    mouth_radiator_id=mouth_radiators[0].id,
                )
            )
            break
        if topologies:
            break

    return tuple(topologies)




def _collect_driver_front_chamber_topologies(
    *,
    driver_front_index: int,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[DriverFrontChamberTopology, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    volumes_by_node: dict[int, list[AssembledElement]] = {}
    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "volume":
            volumes_by_node.setdefault(element.node_a, []).append(element)
        elif element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    front_volumes = volumes_by_node.get(driver_front_index, [])
    if len(front_volumes) != 1:
        return ()
    if radiators_by_node.get(driver_front_index):
        return ()

    front_incident = branch_incidence.get(driver_front_index, [])
    if len(front_incident) != 1:
        return ()
    front_coupling = front_incident[0]
    if front_coupling.kind != "waveguide_1d":
        return ()

    rear_volumes = volumes_by_node.get(driver_rear_index, [])
    if len(rear_volumes) != 1:
        return ()
    if radiators_by_node.get(driver_rear_index):
        return ()

    rear_incident = branch_incidence.get(driver_rear_index, [])
    if len(rear_incident) != 1:
        return ()
    rear_port = rear_incident[0]
    if rear_port.kind != "waveguide_1d":
        return ()

    injection_node = _other_branch_node(rear_port, driver_rear_index)
    if injection_node in {driver_front_index}:
        return ()
    if radiators_by_node.get(injection_node) or volumes_by_node.get(injection_node):
        return ()

    injection_incident = branch_incidence.get(injection_node, [])
    if len(injection_incident) != 2:
        return ()

    throat_entry_candidates = [
        element
        for element in injection_incident
        if element.id != rear_port.id and element.kind == "waveguide_1d"
    ]
    if len(throat_entry_candidates) != 1:
        return ()
    throat_entry = throat_entry_candidates[0]

    throat_node = _other_branch_node(throat_entry, injection_node)
    if throat_node in {driver_rear_index, driver_front_index, injection_node}:
        return ()
    if radiators_by_node.get(throat_node):
        return ()
    throat_volumes = volumes_by_node.get(throat_node, [])
    if len(throat_volumes) != 1:
        return ()

    throat_incident = branch_incidence.get(throat_node, [])
    if len(throat_incident) != 3:
        return ()

    remaining = [
        element for element in throat_incident if element.id != throat_entry.id and element.kind == "waveguide_1d"
    ]
    if len(remaining) != 2:
        return ()

    topologies: list[DriverFrontChamberTopology] = []
    for blind_segment in remaining:
        blind_node = _other_branch_node(blind_segment, throat_node)
        if blind_node in {driver_rear_index, injection_node, driver_front_index}:
            continue
        if len(branch_incidence.get(blind_node, [])) != 1:
            continue
        if radiators_by_node.get(blind_node) or volumes_by_node.get(blind_node):
            continue

        stem_candidates = [element for element in remaining if element.id != blind_segment.id]
        if len(stem_candidates) != 1:
            continue
        stem = stem_candidates[0]
        if stem.kind != "waveguide_1d":
            continue

        split_node = _other_branch_node(stem, throat_node)
        split_junction = junction_by_node.get(split_node)
        if split_junction is None or len(split_junction.incident_element_ids) != 3:
            continue

        incident = [branch_by_id[element_id] for element_id in split_junction.incident_element_ids]
        if stem.id not in {element.id for element in incident}:
            continue

        non_stem = [element for element in incident if element.id != stem.id]
        if len(non_stem) != 2:
            continue

        front_tap_node = _other_branch_node(front_coupling, driver_front_index)

        for tapped_upstream in non_stem:
            if tapped_upstream.kind != "waveguide_1d":
                continue

            tap_node = _other_branch_node(tapped_upstream, split_node)
            if tap_node != front_tap_node or tap_node in {driver_front_index, driver_rear_index, injection_node, throat_node, blind_node}:
                continue
            if radiators_by_node.get(tap_node) or volumes_by_node.get(tap_node):
                continue

            tap_incident = branch_incidence.get(tap_node, [])
            if len(tap_incident) != 3:
                continue

            tapped_downstream_candidates = [
                element
                for element in tap_incident
                if element.id not in {tapped_upstream.id, front_coupling.id} and element.kind == "waveguide_1d"
            ]
            if len(tapped_downstream_candidates) != 1:
                continue
            tapped_downstream = tapped_downstream_candidates[0]

            merge_node = _other_branch_node(tapped_downstream, tap_node)
            merge_junction = junction_by_node.get(merge_node)
            if merge_junction is None or len(merge_junction.incident_element_ids) != 3:
                continue

            main_leg_candidates = [
                element
                for element in non_stem
                if element.id != tapped_upstream.id
                and element.kind == "waveguide_1d"
                and _other_branch_node(element, split_node) == merge_node
            ]
            if len(main_leg_candidates) != 1:
                continue
            main_leg = main_leg_candidates[0]

            merge_ids = set(merge_junction.incident_element_ids)
            if main_leg.id not in merge_ids or tapped_downstream.id not in merge_ids:
                continue

            shared_exit_ids = [
                element_id
                for element_id in merge_junction.incident_element_ids
                if element_id not in {main_leg.id, tapped_downstream.id}
            ]
            if len(shared_exit_ids) != 1:
                continue
            shared_exit = branch_by_id[shared_exit_ids[0]]
            if shared_exit.kind != "waveguide_1d":
                continue

            mouth_node = _other_branch_node(shared_exit, merge_node)
            if mouth_node in {driver_front_index, driver_rear_index, injection_node, throat_node, blind_node, split_node, tap_node}:
                continue
            if len(branch_incidence.get(mouth_node, [])) != 1:
                continue

            mouth_radiators = radiators_by_node.get(mouth_node, [])
            if len(mouth_radiators) != 1:
                continue

            topologies.append(
                DriverFrontChamberTopology(
                    rear_node=driver_rear_index,
                    rear_node_name=node_order[driver_rear_index],
                    rear_chamber_element_id=rear_volumes[0].id,
                    rear_chamber_element_kind=rear_volumes[0].kind,
                    injection_node=injection_node,
                    injection_node_name=node_order[injection_node],
                    port_injection_element_id=rear_port.id,
                    port_injection_element_kind=rear_port.kind,
                    throat_node=throat_node,
                    throat_node_name=node_order[throat_node],
                    throat_chamber_element_id=throat_volumes[0].id,
                    throat_chamber_element_kind=throat_volumes[0].kind,
                    throat_entry_element_id=throat_entry.id,
                    throat_entry_element_kind=throat_entry.kind,
                    blind_node=blind_node,
                    blind_node_name=node_order[blind_node],
                    blind_segment_element_id=blind_segment.id,
                    blind_segment_element_kind=blind_segment.kind,
                    front_chamber_node=driver_front_index,
                    front_chamber_node_name=node_order[driver_front_index],
                    front_chamber_element_id=front_volumes[0].id,
                    front_chamber_element_kind=front_volumes[0].kind,
                    front_coupling_element_id=front_coupling.id,
                    front_coupling_element_kind=front_coupling.kind,
                    stem_element_id=stem.id,
                    stem_element_kind=stem.kind,
                    split_node=split_node,
                    split_node_name=node_order[split_node],
                    tap_node=tap_node,
                    tap_node_name=node_order[tap_node],
                    merge_node=merge_node,
                    merge_node_name=node_order[merge_node],
                    main_leg_element_id=main_leg.id,
                    main_leg_element_kind=main_leg.kind,
                    tapped_upstream_element_id=tapped_upstream.id,
                    tapped_upstream_element_kind=tapped_upstream.kind,
                    tapped_downstream_element_id=tapped_downstream.id,
                    tapped_downstream_element_kind=tapped_downstream.kind,
                    shared_exit_element_id=shared_exit.id,
                    shared_exit_element_kind=shared_exit.kind,
                    mouth_node=mouth_node,
                    mouth_node_name=node_order[mouth_node],
                    mouth_radiator_id=mouth_radiators[0].id,
                )
            )
            break
        if topologies:
            break

    return tuple(topologies)



def _collect_direct_front_radiation_topologies(
    *,
    driver_front_index: int,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
) -> tuple[DirectFrontRadiationTopology, ...]:
    volumes_by_node: dict[int, list[AssembledElement]] = {}
    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "volume":
            volumes_by_node.setdefault(element.node_a, []).append(element)
        elif element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    front_radiators = radiators_by_node.get(driver_front_index, [])
    if len(front_radiators) != 1:
        return ()
    if volumes_by_node.get(driver_front_index):
        return ()
    if branch_incidence.get(driver_front_index):
        return ()

    rear_volumes = volumes_by_node.get(driver_rear_index, [])
    if len(rear_volumes) != 1:
        return ()
    if radiators_by_node.get(driver_rear_index):
        return ()

    rear_incident = branch_incidence.get(driver_rear_index, [])
    if len(rear_incident) != 1:
        return ()
    rear_port = rear_incident[0]
    if rear_port.kind != "waveguide_1d":
        return ()

    injection_node = _other_branch_node(rear_port, driver_rear_index)
    if injection_node == driver_front_index:
        return ()
    if radiators_by_node.get(injection_node) or volumes_by_node.get(injection_node):
        return ()

    injection_incident = branch_incidence.get(injection_node, [])
    if len(injection_incident) != 2:
        return ()
    throat_entry_candidates = [
        element
        for element in injection_incident
        if element.id != rear_port.id and element.kind == "waveguide_1d"
    ]
    if len(throat_entry_candidates) != 1:
        return ()
    throat_entry = throat_entry_candidates[0]

    throat_node = _other_branch_node(throat_entry, injection_node)
    if throat_node in {driver_rear_index, driver_front_index, injection_node}:
        return ()
    if radiators_by_node.get(throat_node):
        return ()
    throat_volumes = volumes_by_node.get(throat_node, [])
    if len(throat_volumes) != 1:
        return ()

    throat_incident = branch_incidence.get(throat_node, [])
    if len(throat_incident) != 3:
        return ()
    remaining = [element for element in throat_incident if element.id != throat_entry.id and element.kind == "waveguide_1d"]
    if len(remaining) != 2:
        return ()

    topologies: list[DirectFrontRadiationTopology] = []
    for blind_upstream in remaining:
        throat_side_node = _other_branch_node(blind_upstream, throat_node)
        if throat_side_node in {driver_rear_index, driver_front_index, injection_node, throat_node}:
            continue
        if radiators_by_node.get(throat_side_node) or volumes_by_node.get(throat_side_node):
            continue

        side_incident = branch_incidence.get(throat_side_node, [])
        if len(side_incident) != 2:
            continue
        blind_downstream_candidates = [
            element
            for element in side_incident
            if element.id != blind_upstream.id and element.kind == "waveguide_1d"
        ]
        if len(blind_downstream_candidates) != 1:
            continue
        blind_downstream = blind_downstream_candidates[0]

        blind_node = _other_branch_node(blind_downstream, throat_side_node)
        if blind_node in {driver_rear_index, driver_front_index, injection_node, throat_node, throat_side_node}:
            continue
        if len(branch_incidence.get(blind_node, [])) != 1:
            continue
        if radiators_by_node.get(blind_node) or volumes_by_node.get(blind_node):
            continue

        rear_path_candidates = [element for element in remaining if element.id != blind_upstream.id]
        if len(rear_path_candidates) != 1:
            continue
        rear_path = rear_path_candidates[0]
        if rear_path.kind != "waveguide_1d":
            continue

        mouth_node = _other_branch_node(rear_path, throat_node)
        if mouth_node in {driver_front_index, driver_rear_index, injection_node, throat_node, throat_side_node, blind_node}:
            continue
        if len(branch_incidence.get(mouth_node, [])) != 1:
            continue
        mouth_radiators = radiators_by_node.get(mouth_node, [])
        if len(mouth_radiators) != 1:
            continue
        if volumes_by_node.get(mouth_node):
            continue

        topologies.append(
            DirectFrontRadiationTopology(
                front_node=driver_front_index,
                front_node_name=node_order[driver_front_index],
                front_radiator_id=front_radiators[0].id,
                rear_node=driver_rear_index,
                rear_node_name=node_order[driver_rear_index],
                rear_chamber_element_id=rear_volumes[0].id,
                rear_chamber_element_kind=rear_volumes[0].kind,
                injection_node=injection_node,
                injection_node_name=node_order[injection_node],
                port_injection_element_id=rear_port.id,
                port_injection_element_kind=rear_port.kind,
                throat_node=throat_node,
                throat_node_name=node_order[throat_node],
                throat_chamber_element_id=throat_volumes[0].id,
                throat_chamber_element_kind=throat_volumes[0].kind,
                throat_entry_element_id=throat_entry.id,
                throat_entry_element_kind=throat_entry.kind,
                throat_side_node=throat_side_node,
                throat_side_node_name=node_order[throat_side_node],
                blind_upstream_element_id=blind_upstream.id,
                blind_upstream_element_kind=blind_upstream.kind,
                blind_node=blind_node,
                blind_node_name=node_order[blind_node],
                blind_downstream_element_id=blind_downstream.id,
                blind_downstream_element_kind=blind_downstream.kind,
                rear_path_element_id=rear_path.id,
                rear_path_element_kind=rear_path.kind,
                mouth_node=mouth_node,
                mouth_node_name=node_order[mouth_node],
                mouth_radiator_id=mouth_radiators[0].id,
            )
        )
        break

    return tuple(topologies)

def _collect_front_chamber_throat_side_coupling_topologies(
    *,
    driver_front_index: int,
    driver_rear_index: int,
    node_order: tuple[str, ...],
    shunt_elements: list[AssembledElement],
    branch_elements: list[AssembledElement],
    acoustic_junctions: tuple[AcousticJunction, ...],
) -> tuple[FrontChamberThroatSideCouplingTopology, ...]:
    branch_by_id = {element.id: element for element in branch_elements}
    junction_by_node = {junction.node: junction for junction in acoustic_junctions}

    volumes_by_node: dict[int, list[AssembledElement]] = {}
    radiators_by_node: dict[int, list[AssembledElement]] = {}
    for element in shunt_elements:
        if element.kind == "volume":
            volumes_by_node.setdefault(element.node_a, []).append(element)
        elif element.kind == "radiator":
            radiators_by_node.setdefault(element.node_a, []).append(element)

    branch_incidence: dict[int, list[AssembledElement]] = {}
    for element in branch_elements:
        branch_incidence.setdefault(element.node_a, []).append(element)
        assert element.node_b is not None
        branch_incidence.setdefault(element.node_b, []).append(element)

    front_volumes = volumes_by_node.get(driver_front_index, [])
    if len(front_volumes) != 1 or radiators_by_node.get(driver_front_index):
        return ()

    front_incident = branch_incidence.get(driver_front_index, [])
    if len(front_incident) != 1:
        return ()
    front_coupling = front_incident[0]
    if front_coupling.kind != "waveguide_1d":
        return ()

    rear_volumes = volumes_by_node.get(driver_rear_index, [])
    if len(rear_volumes) != 1 or radiators_by_node.get(driver_rear_index):
        return ()

    rear_incident = branch_incidence.get(driver_rear_index, [])
    if len(rear_incident) != 1:
        return ()
    rear_port = rear_incident[0]
    if rear_port.kind != "waveguide_1d":
        return ()

    injection_node = _other_branch_node(rear_port, driver_rear_index)
    if injection_node == driver_front_index or radiators_by_node.get(injection_node) or volumes_by_node.get(injection_node):
        return ()

    injection_incident = branch_incidence.get(injection_node, [])
    if len(injection_incident) != 2:
        return ()
    throat_entry_candidates = [e for e in injection_incident if e.id != rear_port.id and e.kind == "waveguide_1d"]
    if len(throat_entry_candidates) != 1:
        return ()
    throat_entry = throat_entry_candidates[0]

    throat_node = _other_branch_node(throat_entry, injection_node)
    if throat_node in {driver_rear_index, driver_front_index, injection_node} or radiators_by_node.get(throat_node):
        return ()
    throat_volumes = volumes_by_node.get(throat_node, [])
    if len(throat_volumes) != 1:
        return ()

    throat_incident = branch_incidence.get(throat_node, [])
    if len(throat_incident) != 3:
        return ()

    remaining = [e for e in throat_incident if e.id != throat_entry.id and e.kind == "waveguide_1d"]
    if len(remaining) != 2:
        return ()

    topologies: list[FrontChamberThroatSideCouplingTopology] = []
    for blind_upstream in remaining:
        throat_side_node = _other_branch_node(blind_upstream, throat_node)
        if throat_side_node in {driver_rear_index, driver_front_index, injection_node, throat_node}:
            continue
        if radiators_by_node.get(throat_side_node) or volumes_by_node.get(throat_side_node):
            continue

        throat_side_junction = junction_by_node.get(throat_side_node)
        if throat_side_junction is None or len(throat_side_junction.incident_element_ids) != 3:
            continue
        if front_coupling.id not in throat_side_junction.incident_element_ids:
            continue
        if _other_branch_node(front_coupling, driver_front_index) != throat_side_node:
            continue

        blind_down_ids = [eid for eid in throat_side_junction.incident_element_ids if eid not in {blind_upstream.id, front_coupling.id}]
        if len(blind_down_ids) != 1:
            continue
        blind_downstream = branch_by_id[blind_down_ids[0]]
        if blind_downstream.kind != "waveguide_1d":
            continue

        blind_node = _other_branch_node(blind_downstream, throat_side_node)
        if blind_node in {driver_rear_index, driver_front_index, injection_node, throat_node, throat_side_node}:
            continue
        if len(branch_incidence.get(blind_node, [])) != 1:
            continue
        if radiators_by_node.get(blind_node) or volumes_by_node.get(blind_node):
            continue

        stem_candidates = [e for e in remaining if e.id != blind_upstream.id]
        if len(stem_candidates) != 1:
            continue
        stem = stem_candidates[0]
        if stem.kind != "waveguide_1d":
            continue

        split_node = _other_branch_node(stem, throat_node)
        split_junction = junction_by_node.get(split_node)
        if split_junction is None or len(split_junction.incident_element_ids) != 3:
            continue
        incident = [branch_by_id[eid] for eid in split_junction.incident_element_ids]
        if stem.id not in {e.id for e in incident}:
            continue
        non_stem = [e for e in incident if e.id != stem.id]
        if len(non_stem) != 2:
            continue

        for tapped_upstream in non_stem:
            if tapped_upstream.kind != "waveguide_1d":
                continue
            tap_node = _other_branch_node(tapped_upstream, split_node)
            if tap_node in {driver_front_index, driver_rear_index, injection_node, throat_node, throat_side_node, blind_node}:
                continue
            if radiators_by_node.get(tap_node) or volumes_by_node.get(tap_node):
                continue

            tap_incident = branch_incidence.get(tap_node, [])
            if len(tap_incident) != 2:
                continue
            tapped_downstream_candidates = [e for e in tap_incident if e.id != tapped_upstream.id and e.kind == "waveguide_1d"]
            if len(tapped_downstream_candidates) != 1:
                continue
            tapped_downstream = tapped_downstream_candidates[0]

            merge_node = _other_branch_node(tapped_downstream, tap_node)
            merge_junction = junction_by_node.get(merge_node)
            if merge_junction is None or len(merge_junction.incident_element_ids) != 3:
                continue

            main_leg_candidates = [
                e for e in non_stem
                if e.id != tapped_upstream.id and e.kind == "waveguide_1d" and _other_branch_node(e, split_node) == merge_node
            ]
            if len(main_leg_candidates) != 1:
                continue
            main_leg = main_leg_candidates[0]

            merge_ids = set(merge_junction.incident_element_ids)
            if main_leg.id not in merge_ids or tapped_downstream.id not in merge_ids:
                continue

            shared_exit_ids = [eid for eid in merge_junction.incident_element_ids if eid not in {main_leg.id, tapped_downstream.id}]
            if len(shared_exit_ids) != 1:
                continue
            shared_exit = branch_by_id[shared_exit_ids[0]]
            if shared_exit.kind != "waveguide_1d":
                continue

            mouth_node = _other_branch_node(shared_exit, merge_node)
            if mouth_node in {driver_front_index, driver_rear_index, injection_node, throat_node, throat_side_node, blind_node, split_node, tap_node}:
                continue
            if len(branch_incidence.get(mouth_node, [])) != 1:
                continue
            mouth_radiators = radiators_by_node.get(mouth_node, [])
            if len(mouth_radiators) != 1:
                continue

            topologies.append(
                FrontChamberThroatSideCouplingTopology(
                    rear_node=driver_rear_index,
                    rear_node_name=node_order[driver_rear_index],
                    rear_chamber_element_id=rear_volumes[0].id,
                    rear_chamber_element_kind=rear_volumes[0].kind,
                    injection_node=injection_node,
                    injection_node_name=node_order[injection_node],
                    port_injection_element_id=rear_port.id,
                    port_injection_element_kind=rear_port.kind,
                    throat_node=throat_node,
                    throat_node_name=node_order[throat_node],
                    throat_chamber_element_id=throat_volumes[0].id,
                    throat_chamber_element_kind=throat_volumes[0].kind,
                    throat_entry_element_id=throat_entry.id,
                    throat_entry_element_kind=throat_entry.kind,
                    throat_side_node=throat_side_node,
                    throat_side_node_name=node_order[throat_side_node],
                    blind_upstream_element_id=blind_upstream.id,
                    blind_upstream_element_kind=blind_upstream.kind,
                    blind_node=blind_node,
                    blind_node_name=node_order[blind_node],
                    blind_downstream_element_id=blind_downstream.id,
                    blind_downstream_element_kind=blind_downstream.kind,
                    front_chamber_node=driver_front_index,
                    front_chamber_node_name=node_order[driver_front_index],
                    front_chamber_element_id=front_volumes[0].id,
                    front_chamber_element_kind=front_volumes[0].kind,
                    front_coupling_element_id=front_coupling.id,
                    front_coupling_element_kind=front_coupling.kind,
                    stem_element_id=stem.id,
                    stem_element_kind=stem.kind,
                    split_node=split_node,
                    split_node_name=node_order[split_node],
                    tap_node=tap_node,
                    tap_node_name=node_order[tap_node],
                    merge_node=merge_node,
                    merge_node_name=node_order[merge_node],
                    main_leg_element_id=main_leg.id,
                    main_leg_element_kind=main_leg.kind,
                    tapped_upstream_element_id=tapped_upstream.id,
                    tapped_upstream_element_kind=tapped_upstream.kind,
                    tapped_downstream_element_id=tapped_downstream.id,
                    tapped_downstream_element_kind=tapped_downstream.kind,
                    shared_exit_element_id=shared_exit.id,
                    shared_exit_element_kind=shared_exit.kind,
                    mouth_node=mouth_node,
                    mouth_node_name=node_order[mouth_node],
                    mouth_radiator_id=mouth_radiators[0].id,
                )
            )
            break
        if topologies:
            break

    return tuple(topologies)

def _collect_dual_radiator_topologies(
    *,
    direct_front_radiation_topologies: tuple[DirectFrontRadiationTopology, ...],
) -> tuple[DualRadiatorTopology, ...]:
    topologies: list[DualRadiatorTopology] = []
    for topology in direct_front_radiation_topologies:
        topologies.append(
            DualRadiatorTopology(
                front_node=topology.front_node,
                front_node_name=topology.front_node_name,
                front_radiator_id=topology.front_radiator_id,
                rear_node=topology.rear_node,
                rear_node_name=topology.rear_node_name,
                rear_chamber_element_id=topology.rear_chamber_element_id,
                rear_chamber_element_kind=topology.rear_chamber_element_kind,
                injection_node=topology.injection_node,
                injection_node_name=topology.injection_node_name,
                port_injection_element_id=topology.port_injection_element_id,
                port_injection_element_kind=topology.port_injection_element_kind,
                throat_node=topology.throat_node,
                throat_node_name=topology.throat_node_name,
                throat_chamber_element_id=topology.throat_chamber_element_id,
                throat_chamber_element_kind=topology.throat_chamber_element_kind,
                throat_entry_element_id=topology.throat_entry_element_id,
                throat_entry_element_kind=topology.throat_entry_element_kind,
                throat_side_node=topology.throat_side_node,
                throat_side_node_name=topology.throat_side_node_name,
                blind_upstream_element_id=topology.blind_upstream_element_id,
                blind_upstream_element_kind=topology.blind_upstream_element_kind,
                blind_node=topology.blind_node,
                blind_node_name=topology.blind_node_name,
                blind_downstream_element_id=topology.blind_downstream_element_id,
                blind_downstream_element_kind=topology.blind_downstream_element_kind,
                rear_path_element_id=topology.rear_path_element_id,
                rear_path_element_kind=topology.rear_path_element_kind,
                mouth_node=topology.mouth_node,
                mouth_node_name=topology.mouth_node_name,
                mouth_radiator_id=topology.mouth_radiator_id,
            )
        )

    return tuple(topologies)


def assemble_system(model: NormalizedModel) -> AssembledSystem:
    """Assemble the currently supported acoustic topology.

    Supported in this patch:
    - volumes (shunt to reference)
    - radiators (shunt to reference)
    - ducts (series/branch between two acoustic nodes)
    - waveguide_1d (two-node branch element)
    """

    node_order = tuple(model.node_order)
    node_index = {node: i for i, node in enumerate(node_order)}

    if len(node_index) != len(node_order):
        raise ValidationError("node_order contains duplicate node names")

    driver_front_index = _require_known_node(
        model.driver.node_front, node_index, context="driver.node_front"
    )
    driver_rear_index = _require_known_node(
        model.driver.node_rear, node_index, context="driver.node_rear"
    )

    shunt_elements: list[AssembledElement] = []
    branch_elements: list[AssembledElement] = []

    for volume in model.volumes:
        shunt_elements.append(
            AssembledElement(
                id=volume.id,
                kind="volume",
                node_a=_require_known_node(volume.node, node_index, context=f"volume {volume.id}"),
                node_b=None,
                payload=volume,
            )
        )

    for radiator in model.radiators:
        shunt_elements.append(
            AssembledElement(
                id=radiator.id,
                kind="radiator",
                node_a=_require_known_node(
                    radiator.node, node_index, context=f"radiator {radiator.id}"
                ),
                node_b=None,
                payload=radiator,
            )
        )

    for duct in model.ducts:
        branch_elements.append(
            AssembledElement(
                id=duct.id,
                kind="duct",
                node_a=_require_known_node(duct.node_a, node_index, context=f"duct {duct.id}.node_a"),
                node_b=_require_known_node(duct.node_b, node_index, context=f"duct {duct.id}.node_b"),
                payload=duct,
            )
        )

    for waveguide in model.waveguides:
        branch_elements.append(
            AssembledElement(
                id=waveguide.id,
                kind="waveguide_1d",
                node_a=_require_known_node(
                    waveguide.node_a, node_index, context=f"waveguide_1d {waveguide.id}.node_a"
                ),
                node_b=_require_known_node(
                    waveguide.node_b, node_index, context=f"waveguide_1d {waveguide.id}.node_b"
                ),
                payload=waveguide,
            )
        )

    parallel_branch_bundles = _collect_parallel_branch_bundles(branch_elements, node_order)
    acoustic_junctions = _collect_acoustic_junctions(branch_elements, node_order)
    branched_horn_skeletons = _collect_branched_horn_skeletons(
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        acoustic_junctions=acoustic_junctions,
    )
    recombination_topologies = _collect_recombination_topologies(
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        parallel_branch_bundles=parallel_branch_bundles,
        acoustic_junctions=acoustic_junctions,
    )
    split_merge_horn_skeletons = _collect_split_merge_horn_skeletons(
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        parallel_branch_bundles=parallel_branch_bundles,
        acoustic_junctions=acoustic_junctions,
    )
    tapped_driver_skeletons = _collect_tapped_driver_skeletons(
        driver_front_index=driver_front_index,
        shunt_elements=shunt_elements,
        split_merge_horn_skeletons=split_merge_horn_skeletons,
    )
    offset_tap_topologies = _collect_offset_tap_topologies(
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        acoustic_junctions=acoustic_junctions,
    )
    rear_chamber_tapped_skeletons = _collect_rear_chamber_tapped_skeletons(
        shunt_elements=shunt_elements,
        offset_tap_topologies=offset_tap_topologies,
    )
    rear_chamber_port_injection_topologies = _collect_rear_chamber_port_injection_topologies(
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        acoustic_junctions=acoustic_junctions,
    )
    throat_chamber_topologies = _collect_throat_chamber_topologies(
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        acoustic_junctions=acoustic_junctions,
    )
    blind_throat_side_segment_topologies = _collect_blind_throat_side_segment_topologies(
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        acoustic_junctions=acoustic_junctions,
    )
    driver_front_chamber_topologies = _collect_driver_front_chamber_topologies(
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        acoustic_junctions=acoustic_junctions,
    )
    front_chamber_throat_side_coupling_topologies = _collect_front_chamber_throat_side_coupling_topologies(
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
        acoustic_junctions=acoustic_junctions,
    )
    direct_front_radiation_topologies = _collect_direct_front_radiation_topologies(
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        node_order=node_order,
        shunt_elements=shunt_elements,
        branch_elements=branch_elements,
    )
    dual_radiator_topologies = _collect_dual_radiator_topologies(
        direct_front_radiation_topologies=direct_front_radiation_topologies,
    )

    return AssembledSystem(
        node_order=node_order,
        node_index=node_index,
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        shunt_elements=tuple(shunt_elements),
        branch_elements=tuple(branch_elements),
        parallel_branch_bundles=parallel_branch_bundles,
        acoustic_junctions=acoustic_junctions,
        branched_horn_skeletons=branched_horn_skeletons,
        recombination_topologies=recombination_topologies,
        split_merge_horn_skeletons=split_merge_horn_skeletons,
        tapped_driver_skeletons=tapped_driver_skeletons,
        offset_tap_topologies=offset_tap_topologies,
        rear_chamber_tapped_skeletons=rear_chamber_tapped_skeletons,
        rear_chamber_port_injection_topologies=rear_chamber_port_injection_topologies,
        throat_chamber_topologies=throat_chamber_topologies,
        blind_throat_side_segment_topologies=blind_throat_side_segment_topologies,
        driver_front_chamber_topologies=driver_front_chamber_topologies,
        front_chamber_throat_side_coupling_topologies=front_chamber_throat_side_coupling_topologies,
        direct_front_radiation_topologies=direct_front_radiation_topologies,
        dual_radiator_topologies=dual_radiator_topologies,
    )
