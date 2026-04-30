"""Minimal validator skeleton for the v0.9.0 acoustic graph IR.

This module validates graph structure only. It intentionally does not compile
acoustic graph IR into os-lem model dictionaries and does not call the solver.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Mapping, Sequence


SUPPORTED_ELEMENT_TYPES: tuple[str, ...] = (
    "electrodynamic_driver",
    "horn_or_duct_segment",
    "closed_termination",
    "acoustic_chamber",
    "radiation_load",
)

SUPPORTED_HORN_PROFILES: tuple[str, ...] = (
    "conical",
    "exponential",
    "tractrix",
    "hyperbolic",
    "parabolic",
    "lecleach",
)

SUPPORTED_RADIATION_SPACES: tuple[str, ...] = ("2pi", "2π")


@dataclass(frozen=True)
class AcousticGraphValidationResult:
    """Structured result returned by :func:`validate_acoustic_graph_ir`."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    node_count: int = 0
    element_count: int = 0
    supported_element_types_seen: list[str] = field(default_factory=list)


def validate_acoustic_graph_ir(graph: Mapping[str, Any]) -> AcousticGraphValidationResult:
    """Validate the minimal v0.9.0 acoustic graph IR shape.

    The validator is deliberately structural. It checks IDs, references,
    supported primitive element types, required fields, and bounded units. It
    does not compile graph IR and does not run acoustic simulation.
    """

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(graph, Mapping):
        return AcousticGraphValidationResult(
            is_valid=False,
            errors=["graph must be a mapping/dictionary"],
            warnings=[],
            node_count=0,
            element_count=0,
            supported_element_types_seen=[],
        )

    unknown_top_level = set(graph) - {"nodes", "elements", "metadata"}
    for key in sorted(unknown_top_level):
        warnings.append(f"unsupported top-level field is ignored by validator skeleton: {key}")

    metadata = graph.get("metadata", {})
    if metadata is not None and not isinstance(metadata, Mapping):
        errors.append("metadata must be a mapping when present")

    nodes = graph.get("nodes")
    elements = graph.get("elements")

    node_ids = _validate_nodes(nodes, errors, warnings)
    supported_seen = _validate_elements(elements, node_ids, errors, warnings)

    node_count = len(nodes) if isinstance(nodes, list) else 0
    element_count = len(elements) if isinstance(elements, list) else 0

    return AcousticGraphValidationResult(
        is_valid=not errors,
        errors=errors,
        warnings=warnings,
        node_count=node_count,
        element_count=element_count,
        supported_element_types_seen=supported_seen,
    )


def _validate_nodes(nodes: Any, errors: list[str], warnings: list[str]) -> set[str]:
    if not isinstance(nodes, list):
        errors.append("nodes must be a list")
        return set()

    if not nodes:
        errors.append("nodes must not be empty")
        return set()

    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        label = f"nodes[{index}]"
        if not isinstance(node, Mapping):
            errors.append(f"{label} must be a mapping")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if node_id in node_ids:
            errors.append(f"duplicate node id: {node_id}")
        node_ids.add(node_id)

        unknown = set(node) - {"id", "metadata"}
        for key in sorted(unknown):
            warnings.append(f"{label} has unsupported validator-skeleton field: {key}")

    return node_ids


