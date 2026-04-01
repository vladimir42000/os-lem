from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "front_rear_sum_demo", "radiation_space": "2pi"},
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
        "elements": [
            {"id": "rear_chamber", "type": "volume", "node": "rear", "value": "10 l"},
            {"id": "throat_chamber", "type": "volume", "node": "throat", "value": "1.6 l"},
            {"id": "rear_port", "type": "waveguide_1d", "node_a": "rear", "node_b": "inject", "length": "11 cm", "area_start": "42 cm2", "area_end": "45 cm2", "profile": "conical", "segments": 2},
            {"id": "throat_entry", "type": "waveguide_1d", "node_a": "inject", "node_b": "throat", "length": "8 cm", "area_start": "45 cm2", "area_end": "48 cm2", "profile": "conical", "segments": 2},
            {"id": "blind_upstream", "type": "waveguide_1d", "node_a": "throat", "node_b": "throat_side", "length": "4 cm", "area_start": "48 cm2", "area_end": "41 cm2", "profile": "conical", "segments": 2},
            {"id": "blind_downstream", "type": "waveguide_1d", "node_a": "throat_side", "node_b": "blind", "length": "5 cm", "area_start": "41 cm2", "area_end": "39 cm2", "profile": "conical", "segments": 2},
            {"id": "rear_leg", "type": "waveguide_1d", "node_a": "throat", "node_b": "mouth", "length": "61 cm", "area_start": "48 cm2", "area_end": "105 cm2", "profile": "conical", "segments": 7},
            {"id": "front_rad", "type": "radiator", "node": "front", "model": "flanged_piston", "area": "130 cm2"},
            {"id": "mouth_rad", "type": "radiator", "node": "mouth", "model": "flanged_piston", "area": "105 cm2"},
        ],
        "observations": [],
    }


def test_assemble_system_carries_one_explicit_front_rear_radiation_sum_observability() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []

    system = assemble_system(model)

    assert len(system.dual_radiator_topologies) == 1
    assert len(system.front_rear_radiation_sum_observabilities) == 1

    observability = system.front_rear_radiation_sum_observabilities[0]
    assert observability.front_node_name == "front"
    assert observability.front_radiator_id == "front_rad"
    assert observability.rear_mouth_node_name == "mouth"
    assert observability.rear_radiator_id == "mouth_rad"
    assert observability.front_node != observability.rear_mouth_node
    assert observability.front_radiator_id != observability.rear_radiator_id
