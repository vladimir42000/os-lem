from __future__ import annotations

import pytest

from os_lem.fixed_real_topology_normalization_adapter import (
    FAMILY,
    FixedRealTopologyNormalizationError,
    example_authored_offset_line_tqwt_input,
    normalize_fixed_real_topology_authored_input,
    summarize_normalized_packet,
)


def test_normalizer_maps_fixed_template_nodes_and_preserves_authored_authority() -> None:
    authored = example_authored_offset_line_tqwt_input()

    packet = normalize_fixed_real_topology_authored_input(authored)

    assert packet["packet_version"] == "v0_8_real_topology_normalization_v1"
    assert packet["family"] == FAMILY
    assert packet["template"]["template_id"] == "offset_line_tqwt_fixed_template_v1"
    assert packet["template"]["nodes"] == ["throat_chamber", "horn_seg1", "horn_seg2"]
    assert list(packet["geometry"].keys())[:3] == ["throat_chamber", "horn_seg1", "horn_seg2"]
    assert packet["authored_authority"]["template_mapping"] == {
        "throat_chamber": "rear_chamber_section",
        "horn_seg1": "pre_bend_main_line",
        "horn_seg2": "post_bend_main_line",
    }
    assert packet["kernel_boundary"] == "os_lem.api.run_simulation(model_dict, frequencies_hz)"


def test_normalizer_encodes_source_slot_as_closed_discrete_token() -> None:
    authored = example_authored_offset_line_tqwt_input()
    authored["source"] = {"slot": "throat_slot", "authored_label": "throat_launch_mount"}

    packet = normalize_fixed_real_topology_authored_input(authored)
    summary = summarize_normalized_packet(packet)

    assert packet["source"] == {"slot": "throat_slot", "authored_label": "throat_launch_mount"}
    assert summary.source_slot == "throat_slot"


@pytest.mark.parametrize("bad_source", [
    {"slot": "rear_slot", "x_attach_norm": 0.31},
    {"slot": "continuous_rear"},
])
def test_normalizer_rejects_unsupported_or_ambiguous_source_semantics(bad_source) -> None:
    authored = example_authored_offset_line_tqwt_input()
    authored["source"] = bad_source

    with pytest.raises(FixedRealTopologyNormalizationError):
        normalize_fixed_real_topology_authored_input(authored)


def test_normalizer_encodes_single_resonator_absence_explicitly() -> None:
    authored = example_authored_offset_line_tqwt_input()
    authored["resonator"] = {"present": False, "slot": "none"}

    packet = normalize_fixed_real_topology_authored_input(authored)

    assert packet["resonator"] == {"slot": "none", "present": False}
    assert packet["geometry"]["resonator"] == {"slot": "none", "present": False, "payload": None}


@pytest.mark.parametrize(
    "bad_resonator",
    [
        {"present": True, "slot": "none", "kind": "side_pipe", "length_m": 0.1, "area_m2": 0.001},
        {"present": False, "slot": "bend_slot"},
        {"present": True, "slot": ["rear_slot", "bend_slot"], "kind": "side_pipe", "length_m": 0.1, "area_m2": 0.001},
        {"present": True, "slot": "bend_slot", "slots": ["rear_slot", "bend_slot"], "kind": "side_pipe", "length_m": 0.1, "area_m2": 0.001},
    ],
)
def test_normalizer_rejects_multiple_or_ambiguous_resonator_semantics(bad_resonator) -> None:
    authored = example_authored_offset_line_tqwt_input()
    authored["resonator"] = bad_resonator

    with pytest.raises(FixedRealTopologyNormalizationError):
        normalize_fixed_real_topology_authored_input(authored)


def test_normalizer_rejects_missing_fixed_template_node_mapping() -> None:
    authored = example_authored_offset_line_tqwt_input()
    authored["main_line"] = authored["main_line"][:2]

    with pytest.raises(FixedRealTopologyNormalizationError):
        normalize_fixed_real_topology_authored_input(authored)


def test_bounded_baseline_example_normalizes_to_expected_fixed_packet_form() -> None:
    authored = example_authored_offset_line_tqwt_input()

    packet = normalize_fixed_real_topology_authored_input(authored)

    assert packet == {
        "packet_version": "v0_8_real_topology_normalization_v1",
        "family": "offset_line_tqwt_family",
        "kernel_boundary": "os_lem.api.run_simulation(model_dict, frequencies_hz)",
        "template": {
            "template_id": "offset_line_tqwt_fixed_template_v1",
            "nodes": ["throat_chamber", "horn_seg1", "horn_seg2"],
            "source_slots": ["rear_slot", "throat_slot", "bend_slot"],
            "resonator_slots": ["none", "rear_slot", "throat_slot", "bend_slot"],
        },
        "source": {"slot": "rear_slot", "authored_label": "rear_driver_mount"},
        "resonator": {"slot": "bend_slot", "present": True},
        "geometry": {
            "throat_chamber": {
                "authored_id": "rear_chamber_section",
                "profile": "conical",
                "length_m": 0.11,
                "area_in_m2": 0.0018,
                "area_out_m2": 0.0021,
            },
            "horn_seg1": {
                "authored_id": "pre_bend_main_line",
                "profile": "conical",
                "length_m": 0.42,
                "area_in_m2": 0.0021,
                "area_out_m2": 0.0085,
            },
            "horn_seg2": {
                "authored_id": "post_bend_main_line",
                "profile": "conical",
                "length_m": 0.37,
                "area_in_m2": 0.0085,
                "area_out_m2": 0.0175,
            },
            "resonator": {
                "slot": "bend_slot",
                "present": True,
                "payload": {
                    "kind": "side_pipe",
                    "length_m": 0.18,
                    "area_m2": 0.0012,
                    "authored_label": "bend_side_pipe",
                },
            },
        },
        "authored_authority": {
            "source_reference": "offset_line_tqwt_family_example_v1",
            "interpretation_notes": "bounded baseline example for fixed-template packet normalization",
            "template_mapping": {
                "throat_chamber": "rear_chamber_section",
                "horn_seg1": "pre_bend_main_line",
                "horn_seg2": "post_bend_main_line",
            },
        },
    }
