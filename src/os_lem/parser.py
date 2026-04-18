"""Strict parser and normalizer for the frozen v1 input subset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
import numpy as np

from .driver import normalize_driver
from .elements.radiator import default_radiation_space_for_model, normalize_radiation_space
from .errors import SchemaError, ValidationError
from .model import (
    DuctElement,
    NormalizedModel,
    Observation,
    RadiatorElement,
    VolumeElement,
    Waveguide1DElement,
)
from .topology import validate_topology
from .units import parse_value

_TOP_LEVEL_ALLOWED = {"driver", "elements", "observations", "output", "meta"}

_ALLOWED_ELEMENT_TYPES = {"volume", "duct", "waveguide_1d", "radiator"}
_ALLOWED_RADIATOR_MODELS = {"infinite_baffle_piston", "unflanged_piston", "flanged_piston"}
_ALLOWED_OBSERVATIONS = {
    "input_impedance",
    "spl",
    "spl_sum",
    "cone_displacement",
    "cone_velocity",
    "element_volume_velocity",
    "element_particle_velocity",
    "node_pressure",
    "line_profile",
    "group_delay",
}

_VOLUME_KEYS = {"id", "type", "node", "value"}
_DUCT_KEYS = {"id", "type", "node_a", "node_b", "length", "area", "loss"}
_WAVEGUIDE_KEYS = {
    "id",
    "type",
    "node_a",
    "node_b",
    "length",
    "area_start",
    "area_end",
    "profile",
    "segments",
    "loss",
}
_RADIATOR_KEYS = {"id", "type", "node", "model", "area"}


def load_model(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SchemaError("Top-level YAML object must be a mapping")
    return data


def _require_top_level(data: dict[str, Any]) -> None:
    unknown = sorted(set(data.keys()) - _TOP_LEVEL_ALLOWED)
    if unknown:
        raise SchemaError(f"Unknown top-level fields: {unknown}")
    if "driver" not in data:
        raise SchemaError("Missing top-level 'driver'")
    if "elements" not in data:
        raise SchemaError("Missing top-level 'elements'")
    if "observations" not in data:
        raise SchemaError("Missing top-level 'observations'")


def _require_positive(name: str, value: float) -> None:
    if value <= 0.0:
        raise ValidationError(f"{name} must be > 0, got {value!r}")


def _validate_radiation_space_field(space: Any, context: str) -> str:
    if not isinstance(space, str):
        raise ValidationError(f"{context} radiation_space must be a string")
    try:
        return normalize_radiation_space(space)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


def _normalize_element(raw: dict[str, Any]):
    etype = raw.get("type")
    if etype not in _ALLOWED_ELEMENT_TYPES:
        raise ValidationError(f"Unsupported element type: {etype!r}")

    if etype == "volume":
        unknown = sorted(set(raw.keys()) - _VOLUME_KEYS)
        if unknown:
            raise ValidationError(f"Unknown volume fields: {unknown}")
        for req in ("id", "type", "node", "value"):
            if req not in raw:
                raise ValidationError(f"Missing required volume field: {req}")
        value_m3 = parse_value(raw["value"])
        _require_positive(f"volume[{raw['id']}].value", value_m3)
        return VolumeElement(id=str(raw["id"]), node=str(raw["node"]), value_m3=value_m3)

    if etype == "duct":
        unknown = sorted(set(raw.keys()) - _DUCT_KEYS)
        if unknown:
            raise ValidationError(f"Unknown duct fields: {unknown}")
        for req in ("id", "type", "node_a", "node_b", "length", "area"):
            if req not in raw:
                raise ValidationError(f"Missing required duct field: {req}")
        length_m = parse_value(raw["length"])
        area_m2 = parse_value(raw["area"])
        _require_positive(f"duct[{raw['id']}].length", length_m)
        _require_positive(f"duct[{raw['id']}].area", area_m2)
        loss = None
        if "loss" in raw and raw["loss"] is not None:
            raise ValidationError("duct.loss is reserved for future work and not supported in the current checkpoint")
        return DuctElement(
            id=str(raw["id"]),
            node_a=str(raw["node_a"]),
            node_b=str(raw["node_b"]),
            length_m=length_m,
            area_m2=area_m2,
            loss=loss,
        )

    if etype == "waveguide_1d":
        unknown = sorted(set(raw.keys()) - _WAVEGUIDE_KEYS)
        if unknown:
            raise ValidationError(f"Unknown waveguide_1d fields: {unknown}")
        for req in ("id", "type", "node_a", "node_b", "length", "area_start", "area_end", "profile"):
            if req not in raw:
                raise ValidationError(f"Missing required waveguide_1d field: {req}")
        length_m = parse_value(raw["length"])
        area_start_m2 = parse_value(raw["area_start"])
        area_end_m2 = parse_value(raw["area_end"])
        segments = int(raw.get("segments", 8))
        _require_positive(f"waveguide_1d[{raw['id']}].length", length_m)
        _require_positive(f"waveguide_1d[{raw['id']}].area_start", area_start_m2)
        _require_positive(f"waveguide_1d[{raw['id']}].area_end", area_end_m2)
        if segments <= 0:
            raise ValidationError(f"waveguide_1d[{raw['id']}].segments must be > 0")
        loss = float(raw["loss"]) if "loss" in raw and raw["loss"] is not None else None
        if loss is not None:
            if loss < 0.0:
                raise ValidationError(f"waveguide_1d[{raw['id']}].loss must be >= 0")
        profile = raw.get("profile", "conical")
        if not isinstance(profile, str):
            raise ValidationError(f"waveguide_1d[{raw['id']}].profile must be a string")
        if profile not in {"conical", "exponential", "tractrix"}:
            raise ValidationError("v1 waveguide_1d supports only profile: conical, exponential, tractrix")
        if profile == "tractrix" and area_end_m2 < area_start_m2:
            raise ValidationError(f"waveguide_1d[{raw['id']}].tractrix requires area_end >= area_start")
        return Waveguide1DElement(
            id=str(raw["id"]),
            node_a=str(raw["node_a"]),
            node_b=str(raw["node_b"]),
            length_m=length_m,
            area_start_m2=area_start_m2,
            area_end_m2=area_end_m2,
            profile=profile,
            segments=segments,
            loss=loss,
        )

    unknown = sorted(set(raw.keys()) - _RADIATOR_KEYS)
    if unknown:
        raise ValidationError(f"Unknown radiator fields: {unknown}")
    for req in ("id", "type", "node", "model", "area"):
        if req not in raw:
            raise ValidationError(f"Missing required radiator field: {req}")
    if raw["model"] not in _ALLOWED_RADIATOR_MODELS:
        raise ValidationError(f"Unsupported radiator model: {raw['model']!r}")
    area_m2 = parse_value(raw["area"])
    _require_positive(f"radiator[{raw['id']}].area", area_m2)
    return RadiatorElement(
        id=str(raw["id"]),
        node=str(raw["node"]),
        model=str(raw["model"]),
        area_m2=area_m2,
    )


def _normalize_observation(raw: dict[str, Any]) -> Observation:
    if "id" not in raw:
        raise ValidationError("Observation missing required field: id")
    if "type" not in raw:
        raise ValidationError(f"Observation {raw['id']!r} missing required field: type")
    if raw["type"] not in _ALLOWED_OBSERVATIONS:
        raise ValidationError(f"Unsupported observation type: {raw['type']!r}")
    return Observation(id=str(raw["id"]), type=str(raw["type"]), data=dict(raw))


def normalize_model(data: dict[str, Any]) -> tuple[NormalizedModel, list[str]]:
    _require_top_level(data)

    meta = data.get("meta", {})
    if meta is not None and not isinstance(meta, dict):
        raise SchemaError("Top-level 'meta' must be a mapping when present")
    if isinstance(meta, dict) and "radiation_space" in meta:
        _validate_radiation_space_field(meta["radiation_space"], "meta")

    driver_raw = data["driver"]
    if not isinstance(driver_raw, dict):
        raise SchemaError("Top-level 'driver' must be a mapping")

    elements_raw = data["elements"]
    observations_raw = data["observations"]
    if not isinstance(elements_raw, list):
        raise SchemaError("'elements' must be a list")
    if not isinstance(observations_raw, list):
        raise SchemaError("'observations' must be a list")

    warnings: list[str] = []

    driver, driver_warnings = normalize_driver(driver_raw)
    warnings.extend(driver_warnings)

    ids: set[str] = {driver.id}
    node_order: list[str] = []
    seen_nodes: set[str] = set()

    def add_node(name: str) -> None:
        if name not in seen_nodes:
            seen_nodes.add(name)
            node_order.append(name)

    add_node(driver.node_front)
    add_node(driver.node_rear)

    volumes = []
    ducts = []
    waveguides = []
    radiators = []

    for raw in elements_raw:
        if not isinstance(raw, dict):
            raise SchemaError("Each element entry must be a mapping")
        elem = _normalize_element(raw)
        if elem.id in ids:
            raise ValidationError(f"Duplicate id detected: {elem.id}")
        ids.add(elem.id)

        if hasattr(elem, "node"):
            add_node(elem.node)
        if hasattr(elem, "node_a"):
            add_node(elem.node_a)
        if hasattr(elem, "node_b"):
            add_node(elem.node_b)

        if isinstance(elem, VolumeElement):
            volumes.append(elem)
        elif isinstance(elem, DuctElement):
            ducts.append(elem)
        elif isinstance(elem, Waveguide1DElement):
            waveguides.append(elem)
        elif isinstance(elem, RadiatorElement):
            radiators.append(elem)

    observations = []
    for raw in observations_raw:
        if not isinstance(raw, dict):
            raise SchemaError("Each observation entry must be a mapping")
        obs = _normalize_observation(raw)
        if obs.id in ids:
            raise ValidationError(f"Duplicate id detected: {obs.id}")
        ids.add(obs.id)
        observations.append(obs)

    model = NormalizedModel(
        driver=driver,
        volumes=volumes,
        ducts=ducts,
        waveguides=waveguides,
        radiators=radiators,
        observations=observations,
        node_order=node_order,
        metadata=dict(data.get("meta", {})),
    )

    _validate_observation_references(model)
    warnings.extend(_collect_observation_warnings(model))
    validate_topology(model)

    return model, warnings


def _validate_observation_references(model: NormalizedModel) -> None:
    element_ids = {e.id for e in model.volumes + model.ducts + model.waveguides + model.radiators}
    duct_ids = {e.id for e in model.ducts}
    waveguide_ids = {e.id for e in model.waveguides}
    radiator_ids = {e.id for e in model.radiators}
    supported_element_observable_ids = duct_ids | waveguide_ids | radiator_ids
    obs_ids = {o.id for o in model.observations}
    node_ids = set(model.node_order)
    driver_id = model.driver.id

    for obs in model.observations:
        data = obs.data
        otype = obs.type

        if otype == "input_impedance":
            target = data.get("target")
            if target != driver_id:
                raise ValidationError(f"Observation {obs.id!r} must target driver id {driver_id!r}")

        elif otype in {"cone_velocity", "cone_displacement"}:
            target = data.get("target")
            if target != driver_id:
                raise ValidationError(f"Observation {obs.id!r} must target driver id {driver_id!r}")

        elif otype == "node_pressure":
            if data.get("target") not in node_ids:
                raise ValidationError(f"Observation {obs.id!r} references missing node target")

        elif otype in {"spl", "element_volume_velocity", "element_particle_velocity", "line_profile"}:
            target = data.get("target")
            if target not in element_ids:
                raise ValidationError(f"Observation {obs.id!r} references missing element target")
            if otype == "spl" and "radiation_space" in data:
                _validate_radiation_space_field(data["radiation_space"], f"observation {obs.id!r}")
            if otype in {"element_volume_velocity", "element_particle_velocity"}:
                if target not in supported_element_observable_ids:
                    raise ValidationError(
                        f"Observation {obs.id!r} requires target element type duct, radiator, or waveguide_1d"
                    )
                location_value = data.get("location")
                location = None if location_value is None else str(location_value).strip()
                if target in waveguide_ids:
                    if location not in {"a", "b"}:
                        raise ValidationError(
                            f"Observation {obs.id!r} requires location 'a' or 'b' for waveguide_1d target {target!r}"
                        )
                elif location not in {None, ""}:
                    raise ValidationError(
                        f"Observation {obs.id!r} does not accept location for target {target!r}"
                    )

        elif otype == "group_delay":
            if data.get("target") not in obs_ids:
                raise ValidationError(f"Observation {obs.id!r} references missing observation target")

        elif otype == "spl_sum":
            if "radiation_space" in data:
                _validate_radiation_space_field(data["radiation_space"], f"observation {obs.id!r}")
            terms = data.get("terms")
            if not isinstance(terms, list) or not terms:
                raise ValidationError(f"Observation {obs.id!r} requires non-empty terms")
            for term in terms:
                if not isinstance(term, dict) or term.get("target") not in element_ids:
                    raise ValidationError(f"Observation {obs.id!r} has invalid spl_sum term target")
                if "radiation_space" in term:
                    _validate_radiation_space_field(term["radiation_space"], f"observation {obs.id!r} term {term.get('target')!r}")



def _resolved_radiation_space_for_term(
    model: NormalizedModel,
    target_to_radiator_model: dict[str, str],
    term: dict[str, Any],
    parent_space: str | None = None,
) -> str | None:
    if "radiation_space" in term:
        return normalize_radiation_space(str(term["radiation_space"]))
    if parent_space is not None:
        return parent_space
    meta_space = model.metadata.get("radiation_space")
    if meta_space is not None:
        return normalize_radiation_space(str(meta_space))
    target = term.get("target")
    if isinstance(target, str) and target in target_to_radiator_model:
        return default_radiation_space_for_model(target_to_radiator_model[target])
    return None


def _collect_observation_warnings(model: NormalizedModel) -> list[str]:
    warnings: list[str] = []
    target_to_radiator_model = {r.id: r.model for r in model.radiators}

    for obs in model.observations:
        if obs.type != "spl_sum":
            continue
        data = obs.data
        parent_space = None
        if "radiation_space" in data:
            parent_space = normalize_radiation_space(str(data["radiation_space"]))
        terms = data.get("terms", [])
        resolved = []
        for term in terms:
            if isinstance(term, dict):
                space = _resolved_radiation_space_for_term(model, target_to_radiator_model, term, parent_space)
                if space is not None:
                    resolved.append(space)
        if resolved and len(set(resolved)) > 1:
            warnings.append(
                f"Observation {obs.id!r} sums sources with different radiation_space values; "
                "low-frequency summation may be unphysical."
            )
    return warnings

def load_and_normalize(path: str | Path) -> tuple[NormalizedModel, list[str]]:
    return normalize_model(load_model(path))
