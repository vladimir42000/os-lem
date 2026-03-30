from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.model import Driver, NormalizedModel, RadiatorElement, VolumeElement, Waveguide1DElement


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
        node_front="tap",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def _rear_chamber_port_injection_model(*, include_rear_volume: bool = True) -> NormalizedModel:
    volumes = []
    if include_rear_volume:
        volumes.append(VolumeElement(id="rear_chamber", node="rear", value_m3=0.010))

    return NormalizedModel(
        driver=_driver(),
        volumes=volumes,
        waveguides=[
            Waveguide1DElement(
                id="rear_port",
                node_a="rear",
                node_b="inject",
                length_m=0.11,
                area_start_m2=0.0042,
                area_end_m2=0.0045,
                profile="conical",
                segments=2,
            ),
            Waveguide1DElement(
                id="stem",
                node_a="inject",
                node_b="split",
                length_m=0.19,
                area_start_m2=0.0045,
                area_end_m2=0.0088,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="main_leg",
                node_a="split",
                node_b="merge",
                length_m=0.46,
                area_start_m2=0.0088,
                area_end_m2=0.0102,
                profile="conical",
                segments=6,
            ),
            Waveguide1DElement(
                id="tap_upstream",
                node_a="split",
                node_b="tap",
                length_m=0.18,
                area_start_m2=0.0052,
                area_end_m2=0.0055,
                profile="conical",
                segments=3,
            ),
            Waveguide1DElement(
                id="tap_downstream",
                node_a="tap",
                node_b="merge",
                length_m=0.16,
                area_start_m2=0.0055,
                area_end_m2=0.0062,
                profile="conical",
                segments=3,
            ),
            Waveguide1DElement(
                id="exit",
                node_a="merge",
                node_b="mouth",
                length_m=0.32,
                area_start_m2=0.0102,
                area_end_m2=0.0105,
                profile="conical",
                segments=5,
            ),
        ],
        radiators=[
            RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0105),
        ],
        node_order=["rear", "inject", "split", "tap", "merge", "mouth"],
    )


def test_assemble_system_collects_one_rear_chamber_port_injection_topology() -> None:
    assembled = assemble_system(_rear_chamber_port_injection_model())

    assert len(assembled.offset_tap_topologies) == 0
    assert len(assembled.rear_chamber_tapped_skeletons) == 0
    assert len(assembled.rear_chamber_port_injection_topologies) == 1

    topology = assembled.rear_chamber_port_injection_topologies[0]
    assert topology.rear_node_name == "rear"
    assert topology.rear_chamber_element_id == "rear_chamber"
    assert topology.injection_node_name == "inject"
    assert topology.port_injection_element_id == "rear_port"
    assert topology.stem_element_id == "stem"
    assert topology.split_node_name == "split"
    assert topology.tap_node_name == "tap"
    assert topology.merge_node_name == "merge"
    assert topology.main_leg_element_id == "main_leg"
    assert topology.tapped_upstream_element_id == "tap_upstream"
    assert topology.tapped_downstream_element_id == "tap_downstream"
    assert topology.shared_exit_element_id == "exit"
    assert topology.mouth_node_name == "mouth"
    assert topology.mouth_radiator_id == "mouth_rad"


def test_assemble_system_does_not_claim_rear_chamber_port_injection_without_rear_volume() -> None:
    assembled = assemble_system(_rear_chamber_port_injection_model(include_rear_volume=False))

    assert len(assembled.rear_chamber_port_injection_topologies) == 0