def _validate_elements(
    elements: Any,
    node_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> list[str]:
    if not isinstance(elements, list):
        errors.append("elements must be a list")
        return []

    if not elements:
        errors.append("elements must not be empty")
        return []

    element_ids: set[str] = set()
    supported_seen: list[str] = []

    for index, element in enumerate(elements):
        label = f"elements[{index}]"
        if not isinstance(element, Mapping):
            errors.append(f"{label} must be a mapping")
            continue

        element_id = element.get("id")
        if not isinstance(element_id, str) or not element_id:
            errors.append(f"{label}.id must be a non-empty string")
        elif element_id in element_ids:
            errors.append(f"duplicate element id: {element_id}")
        else:
            element_ids.add(element_id)

        element_type = element.get("type")
        if not isinstance(element_type, str) or not element_type:
            errors.append(f"{label}.type must be a non-empty string")
            continue
        if element_type not in SUPPORTED_ELEMENT_TYPES:
            errors.append(f"unknown element type for {label}: {element_type}")
            continue
        if element_type not in supported_seen:
            supported_seen.append(element_type)

        if element_type == "electrodynamic_driver":
            _validate_electrodynamic_driver(element, node_ids, errors, warnings, label)
        elif element_type == "horn_or_duct_segment":
            _validate_horn_or_duct_segment(element, node_ids, errors, warnings, label)
        elif element_type == "closed_termination":
            _validate_closed_termination(element, node_ids, errors, warnings, label)
        elif element_type == "acoustic_chamber":
            _validate_acoustic_chamber(element, node_ids, errors, warnings, label)
        elif element_type == "radiation_load":
            _validate_radiation_load(element, node_ids, errors, warnings, label)

    return supported_seen


def _validate_electrodynamic_driver(
    element: Mapping[str, Any],
    node_ids: set[str],
    errors: list[str],
    warnings: list[str],
    label: str,
) -> None:
    _warn_unknown_element_fields(element, {"id", "type", "front_node", "rear_node", "parameters", "metadata"}, warnings, label)
    _require_distinct_known_nodes(element, "front_node", "rear_node", node_ids, errors, label)

    parameters = element.get("parameters")
    if not isinstance(parameters, Mapping):
        errors.append(f"{label}.parameters must be a mapping")
        return

    _require_exactly_one_numeric(parameters, ("Sd_cm2", "Sd_m2"), errors, f"{label}.parameters.Sd")
    _require_positive_numeric(parameters, "Bl_Tm", errors, f"{label}.parameters")
    _require_positive_numeric(parameters, "Cms_m_per_N", errors, f"{label}.parameters")
    _require_exactly_one_numeric(parameters, ("Rms_Ns_per_m", "Rms"), errors, f"{label}.parameters.Rms")
    _require_exactly_one_numeric(parameters, ("Mmd_g", "Mmd_kg"), errors, f"{label}.parameters.Mmd")
    _require_positive_numeric(parameters, "Re_ohm", errors, f"{label}.parameters")
    _require_exactly_one_numeric(parameters, ("Le_mH", "Le_H"), errors, f"{label}.parameters.Le")

    supported = {
        "Sd_cm2",
        "Sd_m2",
        "Bl_Tm",
        "Cms_m_per_N",
        "Rms_Ns_per_m",
        "Rms",
        "Mmd_g",
        "Mmd_kg",
        "Re_ohm",
        "Le_mH",
        "Le_H",
    }
    for key in sorted(set(parameters) - supported):
        warnings.append(f"{label}.parameters has unsupported validator-skeleton field: {key}")


def _validate_horn_or_duct_segment(
    element: Mapping[str, Any],
    node_ids: set[str],
    errors: list[str],
    warnings: list[str],
    label: str,
) -> None:
    _warn_unknown_element_fields(
        element,
        {
            "id",
            "type",
            "node_a",
            "node_b",
            "length_cm",
            "length_m",
            "area_a_cm2",
            "area_a_m2",
            "area_b_cm2",
            "area_b_m2",
            "profile",
            "metadata",
        },
        warnings,
        label,
    )
    _require_distinct_known_nodes(element, "node_a", "node_b", node_ids, errors, label)
    _require_exactly_one_numeric(element, ("length_cm", "length_m"), errors, f"{label}.length")
    _require_exactly_one_numeric(element, ("area_a_cm2", "area_a_m2"), errors, f"{label}.area_a")
    _require_exactly_one_numeric(element, ("area_b_cm2", "area_b_m2"), errors, f"{label}.area_b")

    profile = element.get("profile")
    if not isinstance(profile, str) or not profile:
        errors.append(f"{label}.profile must be a non-empty string")
    elif profile not in SUPPORTED_HORN_PROFILES:
        errors.append(f"unsupported horn_or_duct_segment profile for {label}: {profile}")


def _validate_closed_termination(
    element: Mapping[str, Any],
    node_ids: set[str],
    errors: list[str],
    warnings: list[str],
    label: str,
) -> None:
    _warn_unknown_element_fields(element, {"id", "type", "node", "metadata"}, warnings, label)
    _require_known_node(element, "node", node_ids, errors, label)


def _validate_acoustic_chamber(
    element: Mapping[str, Any],
    node_ids: set[str],
    errors: list[str],
    warnings: list[str],
    label: str,
) -> None:
    _warn_unknown_element_fields(element, {"id", "type", "node", "volume_l", "volume_m3", "metadata"}, warnings, label)
    _require_known_node(element, "node", node_ids, errors, label)
    _require_exactly_one_numeric(element, ("volume_l", "volume_m3"), errors, f"{label}.volume")


def _validate_radiation_load(
    element: Mapping[str, Any],
    node_ids: set[str],
    errors: list[str],
    warnings: list[str],
    label: str,
) -> None:
    _warn_unknown_element_fields(
        element,
        {"id", "type", "node", "area_cm2", "area_m2", "radiation_space", "metadata"},
        warnings,
        label,
    )
    _require_known_node(element, "node", node_ids, errors, label)
    _require_exactly_one_numeric(element, ("area_cm2", "area_m2"), errors, f"{label}.area")

    radiation_space = element.get("radiation_space")
    if not isinstance(radiation_space, str) or not radiation_space:
        errors.append(f"{label}.radiation_space must be a non-empty string")
    elif radiation_space not in SUPPORTED_RADIATION_SPACES:
        errors.append(f"unsupported radiation_space for {label}: {radiation_space}")


def _require_known_node(
    element: Mapping[str, Any],
    key: str,
    node_ids: set[str],
    errors: list[str],
    label: str,
) -> None:
    value = element.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"{label}.{key} must be a non-empty string")
    elif value not in node_ids:
        errors.append(f"{label}.{key} references unknown node: {value}")


