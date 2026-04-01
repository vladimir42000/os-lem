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
        node_front="front",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def _model(*, include_front_radiator: bool = True) -> NormalizedModel:
    radiators = [RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0105)]
    if include_front_radiator:
        radiators.insert(0, RadiatorElement(id="front_rad", node="front", model="flanged_piston", area_m2=0.0130))

    return NormalizedModel(
        driver=_driver(),
        volumes=[
            VolumeElement(id="rear_chamber", node="rear", value_m3=0.010),
            VolumeElement(id="throat_chamber", node="throat", value_m3=0.0016),
        ],
        waveguides=[
            Waveguide1DElement(id="rear_port", node_a="rear", node_b="inject", length_m=0.11, area_start_m2=0.0042, area_end_m2=0.0045, profile="conical", segments=2),
            Waveguide1DElement(id="throat_entry", node_a="inject", node_b="throat", length_m=0.08, area_start_m2=0.0045, area_end_m2=0.0048, profile="conical", segments=2),
            Waveguide1DElement(id="blind_upstream", node_a="throat", node_b="throat_side", length_m=0.04, area_start_m2=0.0048, area_end_m2=0.0041, profile="conical", segments=2),
            Waveguide1DElement(id="blind_downstream", node_a="throat_side", node_b="blind", length_m=0.05, area_start_m2=0.0041, area_end_m2=0.0039, profile="conical", segments=2),
            Waveguide1DElement(id="rear_leg", node_a="throat", node_b="mouth", length_m=0.61, area_start_m2=0.0048, area_end_m2=0.0105, profile="conical", segments=7),
        ],
        radiators=radiators,
        node_order=["rear", "inject", "throat", "throat_side", "blind", "front", "mouth"],
    )


def test_assemble_system_collects_one_back_loaded_horn_skeleton() -> None:
    assembled = assemble_system(_model())

    assert len(assembled.direct_front_radiation_topologies) == 1
    assert len(assembled.dual_radiator_topologies) == 1
    assert len(assembled.back_loaded_horn_skeletons) == 1

    skeleton = assembled.back_loaded_horn_skeletons[0]
    assert skeleton.front_node_name == "front"
    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.rear_node_name == "rear"
    assert skeleton.rear_chamber_element_id == "rear_chamber"
    assert skeleton.throat_node_name == "throat"
    assert skeleton.throat_side_node_name == "throat_side"
    assert skeleton.rear_path_element_id == "rear_leg"
    assert skeleton.mouth_node_name == "mouth"
    assert skeleton.mouth_radiator_id == "mouth_rad"


def test_assemble_system_does_not_claim_back_loaded_horn_skeleton_without_front_radiator() -> None:
    assembled = assemble_system(_model(include_front_radiator=False))

    assert len(assembled.direct_front_radiation_topologies) == 0
    assert len(assembled.dual_radiator_topologies) == 0
    assert len(assembled.back_loaded_horn_skeletons) == 0
