from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_split_merge_rear_path import build_direct_plus_split_merge_rear_path_model_dict


def test_assemble_system_carries_one_direct_plus_split_merge_rear_path_contribution_contract() -> None:
    model, warnings = normalize_model(build_direct_plus_split_merge_rear_path_model_dict())
    assert warnings == []

    system = assemble_system(model)

    assert len(system.direct_plus_split_merge_rear_path_skeletons) == 1
    assert len(system.direct_plus_split_merge_rear_path_contribution_contracts) == 1

    contract = system.direct_plus_split_merge_rear_path_contribution_contracts[0]
    assert contract.front_node_name == "front"
    assert contract.front_radiator_id == "front_rad"
    assert contract.split_node_name == "split"
    assert contract.merge_node_name == "merge"
    assert contract.rear_leg_element_ids == ("leg_main", "leg_aux")
    assert contract.shared_exit_element_id == "shared_exit"
    assert contract.rear_mouth_node_name == "rear_mouth"
    assert contract.rear_mouth_radiator_id == "rear_mouth_rad"
    assert contract.front_node != contract.rear_mouth_node
    assert contract.front_radiator_id != contract.rear_mouth_radiator_id
