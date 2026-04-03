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
                "length": "30 cm",
                "area_start": "90 cm2",
                "area_end": "95 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_main_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_main",
                "length": "45 cm",
                "area_start": "95 cm2",
                "area_end": "110 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "rear_aux_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_aux",
                "length": "26 cm",
                "area_start": "40 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_main_rad",
                "type": "radiator",
                "node": "rear_mouth_main",
                "model": "flanged_piston",
                "area": "110 cm2",
            },
            {
                "id": "rear_aux_rad",
                "type": "radiator",
                "node": "rear_mouth_aux",
                "model": "flanged_piston",
                "area": "55 cm2",
            },
        ]
    )
    return {
        "meta": {"name": "direct_plus_branched_rear_path_demo", "radiation_space": "2pi"},
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


def test_assemble_system_collects_one_direct_plus_branched_rear_path_skeleton() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.branched_horn_skeletons) == 1
    assert len(assembled.direct_plus_branched_rear_path_skeletons) == 1

    skeleton = assembled.direct_plus_branched_rear_path_skeletons[0]
    assert skeleton.front_node_name == "front"
    assert skeleton.front_radiator_id == "front_rad"
    assert skeleton.rear_node_name == "rear"
    assert skeleton.junction_node_name == "junction"
    assert skeleton.stem_element_id == "stem"
    assert skeleton.rear_branch_element_ids == ("rear_main_leg", "rear_aux_leg")
    assert skeleton.rear_mouth_node_names == ("rear_mouth_main", "rear_mouth_aux")
    assert skeleton.rear_mouth_radiator_ids == ("rear_main_rad", "rear_aux_rad")


def test_assemble_system_does_not_claim_direct_plus_branched_rear_path_without_front_radiator() -> None:
    model, warnings = normalize_model(_model_dict(include_front_radiator=False))
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.branched_horn_skeletons) == 1
    assert len(assembled.direct_plus_branched_rear_path_skeletons) == 0