def _require_distinct_known_nodes(
    element: Mapping[str, Any],
    key_a: str,
    key_b: str,
    node_ids: set[str],
    errors: list[str],
    label: str,
) -> None:
    _require_known_node(element, key_a, node_ids, errors, label)
    _require_known_node(element, key_b, node_ids, errors, label)
    value_a = element.get(key_a)
    value_b = element.get(key_b)
    if isinstance(value_a, str) and isinstance(value_b, str) and value_a and value_a == value_b:
        errors.append(f"{label}.{key_a} and {key_b} must not reference the same node")


def _require_positive_numeric(
    source: Mapping[str, Any],
    key: str,
    errors: list[str],
    label: str,
) -> None:
    value = source.get(key)
    if key not in source:
        errors.append(f"{label}.{key} is required")
    elif not _is_positive_number(value):
        errors.append(f"{label}.{key} must be a positive number")


def _require_exactly_one_numeric(
    source: Mapping[str, Any],
    keys: Sequence[str],
    errors: list[str],
    label: str,
) -> None:
    present = [key for key in keys if key in source]
    if not present:
        errors.append(f"{label} requires exactly one of: {', '.join(keys)}")
        return
    if len(present) > 1:
        errors.append(f"{label} is ambiguous; provide only one of: {', '.join(keys)}")
        return
    key = present[0]
    if not _is_positive_number(source[key]):
        errors.append(f"{label}.{key} must be a positive number")


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and value > 0


def _warn_unknown_element_fields(
    element: Mapping[str, Any],
    supported_fields: set[str],
    warnings: list[str],
    label: str,
) -> None:
    for key in sorted(set(element) - supported_fields):
        warnings.append(f"{label} has unsupported validator-skeleton field: {key}")


@dataclass(frozen=True)
class AcousticGraphCompileResult:
    """Structured result returned by graph-to-existing-model compilation.

    This is a compiler skeleton result.  It proves the bounded graph IR to
    existing os-lem model_dict boundary without running the solver and without
    claiming graph-defined acoustic parity.
    """

    is_success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_dict: dict[str, Any] | None = None
    compiled_node_count: int = 0
    compiled_element_count: int = 0
    compiled_element_ids: list[str] = field(default_factory=list)
    unsupported_element_ids: list[str] = field(default_factory=list)


