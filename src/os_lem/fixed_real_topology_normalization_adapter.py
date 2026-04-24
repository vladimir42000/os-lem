"""Bounded v0.8.0 fixed real-topology normalization adapter.

This module makes the frozen v0.8.0 normalization contract executable for one
accepted authored-input family: offset-line / TQWT-style examples that can be
mapped truthfully onto the fixed three-node template defined by
``docs/v0_8_real_topology_normalization_interface_definition.md``.

The adapter is intentionally narrow:
- no arbitrary topology import
- no graph mutation semantics
- no continuous source-position handling
- no multiple resonator semantics
- no solver ownership changes
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

PACKET_VERSION = "v0_8_real_topology_normalization_v1"
FAMILY = "offset_line_tqwt_family"
KERNEL_BOUNDARY = "os_lem.api.run_simulation(model_dict, frequencies_hz)"
TEMPLATE_ID = "offset_line_tqwt_fixed_template_v1"
FIXED_TEMPLATE_NODES = ("throat_chamber", "horn_seg1", "horn_seg2")
SOURCE_SLOTS = ("rear_slot", "throat_slot", "bend_slot")
RESONATOR_SLOTS = ("none", "rear_slot", "throat_slot", "bend_slot")
AMBIGUOUS_SOURCE_KEYS = {"x_attach_norm", "position_m", "source_position", "distance_along_line_m"}
AMBIGUOUS_RESONATOR_KEYS = {"slots", "x_attach_norm", "position_m", "attach_positions"}


class FixedRealTopologyNormalizationError(ValueError):
    """Raised when authored input is outside the accepted fixed contract."""


@dataclass(frozen=True)
class NormalizedPacketSummary:
    """Small read-only view useful to downstream callers and tests."""

    template_id: str
    source_slot: str
    resonator_slot: str
    resonator_present: bool


def _require_mapping(name: str, value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FixedRealTopologyNormalizationError(f"{name} must be a mapping")
    return value


def _require_non_empty_string(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FixedRealTopologyNormalizationError(f"{name} must be a non-empty string")
    return value


def _require_positive_float(name: str, value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise FixedRealTopologyNormalizationError(f"{name} must be numeric") from exc
    if number <= 0.0:
        raise FixedRealTopologyNormalizationError(f"{name} must be > 0")
    return number


def _normalize_segment(segment: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    authored_id = _require_non_empty_string("main_line[].authored_id", segment.get("authored_id"))
    template_node = _require_non_empty_string("main_line[].template_node", segment.get("template_node"))
    if template_node not in FIXED_TEMPLATE_NODES:
        raise FixedRealTopologyNormalizationError(
            f"main_line[].template_node must be one of {FIXED_TEMPLATE_NODES}, got {template_node!r}"
        )

    normalized = {
        "authored_id": authored_id,
        "profile": str(segment.get("profile", "conical")),
        "length_m": _require_positive_float("main_line[].length_m", segment.get("length_m")),
        "area_in_m2": _require_positive_float("main_line[].area_in_m2", segment.get("area_in_m2")),
        "area_out_m2": _require_positive_float("main_line[].area_out_m2", segment.get("area_out_m2")),
    }
    return template_node, normalized


def _normalize_source(source: Mapping[str, Any]) -> dict[str, Any]:
    unknown_ambiguous = AMBIGUOUS_SOURCE_KEYS.intersection(source.keys())
    if unknown_ambiguous:
        key = sorted(unknown_ambiguous)[0]
        raise FixedRealTopologyNormalizationError(
            f"continuous or ambiguous source-position field is out of scope: {key}"
        )

    slot = _require_non_empty_string("source.slot", source.get("slot"))
    if slot not in SOURCE_SLOTS:
        raise FixedRealTopologyNormalizationError(
            f"source.slot must be one of {SOURCE_SLOTS}, got {slot!r}"
        )
    out = {"slot": slot}
    if "authored_label" in source and source["authored_label"] is not None:
        out["authored_label"] = _require_non_empty_string("source.authored_label", source.get("authored_label"))
    return out


def _normalize_resonator(resonator: Mapping[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    if resonator is None:
        resonator = {"present": False, "slot": "none"}

    unknown_ambiguous = AMBIGUOUS_RESONATOR_KEYS.intersection(resonator.keys())
    if unknown_ambiguous:
        key = sorted(unknown_ambiguous)[0]
        raise FixedRealTopologyNormalizationError(
            f"multiple or ambiguous resonator-position field is out of scope: {key}"
        )

    present = bool(resonator.get("present", False))
    slot = resonator.get("slot", "none")
    if slot not in RESONATOR_SLOTS:
        raise FixedRealTopologyNormalizationError(
            f"resonator.slot must be one of {RESONATOR_SLOTS}, got {slot!r}"
        )

    if not present:
        if slot != "none":
            raise FixedRealTopologyNormalizationError(
                "resonator absence must be encoded as present=false with slot='none'"
            )
        return {"slot": "none", "present": False}, {"slot": "none", "present": False, "payload": None}

    if slot == "none":
        raise FixedRealTopologyNormalizationError(
            "present resonator must use exactly one accepted slot and may not use slot='none'"
        )

    payload = {
        "kind": _require_non_empty_string("resonator.kind", resonator.get("kind", "side_pipe")),
        "length_m": _require_positive_float("resonator.length_m", resonator.get("length_m")),
        "area_m2": _require_positive_float("resonator.area_m2", resonator.get("area_m2")),
    }
    if resonator.get("volume_m3") is not None:
        payload["volume_m3"] = _require_positive_float("resonator.volume_m3", resonator.get("volume_m3"))
    if resonator.get("authored_label") is not None:
        payload["authored_label"] = _require_non_empty_string("resonator.authored_label", resonator.get("authored_label"))

    return {"slot": slot, "present": True}, {"slot": slot, "present": True, "payload": payload}


def normalize_fixed_real_topology_authored_input(authored_input: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize one bounded authored offset-line / TQWT-family input into fixed packet form."""
    authored_input = _require_mapping("authored_input", authored_input)

    family = _require_non_empty_string("family", authored_input.get("family"))
    if family != FAMILY:
        raise FixedRealTopologyNormalizationError(f"family must be {FAMILY!r}, got {family!r}")

    authored_authority = _require_mapping("authored_authority", authored_input.get("authored_authority"))
    source_reference = _require_non_empty_string(
        "authored_authority.source_reference", authored_authority.get("source_reference")
    )
    interpretation_notes = authored_authority.get("interpretation_notes", "")
    if interpretation_notes is None:
        interpretation_notes = ""
    elif not isinstance(interpretation_notes, str):
        raise FixedRealTopologyNormalizationError("authored_authority.interpretation_notes must be a string")

    main_line = authored_input.get("main_line")
    if not isinstance(main_line, list) or not main_line:
        raise FixedRealTopologyNormalizationError("main_line must be a non-empty list of authored segments")

    normalized_geometry: dict[str, Any] = {}
    template_mapping: dict[str, str] = {}
    for raw_segment in main_line:
        segment = _require_mapping("main_line[]", raw_segment)
        template_node, payload = _normalize_segment(segment)
        if template_node in normalized_geometry:
            raise FixedRealTopologyNormalizationError(
                f"duplicate template_node mapping is not allowed: {template_node!r}"
            )
        normalized_geometry[template_node] = payload
        template_mapping[template_node] = payload["authored_id"]

    missing = [node for node in FIXED_TEMPLATE_NODES if node not in normalized_geometry]
    if missing:
        raise FixedRealTopologyNormalizationError(
            f"main_line is missing fixed template node mappings for: {', '.join(missing)}"
        )
    extra = [node for node in normalized_geometry if node not in FIXED_TEMPLATE_NODES]
    if extra:
        raise FixedRealTopologyNormalizationError(
            f"main_line includes unsupported template nodes: {', '.join(extra)}"
        )

    source = _normalize_source(_require_mapping("source", authored_input.get("source")))
    resonator_packet, resonator_geometry = _normalize_resonator(
        authored_input.get("resonator") if authored_input.get("resonator") is None else _require_mapping("resonator", authored_input.get("resonator"))
    )

    normalized_geometry["resonator"] = resonator_geometry

    return {
        "packet_version": PACKET_VERSION,
        "family": FAMILY,
        "kernel_boundary": KERNEL_BOUNDARY,
        "template": {
            "template_id": TEMPLATE_ID,
            "nodes": list(FIXED_TEMPLATE_NODES),
            "source_slots": list(SOURCE_SLOTS),
            "resonator_slots": list(RESONATOR_SLOTS),
        },
        "source": source,
        "resonator": resonator_packet,
        "geometry": normalized_geometry,
        "authored_authority": {
            "source_reference": source_reference,
            "interpretation_notes": interpretation_notes,
            "template_mapping": template_mapping,
        },
    }


