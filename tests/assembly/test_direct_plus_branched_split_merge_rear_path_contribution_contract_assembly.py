from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_split_merge_rear_path import (
    build_direct_plus_branched_split_merge_rear_path_model_dict,
)


def test_assemble_system_collects_one_direct_plus_branched_split_merge_rear_path_contribution_contract() -> None:
    model, warnings = normalize_model(build_direct_plus_branched_split_merge_rear_path_model_dict())
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.direct_plus_branched_split_merge_rear_path_skeletons) == 1
    assert len(assembled.direct_plus_branched_split_merge_rear_path_contribution_contracts) == 1

    skeleton = assembled.direct_plus_branched_split_merge_rear_path_skeletons[0]
    contract = assembled.direct_plus_branched_split_merge_rear_path_contribution_contracts[0]

    assert contract.front_node == skeleton.front_node
    assert contract.front_node_name == "front"
    assert contract.front_radiator_id == "front_rad"
    assert contract.rear_junction_node == skeleton.junction_node
    assert contract.rear_junction_node_name == "junction"
    assert contract.direct_branch_element_id == skeleton.direct_branch_element_id
    assert contract.direct_rear_mouth_node == skeleton.direct_rear_mouth_node
    assert contract.direct_rear_mouth_radiator_id == "rear_direct_rad"
    assert contract.split_feed_element_id == skeleton.split_feed_element_id
    assert contract.split_node == skeleton.split_node
    assert contract.split_node_name == "split"
    assert contract.merge_node == skeleton.merge_node
    assert contract.merge_node_name == "merge"
    assert contract.recombined_leg_element_ids == skeleton.recombined_leg_element_ids
    assert contract.shared_exit_element_id == skeleton.shared_exit_element_id
    assert contract.merged_rear_mouth_node == skeleton.merged_rear_mouth_node
    assert contract.merged_rear_mouth_radiator_id == "rear_merged_rad"


def test_direct_plus_branched_split_merge_rear_path_contribution_contract_keeps_front_and_rear_radiators_distinct() -> None:
    model, warnings = normalize_model(build_direct_plus_branched_split_merge_rear_path_model_dict())
    assert warnings == []

    assembled = assemble_system(model)
    contract = assembled.direct_plus_branched_split_merge_rear_path_contribution_contracts[0]

    assert contract.front_radiator_id not in {
        contract.direct_rear_mouth_radiator_id,
        contract.merged_rear_mouth_radiator_id,
    }
    assert contract.direct_rear_mouth_radiator_id != contract.merged_rear_mouth_radiator_id
    assert contract.front_node not in {
        contract.direct_rear_mouth_node,
        contract.merged_rear_mouth_node,
    }
    assert contract.direct_rear_mouth_node != contract.merged_rear_mouth_node
