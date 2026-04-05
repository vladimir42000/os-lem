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
                "node_b": "split",
                "length": "22 cm",
                "area_start": "85 cm2",
                "area_end": "90 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "leg_main",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "40 cm",
                "area_start": "90 cm2",
                "area_end": "105 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "leg_aux",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "28 cm",
                "area_start": "55 cm2",
                "area_end": "65 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "shared_exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "rear_mouth",
                "length": "34 cm",
                "area_start": "105 cm2",
                "area_end": "108 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "rear_mouth_rad",
                "type": "radiator",
                "node": "rear_mouth",
                "model": "flanged_piston",
                "area": "108 cm2",
            },
        ]
    )
    return {
        "meta": {"name": "direct_plus_split_merge_rear_path_demo", "radiation_space": "2pi"},
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


def test_assemble_system_collects_one_direct_plus_split_merge_rear_path_skeleton() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.split_merge_horn_skeletons) == 1
    assert len(assembled.direct_plus_split_merge_rear_path_skeletons) == 1

    skeleton = assembled.direct_plus_split_merge_rear_path_skeletons[0]
    assert skeleton.front_node_name == "front"
    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.rear_node_name == "rear"
    assert skeleton.split_node_name == "split"
    assert skeleton.merge_node_name == "merge"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.rear_leg_element_ids == ("leg_main", "leg_aux")
    assert skeleton.shared_exit_element_id == "shared_exit"
    assert skeleton.rear_mouth_node_name == "rear_mouth"
    assert skeleton.rear_mouth_radiator_id == "rear_mouth_rad"


def test_assemble_system_does_not_claim_direct_plus_split_merge_rear_path_without_front_radiator() -> None:
    model, warnings = normalize_model(_model_dict(include_front_radiator=False))
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.split_merge_horn_skeletons) == 1
    assert len(assembled.direct_plus_split_merge_rear_path_skeletons) == 0