COMPILED_ELEMENT_TYPES: tuple[str, ...] = (
    "electrodynamic_driver",
    "horn_or_duct_segment",
    "closed_termination",
    "radiation_load",
)


class _CompileError(ValueError):
    """Internal bounded compiler error converted into structured result errors."""



def compile_acoustic_graph_ir_to_model_dict(graph: Mapping[str, Any]) -> AcousticGraphCompileResult:
    """Compile validated v0.9.0 acoustic graph IR to a model_dict-like structure.

    This callable intentionally implements only the first compiler skeleton:

    graph IR -> validator -> bounded existing-model/model_dict representation

    It does not import or call :mod:`os_lem.api`, does not run the solver, and
    does not claim graph-defined GDN13 SPL or impedance parity.  Unsupported or
    ambiguous cases return structured errors instead of silently guessing.
    """

    validation = validate_acoustic_graph_ir(graph)
    if not validation.is_valid:
        return AcousticGraphCompileResult(
            is_success=False,
            errors=["graph validation failed before compilation", *validation.errors],
            warnings=validation.warnings,
            model_dict=None,
            compiled_node_count=validation.node_count,
            compiled_element_count=0,
            compiled_element_ids=[],
            unsupported_element_ids=[],
        )

    errors: list[str] = []
    warnings: list[str] = list(validation.warnings)
    compiled_element_ids: list[str] = []
    unsupported_element_ids: list[str] = []

    nodes = graph["nodes"]
    elements = graph["elements"]
    metadata = dict(graph.get("metadata", {}) or {})

    driver_model: dict[str, Any] | None = None
    compiled_elements: list[dict[str, Any]] = []
    closed_terminations: list[dict[str, Any]] = []

    for element in elements:
        element_id = element["id"]
        element_type = element["type"]
        try:
            if element_type == "electrodynamic_driver":
                if driver_model is not None:
                    raise _CompileError("compiler skeleton supports exactly one electrodynamic_driver")
                driver_model = _compile_electrodynamic_driver(element)
                compiled_element_ids.append(element_id)
            elif element_type == "horn_or_duct_segment":
                compiled_elements.append(_compile_horn_or_duct_segment(element))
                compiled_element_ids.append(element_id)
            elif element_type == "closed_termination":
                closed_terminations.append(_compile_closed_termination(element))
                compiled_element_ids.append(element_id)
            elif element_type == "radiation_load":
                compiled_elements.append(_compile_radiation_load(element))
                compiled_element_ids.append(element_id)
            elif element_type == "acoustic_chamber":
                unsupported_element_ids.append(element_id)
                errors.append(
                    f"element {element_id!r} is structurally valid but acoustic_chamber has no accepted compiler target yet"
                )
            else:
                # The validator should catch this first; retain an explicit
                # compiler guard so unknowns never pass silently.
                unsupported_element_ids.append(element_id)
                errors.append(f"element {element_id!r} has unsupported compiler element type: {element_type}")
        except _CompileError as exc:
            errors.append(f"element {element_id!r} compile error: {exc}")

    if driver_model is None:
        errors.append("compiler skeleton requires exactly one electrodynamic_driver")

    model_dict: dict[str, Any] | None = None
    if not errors:
        model_dict = {
            "meta": {
                "name": metadata.get("name", "acoustic_graph_ir_compiler_skeleton_model"),
                "source": "acoustic_graph_ir",
                "acoustic_graph_ir_version": "v0.9.0",
                "compiler_skeleton": True,
                "graph_metadata": metadata,
                "non_claims": [
                    "compiler skeleton only",
                    "no solver execution from graph IR",
                    "no graph-defined parity claim",
                ],
            },
            "nodes": [dict(node) for node in nodes],
            "driver": driver_model,
            "elements": compiled_elements,
            "closed_terminations": closed_terminations,
            "observations": [],
        }

    return AcousticGraphCompileResult(
        is_success=not errors,
        errors=errors,
        warnings=warnings,
        model_dict=model_dict,
        compiled_node_count=validation.node_count,
        compiled_element_count=len(compiled_element_ids),
        compiled_element_ids=compiled_element_ids,
        unsupported_element_ids=unsupported_element_ids,
    )



