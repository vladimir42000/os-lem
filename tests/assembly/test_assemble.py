from __future__ import annotations

import pytest

from os_lem.assemble import assemble_system
from os_lem.errors import ValidationError
from os_lem.model import (
    Driver,
    DuctElement,
    NormalizedModel,
    Observation,
    RadiatorElement,
    VolumeElement,
    Waveguide1DElement,
)


def _driver() -> Driver:
    return Driver(
        id="drv1",
        Re=6.0,
        Le=0.0,
        Bl=7.0,
        Mms=0.02,
        Cms=1.0e-3,
        Rms=1.0,
        Sd=0.013,
        node_front="front",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def test_assemble_system_resolves_nodes_and_driver_indices() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="v1", node="rear", value_m3=0.02)],
        ducts=[DuctElement(id="d1", node_a="front", node_b="port", length_m=0.1, area_m2=0.01)],
        radiators=[RadiatorElement(id="r1", node="port", model="flanged_piston", area_m2=0.01)],
        observations=[Observation(id="obs1", type="spl", data={"radiator_id": "r1", "distance_m": 1.0})],
        node_order=["front", "rear", "port"],
    )

    assembled = assemble_system(model)

    assert assembled.node_order == ("front", "rear", "port")
    assert assembled.node_index == {"front": 0, "rear": 1, "port": 2}
    assert assembled.driver_front_index == 0
    assert assembled.driver_rear_index == 1


def test_assemble_system_collects_shunt_and_branch_elements_in_deterministic_order() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="v1", node="rear", value_m3=0.02)],
        ducts=[DuctElement(id="d1", node_a="front", node_b="port", length_m=0.1, area_m2=0.01)],
        radiators=[RadiatorElement(id="r1", node="port", model="flanged_piston", area_m2=0.01)],
        node_order=["front", "rear", "port"],
    )

    assembled = assemble_system(model)

    assert [element.id for element in assembled.shunt_elements] == ["v1", "r1"]
    assert [element.kind for element in assembled.shunt_elements] == ["volume", "radiator"]
    assert [element.id for element in assembled.branch_elements] == ["d1"]
    assert assembled.branch_elements[0].kind == "duct"
    assert assembled.branch_elements[0].node_a == 0
    assert assembled.branch_elements[0].node_b == 2


def test_assemble_system_rejects_unknown_nodes() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="v1", node="missing_node", value_m3=0.02)],
        node_order=["front", "rear", "port"],
    )

    with pytest.raises(ValidationError, match="unknown node"):
        assemble_system(model)


def test_assemble_system_rejects_duplicate_node_order_entries() -> None:
    model = NormalizedModel(
        driver=_driver(),
        node_order=["front", "rear", "front"],
    )

    with pytest.raises(ValidationError, match="duplicate node names"):
        assemble_system(model)


def test_assemble_system_collects_waveguide_as_branch_element() -> None:
    model = NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="wg1",
                node_a="front",
                node_b="port",
                length_m=0.4,
                area_start_m2=0.01,
                area_end_m2=0.02,
                profile="conical",
                segments=8,
            )
        ],
        node_order=["front", "rear", "port"],
    )

    assembled = assemble_system(model)

    assert [element.id for element in assembled.branch_elements] == ["wg1"]
    assert [element.kind for element in assembled.branch_elements] == ["waveguide_1d"]
    assert assembled.branch_elements[0].node_a == 0
    assert assembled.branch_elements[0].node_b == 2
