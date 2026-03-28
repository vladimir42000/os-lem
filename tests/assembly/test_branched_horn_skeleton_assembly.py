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


def _branched_horn_model(*, include_tap_radiator: bool = True) -> NormalizedModel:
    radiators = [
        RadiatorElement(id="front_rad", node="front", model="flanged_piston", area_m2=0.0132),
        RadiatorElement(id="main_rad", node="mouth_main", model="flanged_piston", area_m2=0.0110),
    ]
    if include_tap_radiator:
        radiators.append(
            RadiatorElement(id="tap_rad", node="mouth_tap", model="flanged_piston", area_m2=0.0055)
        )

    return NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="stem",
                node_a="rear",
                node_b="junction",
                length_m=0.30,
                area_start_m2=0.0090,
                area_end_m2=0.0095,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="main_branch",
                node_a="junction",
                node_b="mouth_main",
                length_m=0.45,
                area_start_m2=0.0095,
                area_end_m2=0.0110,
                profile="conical",
                segments=6,
            ),
            Waveguide1DElement(
                id="tap_branch",
                node_a="junction",
                node_b="mouth_tap",
                length_m=0.26,
                area_start_m2=0.0040,
                area_end_m2=0.0055,
                profile="conical",
                segments=4,
            ),
        ],
        radiators=radiators,
        node_order=["front", "rear", "junction", "mouth_main", "mouth_tap"],
    )


def test_assemble_system_collects_one_branched_horn_skeleton() -> None:
    assembled = assemble_system(_branched_horn_model())

    assert len(assembled.parallel_branch_bundles) == 0
    assert len(assembled.acoustic_junctions) == 1
    assert len(assembled.branched_horn_skeletons) == 1

    skeleton = assembled.branched_horn_skeletons[0]
    assert skeleton.rear_node_name == "rear"
    assert skeleton.junction_node_name == "junction"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.branch_element_ids == ("main_branch", "tap_branch")
    assert skeleton.mouth_node_names == ("mouth_main", "mouth_tap")
    assert skeleton.mouth_radiator_ids == ("main_rad", "tap_rad")


def test_assemble_system_does_not_claim_branched_horn_skeleton_without_two_mouth_radiators() -> None:
    assembled = assemble_system(_branched_horn_model(include_tap_radiator=False))

    assert len(assembled.acoustic_junctions) == 1
    assert len(assembled.branched_horn_skeletons) == 0
