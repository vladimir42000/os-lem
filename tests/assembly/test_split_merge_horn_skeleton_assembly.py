from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.model import Driver, NormalizedModel, RadiatorElement, Waveguide1DElement


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


def _split_merge_model(*, include_mouth_radiator: bool = True) -> NormalizedModel:
    radiators = [
        RadiatorElement(id="front_rad", node="front", model="flanged_piston", area_m2=0.0132),
    ]
    if include_mouth_radiator:
        radiators.append(
            RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0108)
        )

    return NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="stem",
                node_a="rear",
                node_b="split",
                length_m=0.22,
                area_start_m2=0.0085,
                area_end_m2=0.0090,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="leg_main",
                node_a="split",
                node_b="merge",
                length_m=0.40,
                area_start_m2=0.0090,
                area_end_m2=0.0105,
                profile="conical",
                segments=5,
            ),
            Waveguide1DElement(
                id="leg_tap",
                node_a="split",
                node_b="merge",
                length_m=0.28,
                area_start_m2=0.0055,
                area_end_m2=0.0065,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="exit",
                node_a="merge",
                node_b="mouth",
                length_m=0.34,
                area_start_m2=0.0105,
                area_end_m2=0.0108,
                profile="conical",
                segments=5,
            ),
        ],
        radiators=radiators,
        node_order=["front", "rear", "split", "merge", "mouth"],
    )


def test_assemble_system_collects_one_split_merge_horn_skeleton() -> None:
    assembled = assemble_system(_split_merge_model())

    assert len(assembled.parallel_branch_bundles) == 1
    assert len(assembled.acoustic_junctions) == 2
    assert len(assembled.split_merge_horn_skeletons) == 1

    skeleton = assembled.split_merge_horn_skeletons[0]
    assert skeleton.rear_node_name == "rear"
    assert skeleton.split_node_name == "split"
    assert skeleton.merge_node_name == "merge"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.leg_element_ids == ("leg_main", "leg_tap")
    assert skeleton.shared_exit_element_id == "exit"
    assert skeleton.mouth_node_name == "mouth"
    assert skeleton.mouth_radiator_id == "mouth_rad"



def test_assemble_system_does_not_claim_split_merge_horn_skeleton_without_mouth_radiator() -> None:
    assembled = assemble_system(_split_merge_model(include_mouth_radiator=False))

    assert len(assembled.parallel_branch_bundles) == 1
    assert len(assembled.acoustic_junctions) == 2
    assert len(assembled.split_merge_horn_skeletons) == 0