def summarize_normalized_packet(packet: Mapping[str, Any]) -> NormalizedPacketSummary:
    packet = _require_mapping("packet", packet)
    template = _require_mapping("template", packet.get("template"))
    source = _require_mapping("source", packet.get("source"))
    resonator = _require_mapping("resonator", packet.get("resonator"))
    return NormalizedPacketSummary(
        template_id=_require_non_empty_string("template.template_id", template.get("template_id")),
        source_slot=_require_non_empty_string("source.slot", source.get("slot")),
        resonator_slot=_require_non_empty_string("resonator.slot", resonator.get("slot")),
        resonator_present=bool(resonator.get("present", False)),
    )


_EXAMPLE_AUTHORED_INPUT: dict[str, Any] = {
    "family": FAMILY,
    "authored_authority": {
        "source_reference": "offset_line_tqwt_family_example_v1",
        "interpretation_notes": "bounded baseline example for fixed-template packet normalization",
    },
    "main_line": [
        {
            "authored_id": "rear_chamber_section",
            "template_node": "throat_chamber",
            "profile": "conical",
            "length_m": 0.11,
            "area_in_m2": 0.0018,
            "area_out_m2": 0.0021,
        },
        {
            "authored_id": "pre_bend_main_line",
            "template_node": "horn_seg1",
            "profile": "conical",
            "length_m": 0.42,
            "area_in_m2": 0.0021,
            "area_out_m2": 0.0085,
        },
        {
            "authored_id": "post_bend_main_line",
            "template_node": "horn_seg2",
            "profile": "conical",
            "length_m": 0.37,
            "area_in_m2": 0.0085,
            "area_out_m2": 0.0175,
        },
    ],
    "source": {"slot": "rear_slot", "authored_label": "rear_driver_mount"},
    "resonator": {
        "present": True,
        "slot": "bend_slot",
        "kind": "side_pipe",
        "length_m": 0.18,
        "area_m2": 0.0012,
        "authored_label": "bend_side_pipe",
    },
}


def example_authored_offset_line_tqwt_input() -> dict[str, Any]:
    """Return one bounded authored example in the accepted normalization family."""
    return deepcopy(_EXAMPLE_AUTHORED_INPUT)
