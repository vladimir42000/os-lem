"""Topology checks for normalized models."""

from __future__ import annotations

from collections import defaultdict, deque

from .errors import ValidationError
from .model import NormalizedModel


def _connected_components(graph: dict[str, set[str]]) -> list[set[str]]:
    seen: set[str] = set()
    components: list[set[str]] = []

    for start in graph:
        if start in seen:
            continue
        comp: set[str] = set()
        q = deque([start])
        seen.add(start)
        while q:
            node = q.popleft()
            comp.add(node)
            for nxt in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        components.append(comp)
    return components


def validate_topology(model: NormalizedModel) -> None:
    if model.driver.node_front == model.driver.node_rear:
        raise ValidationError("driver.node_front and driver.node_rear must not be the same node")

    graph: dict[str, set[str]] = defaultdict(set)
    shunt_nodes: set[str] = set()

    for node in model.node_order:
        graph[node]

    graph[model.driver.node_front].add(model.driver.node_rear)
    graph[model.driver.node_rear].add(model.driver.node_front)

    for duct in model.ducts:
        graph[duct.node_a].add(duct.node_b)
        graph[duct.node_b].add(duct.node_a)

    for line in model.waveguides:
        graph[line.node_a].add(line.node_b)
        graph[line.node_b].add(line.node_a)

    for vol in model.volumes:
        shunt_nodes.add(vol.node)

    for rad in model.radiators:
        shunt_nodes.add(rad.node)

    for comp in _connected_components(graph):
        if comp and not (comp & shunt_nodes):
            raise ValidationError(
                "Acoustic connected component lacks a valid shunt path to reference"
            )
