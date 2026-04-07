from __future__ import annotations

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side import (
    build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict,
)


def test_assemble_system_collects_one_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contract() -> None:
    model, warnings = normalize_model(
        build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict()
    )
    assert warnings == []

    assembled = assemble_system(model)

    assert len(assembled.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_skeletons) == 1
    assert len(assembled.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts) == 1

    skeleton = assembled.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_skeletons[0]
    contract = assembled.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts[0]

    assert contract.front_node == skeleton.front_node
    assert contract.front_node_name == "front"
    assert contract.front_radiator_id == "front_rad"
    assert contract.front_chamber_element_id == skeleton.front_chamber_element_id
    assert contract.front_chamber_element_kind == skeleton.front_chamber_element_kind
    assert contract.rear_junction_node == skeleton.junction_node
    assert contract.rear_junction_node_name == "junction"
    assert contract.direct_branch_element_id == skeleton.direct_branch_element_id
    assert contract.direct_rear_mouth_node == skeleton.direct_rear_mouth_node
    assert contract.direct_rear_mouth_radiator_id == "rear_direct_rad"
    assert contract.throat_side_node == skeleton.throat_side_node
    assert contract.throat_side_node_name == "throat_side"
    assert contract.throat_feed_upstream_element_id == skeleton.throat_feed_upstream_element_id
    assert contract.throat_feed_downstream_element_id == skeleton.throat_feed_downstream_element_id
    assert contract.front_coupling_element_id == skeleton.front_coupling_element_id
    assert contract.split_node == skeleton.split_node
    assert contract.split_node_name == "split"
    assert contract.merge_node == skeleton.merge_node
    assert contract.merge_node_name == "merge"
    assert contract.recombined_leg_element_ids == skeleton.recombined_leg_element_ids
    assert contract.shared_exit_element_id == skeleton.shared_exit_element_id
    assert contract.merged_rear_mouth_node == skeleton.merged_rear_mouth_node
    assert contract.merged_rear_mouth_radiator_id == "rear_merged_rad"


def test_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contract_keeps_front_and_rear_radiators_distinct() -> None:
    model, warnings = normalize_model(
        build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict()
    )
    assert warnings == []

    assembled = assemble_system(model)
    contract = assembled.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts[0]

    assert contract.front_radiator_id not in {
        contract.direct_rear_mouth_radiator_id,
        contract.merged_rear_mouth_radiator_id,
    }
    assert contract.direct_rear_mouth_radiator_id != contract.merged_rear_mouth_radiator_id
    assert contract.front_node not in {
        contract.direct_rear_mouth_node,
        contract.merged_rear_mouth_node,
        contract.throat_side_node,
    }
    assert contract.direct_rear_mouth_node != contract.merged_rear_mouth_node