def _compile_electrodynamic_driver(element: Mapping[str, Any]) -> dict[str, Any]:
    parameters = element["parameters"]
    return {
        "id": element["id"],
        "type": "electrodynamic_driver",
        "model": "acoustic_graph_ir_driver_skeleton",
        "node_front": element["front_node"],
        "node_rear": element["rear_node"],
        "parameters": {
            "Sd_m2": _canonical_area_value(parameters, "Sd"),
            "Bl_Tm": float(parameters["Bl_Tm"]),
            "Cms_m_per_N": float(parameters["Cms_m_per_N"]),
            "Rms_Ns_per_m": _canonical_one_of(parameters, ("Rms_Ns_per_m", "Rms"), "Rms"),
            "Mmd_kg": _canonical_mass_value(parameters),
            "Re_ohm": float(parameters["Re_ohm"]),
            "Le_H": _canonical_inductance_value(parameters),
        },
        "source_graph_element_id": element["id"],
    }



def _compile_horn_or_duct_segment(element: Mapping[str, Any]) -> dict[str, Any]:
    profile = element["profile"]
    if profile not in SUPPORTED_HORN_PROFILES:
        raise _CompileError(f"unsupported horn profile: {profile}")
    return {
        "id": element["id"],
        "type": "waveguide_1d",
        "node_a": element["node_a"],
        "node_b": element["node_b"],
        "length": _format_m(_canonical_length_value(element)),
        "area_start": _format_m2(_canonical_area_value(element, "area_a")),
        "area_end": _format_m2(_canonical_area_value(element, "area_b")),
        "profile": profile,
        "source_graph_element_id": element["id"],
    }



def _compile_closed_termination(element: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": element["id"],
        "type": "closed_termination",
        "node": element["node"],
        "structural_only": True,
        "source_graph_element_id": element["id"],
    }



def _compile_radiation_load(element: Mapping[str, Any]) -> dict[str, Any]:
    radiation_space = element["radiation_space"]
    if radiation_space not in SUPPORTED_RADIATION_SPACES:
        raise _CompileError(f"unsupported radiation_space: {radiation_space}")
    return {
        "id": element["id"],
        "type": "radiator",
        "node": element["node"],
        "model": "unflanged_piston",
        "area": _format_m2(_canonical_area_value(element, "area")),
        "radiation_space": "2pi",
        "source_graph_element_id": element["id"],
    }



def _canonical_length_value(source: Mapping[str, Any]) -> float:
    if "length_m" in source:
        return float(source["length_m"])
    if "length_cm" in source:
        return float(source["length_cm"]) * 1.0e-2
    raise _CompileError("missing supported length unit field; expected length_m or length_cm")



def _canonical_area_value(source: Mapping[str, Any], stem: str) -> float:
    m2_key = f"{stem}_m2"
    cm2_key = f"{stem}_cm2"
    if m2_key in source:
        return float(source[m2_key])
    if cm2_key in source:
        return float(source[cm2_key]) * 1.0e-4
    raise _CompileError(f"missing supported area unit field for {stem}; expected {m2_key} or {cm2_key}")



def _canonical_mass_value(source: Mapping[str, Any]) -> float:
    if "Mmd_kg" in source:
        return float(source["Mmd_kg"])
    if "Mmd_g" in source:
        return float(source["Mmd_g"]) * 1.0e-3
    raise _CompileError("missing supported Mmd unit field; expected Mmd_kg or Mmd_g")



def _canonical_inductance_value(source: Mapping[str, Any]) -> float:
    if "Le_H" in source:
        return float(source["Le_H"])
    if "Le_mH" in source:
        return float(source["Le_mH"]) * 1.0e-3
    raise _CompileError("missing supported Le unit field; expected Le_H or Le_mH")



def _canonical_one_of(source: Mapping[str, Any], keys: Sequence[str], label: str) -> float:
    for key in keys:
        if key in source:
            return float(source[key])
    raise _CompileError(f"missing supported {label} field; expected one of: {', '.join(keys)}")



def _format_m(value: float) -> str:
    return f"{value:.12g} m"



def _format_m2(value: float) -> str:
    return f"{value:.12g} m2"
