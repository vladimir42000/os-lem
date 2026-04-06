from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


def _model_dict(*, include_front_radiator: bool = True) -> dict[str, object]:
    elements: list[dict[str, object]] = []
    if include_front_radiator:
        elements.append(
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "flanged_piston",
                "area": "132 cm2",
            }
        )
    elements.extend(
        [
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "junction",
                "length": "20 cm",
                "area_start": "82 cm2",
                "area_end": "88 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "direct_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_direct",
                "length": "34 cm",
                "area_start": "88 cm2",
                "area_end": "96 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "split_feed",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "split",
                "length": "18 cm",
                "area_start": "44 cm2",
                "area_end": "50 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "merge_main",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "26 cm",
                "area_start": "50 cm2",
                "area_end": "58 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "merge_aux",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "31 cm",
                "area_start": "42 cm2",
                "area_end": "47 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "shared_exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "rear_mouth_merged",
                "length": "22 cm",
                "area_start": "58 cm2",
                "area_end": "62 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_direct_rad",
                "type": "radiator",
                "node": "rear_mouth_direct",
                "model": "flanged_piston",
                "area": "96 cm2",
            },
            {
                "id": "rear_merged_rad",
                "type": "radiator",
                "node": "rear_mouth_merged",
                "model": "flanged_piston",
                "area": "62 cm2",
            },
        ]
    )
    return {
        "meta": {"name": "direct_plus_branched_split_merge_rear_path_demo", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "front",
            "node_rear": "rear",
        },
        "elements": elements,
        "observations": [],
    }


def test_assemble_system_collects_one_direct_plus_branched_split_merge_rear_path_skeleton() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.recombination_topologies) == 1
    assert len(assembled.direct_plus_branched_split_merge_rear_path_skeletons) == 1

    skeleton = assembled.direct_plus_branched_split_merge_rear_path_skeletons[0]
    assert skeleton.front_node_name == "front"
    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.rear_node_name == "rear"
    assert skeleton.junction_node_name == "junction"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.direct_branch_element_id == "direct_leg"
    assert skeleton.direct_rear_mouth_node_name == "rear_mouth_direct"
    assert skeleton.direct_rear_mouth_radiator_id == "rear_direct_rad"
    assert skeleton.split_feed_element_id == "split_feed"
    assert skeleton.split_node_name == "split"
    assert skeleton.merge_node_name == "merge"
    assert skeleton.recombined_leg_element_ids == ("merge_main", "merge_aux")
    assert skeleton.shared_exit_element_id == "shared_exit"
    assert skeleton.merged_rear_mouth_node_name == "rear_mouth_merged"
    assert skeleton.merged_rear_mouth_radiator_id == "rear_merged_rad"


def test_assemble_system_does_not_claim_direct_plus_branched_split_merge_rear_path_without_front_radiator() -> None:
    model, warnings = normalize_model(_model_dict(include_front_radiator=False))
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.recombination_topologies) == 1
    assert len(assembled.direct_plus_branched_split_merge_rear_path_skeletons) == 0
