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

    return AssembledSystem(
        node_order=node_order,
        node_index=node_index,
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        shunt_elements=tuple(shunt_elements),
        branch_elements=tuple(branch_elements),
        parallel_branch_bundles=parallel_branch_bundles,
        acoustic_junctions=acoustic_junctions,
    )
