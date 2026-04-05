from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_rear_path import build_direct_plus_branched_rear_path_model_dict


def test_assemble_system_carries_one_direct_plus_branched_rear_path_contribution_contract() -> None:
    model, warnings = normalize_model(build_direct_plus_branched_rear_path_model_dict())
    assert warnings == []

    system = assemble_system(model)

    assert len(system.direct_plus_branched_rear_path_skeletons) == 1
    assert len(system.direct_plus_branched_rear_path_contribution_contracts) == 1

    contract = system.direct_plus_branched_rear_path_contribution_contracts[0]
    assert contract.front_node_name == "front"
    assert contract.front_radiator_id == "front_rad"
    assert contract.rear_junction_node_name == "junction"
    assert contract.rear_branch_element_ids == ("rear_main_leg", "rear_aux_leg")
    assert contract.rear_mouth_node_names == ("rear_mouth_main", "rear_mouth_aux")
    assert contract.rear_mouth_radiator_ids == ("rear_main_rad", "rear_aux_rad")
    assert contract.front_node not in contract.rear_mouth_nodes
    assert contract.front_radiator_id not in contract.rear_mouth_radiator_ids
