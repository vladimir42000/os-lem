from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_back_loaded_horn import build_back_loaded_horn_model_dict


def test_assemble_system_carries_one_rear_radiation_delay_path_observability() -> None:
    model, warnings = normalize_model(build_back_loaded_horn_model_dict())
    assert warnings == []

    system = assemble_system(model)

    assert len(system.back_loaded_horn_skeletons) == 1
    assert len(system.rear_radiation_delay_path_observabilities) == 1

    observability = system.rear_radiation_delay_path_observabilities[0]
    assert observability.front_node_name == "front"
    assert observability.front_radiator_id == "front_rad"
    assert observability.rear_path_element_id == "rear_leg"
    assert observability.rear_path_element_kind == "waveguide_1d"
    assert observability.rear_mouth_node_name == "mouth"
    assert observability.rear_radiator_id == "mouth_rad"
    assert observability.front_node != observability.rear_mouth_node
    assert observability.front_radiator_id != observability.rear_radiator_id
