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


def _require_known_node(node: str, node_index: dict[str, int], *, context: str) -> int:
    try:
        return node_index[node]
    except KeyError as exc:
        raise ValidationError(f"{context} refers to unknown node {node!r}") from exc


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

    return AssembledSystem(
        node_order=node_order,
        node_index=node_index,
        driver_front_index=driver_front_index,
        driver_rear_index=driver_rear_index,
        shunt_elements=tuple(shunt_elements),
        branch_elements=tuple(branch_elements),
    )
