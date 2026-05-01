"""POC3 BLH graph-to-handmapped construction-equivalence smoke.

This test is intentionally construction-level only.  It validates and compiles
one graph-defined POC3 back-loaded horn representation, then compares the
compiled construction against the accepted hand-mapped POC3 construction from
``proof/poc3_blh_benchmark_pass1/model.yaml`` on a bounded semantic projection.

It does not run the solver, does not claim POC3 solver equivalence, does not
claim POC3 HornResp parity, and does not replace the accepted hand-mapped POC3
path.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

import pytest
import yaml

from os_lem.acoustic_graph_ir import (
    compile_acoustic_graph_ir_to_model_dict,
    validate_acoustic_graph_ir,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
POC3_MODEL_PATH = REPO_ROOT / "proof" / "poc3_blh_benchmark_pass1" / "model.yaml"


_NUMBER_RE = re.compile(r"^\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*([^#]*)$")
SUPPORTED_GRAPH_PROFILES = {"conical", "exponential", "tractrix", "hyperbolic", "parabolic", "lecleach"}


def _load_poc3_authority_model() -> dict[str, Any]:
    assert POC3_MODEL_PATH.exists(), f"missing accepted POC3 hand-mapped authority: {POC3_MODEL_PATH}"
    data = yaml.safe_load(POC3_MODEL_PATH.read_text())
    assert isinstance(data, dict), "POC3 model.yaml must load as a mapping"
    return data


def _as_component_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, Mapping)]
    if isinstance(value, Mapping):
        result: list[dict[str, Any]] = []
        for key, item in value.items():
            if isinstance(item, Mapping):
                copied = dict(item)
                copied.setdefault("id", str(key))
                result.append(copied)
        return result
    return []


def _all_authority_components(model: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Collect likely construction components without inventing authority data."""

    components: list[dict[str, Any]] = []
    for key in (
        "elements",
        "segments",
        "horn_segments",
        "duct_segments",
        "waveguides",
        "acoustic_chambers",
        "chambers",
        "radiators",
        "radiation_loads",
        "terminations",
    ):
        components.extend(_as_component_list(model.get(key)))

    # Some hand-mapped models keep named chamber/radiator blocks at top level.
    for key, value in model.items():
        if not isinstance(value, Mapping):
            continue
        lower = str(key).lower()
        if any(token in lower for token in ("chamber", "radiator", "radiation", "termination")):
            copied = dict(value)
            copied.setdefault("id", str(key))
            components.append(copied)

    # Preserve first occurrence by id/type/key-like content to avoid comparing
    # the same object twice when top-level convenience blocks mirror elements.
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(components):
        ident = str(item.get("id", f"component_{index}"))
        typ = str(item.get("type", ""))
        key = (ident, typ)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _quantity(value: Any, default_unit: str) -> float:
    """Return value in SI units for the quantities used by this smoke."""

    if isinstance(value, bool):
        raise TypeError(f"boolean is not a quantity: {value!r}")
    if isinstance(value, (int, float)):
        return _convert_unit(float(value), default_unit)
    if not isinstance(value, str):
        raise TypeError(f"unsupported quantity value: {value!r}")

    match = _NUMBER_RE.match(value.replace("²", "2").replace("^", ""))
    if not match:
        raise ValueError(f"cannot parse quantity: {value!r}")
    number = float(match.group(1))
    unit = match.group(2).strip().lower().replace(" ", "") or default_unit
    return _convert_unit(number, unit)


def _convert_unit(number: float, unit: str) -> float:
    normalized = unit.lower().replace(" ", "").replace("²", "2").replace("^", "")
    normalized = {
        "meter": "m",
        "meters": "m",
        "metre": "m",
        "metres": "m",
        "hz": "hz",
        "ohms": "ohm",
        "ohm": "ohm",
        "tm": "tm",
        "ns/m": "ns/m",
        "n*s/m": "ns/m",
        "m/n": "m/n",
        "l": "l",
        "liter": "l",
        "liters": "l",
        "litre": "l",
        "litres": "l",
    }.get(normalized, normalized)

    if normalized == "m":
        return number
    if normalized == "cm":
        return number * 1.0e-2
    if normalized in {"m2", "sqm"}:
        return number
    if normalized in {"cm2", "sqcm"}:
        return number * 1.0e-4
    if normalized == "m3":
        return number
    if normalized in {"l", "dm3"}:
        return number * 1.0e-3
    if normalized == "kg":
        return number
    if normalized == "g":
        return number * 1.0e-3
    if normalized == "h":
        return number
    if normalized == "mh":
        return number * 1.0e-3
    if normalized in {"hz", "ohm", "tm", "m/n", "ns/m"}:
        return number
    # Dimensionless quantities such as Qes/Qms are passed with default unit "".
    if normalized == "":
        return number
    raise ValueError(f"unsupported unit {unit!r} in construction-equivalence smoke")


def _lookup(mapping: Mapping[str, Any], aliases: Iterable[str]) -> Any:
    for alias in aliases:
        if alias in mapping:
            return mapping[alias]
    lower_map = {str(key).lower(): value for key, value in mapping.items()}
    for alias in aliases:
        lowered = alias.lower()
        if lowered in lower_map:
            return lower_map[lowered]
    raise KeyError(f"missing aliases {tuple(aliases)!r}")


def _has_any(mapping: Mapping[str, Any], aliases: Iterable[str]) -> bool:
    try:
        _lookup(mapping, aliases)
    except KeyError:
        return False
    return True


def _driver_block(model: Mapping[str, Any]) -> dict[str, Any]:
    driver = model.get("driver")
    assert isinstance(driver, Mapping), "POC3 hand-mapped authority must contain a driver mapping"
    combined = dict(driver)
    parameters = driver.get("parameters")
    if isinstance(parameters, Mapping):
        combined.update(parameters)
    return combined


def _driver_nodes(driver: Mapping[str, Any]) -> tuple[str, str]:
    front = driver.get("node_front", driver.get("front_node", "driver_front"))
    rear = driver.get("node_rear", driver.get("rear_node", "driver_rear"))
    assert isinstance(front, str) and front, "driver front node must be explicit or use driver_front fallback"
    assert isinstance(rear, str) and rear, "driver rear node must be explicit or use driver_rear fallback"
    assert front != rear, "driver front/rear nodes must not collapse"
    return front, rear


def _canonical_driver_parameters(driver: Mapping[str, Any]) -> dict[str, float]:
    """Return canonical raw driver parameters from raw or TS-classic authority."""

    if _has_any(driver, ("Bl_Tm", "Bl", "BL")) and _has_any(driver, ("Cms_m_per_N", "Cms")):
        return {
            "Sd_m2": _quantity(_lookup(driver, ("Sd_m2", "Sd_cm2", "Sd", "sd")), "m2"),
            "Bl_Tm": _quantity(_lookup(driver, ("Bl_Tm", "Bl", "BL")), "tm"),
            "Cms_m_per_N": _quantity(_lookup(driver, ("Cms_m_per_N", "Cms")), "m/n"),
            "Rms_Ns_per_m": _quantity(_lookup(driver, ("Rms_Ns_per_m", "Rms")), "ns/m"),
            "Mmd_kg": _quantity(_lookup(driver, ("Mmd_kg", "Mmd_g", "Mmd", "Mms_kg", "Mms_g", "Mms")), "kg"),
            "Re_ohm": _quantity(_lookup(driver, ("Re_ohm", "Re")), "ohm"),
            "Le_H": _quantity(_lookup(driver, ("Le_H", "Le_mH", "Le")), "h"),
        }

    # Many accepted os-lem model_dicts store TS-classic parameters.  Derive the
    # equivalent raw parameters only for construction comparison; no solver is run.
    sd_m2 = _quantity(_lookup(driver, ("Sd_m2", "Sd_cm2", "Sd", "sd")), "m2")
    fs_hz = _quantity(_lookup(driver, ("Fs_Hz", "Fs_hz", "Fs")), "hz")
    qes = float(_quantity(_lookup(driver, ("Qes", "qes")), ""))
    qms = float(_quantity(_lookup(driver, ("Qms", "qms")), ""))
    vas_m3 = _quantity(_lookup(driver, ("Vas_m3", "Vas_l", "Vas")), "m3")
    re_ohm = _quantity(_lookup(driver, ("Re_ohm", "Re")), "ohm")
    le_h = _quantity(_lookup(driver, ("Le_H", "Le_mH", "Le")), "h")

    rho0 = 1.184
    c0 = 343.0
    cms = vas_m3 / (rho0 * c0 * c0 * sd_m2 * sd_m2)
    omega = 2.0 * math.pi * fs_hz
    mmd = 1.0 / (omega * omega * cms)
    rms = omega * mmd / qms
    bl = math.sqrt((omega * mmd * re_ohm) / qes)
    return {
        "Sd_m2": sd_m2,
        "Bl_Tm": bl,
        "Cms_m_per_N": cms,
        "Rms_Ns_per_m": rms,
        "Mmd_kg": mmd,
        "Re_ohm": re_ohm,
        "Le_H": le_h,
    }


def _segment_components(components: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, item in enumerate(components):
        typ = str(item.get("type", "")).lower()
        has_segment_shape = all(key in item for key in ("node_a", "node_b")) and (
            _has_any(item, ("length_m", "length_cm", "length"))
            and _has_any(item, ("area_start", "area_a", "area_a_m2", "area_a_cm2"))
            and _has_any(item, ("area_end", "area_b", "area_b_m2", "area_b_cm2"))
        )
        if typ in {"waveguide_1d", "horn_or_duct_segment", "duct", "horn_segment"} or has_segment_shape:
            copied = dict(item)
            copied.setdefault("id", f"poc3_segment_{len(result)}")
            result.append(copied)
    assert result, "POC3 authority must expose at least one horn/duct segment"
    return result


def _chamber_components(components: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in components:
        typ = str(item.get("type", "")).lower()
        ident = str(item.get("id", "")).lower()
        if ("chamber" in typ or "chamber" in ident) and _has_any(item, ("volume_m3", "volume_l", "volume", "Vb", "Vrc", "Vtc")):
            result.append(dict(item))
    return result


def _radiation_components(components: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in components:
        typ = str(item.get("type", "")).lower()
        ident = str(item.get("id", "")).lower()
        if typ in {"radiator", "radiation_load"} or "radiation" in typ or "radiator" in ident or "radiation" in ident:
            if _has_any(item, ("node", "node_a", "node_b")) and _has_any(item, ("area", "area_m2", "area_cm2")):
                result.append(dict(item))
    return result


def _closed_components(components: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in components:
        typ = str(item.get("type", "")).lower()
        ident = str(item.get("id", "")).lower()
        if typ == "closed_termination" or "closed_termination" in ident:
            result.append(dict(item))
    return result


def _normalize_profile(profile: Any) -> str:
    if not profile:
        return "conical"
    normalized = str(profile).strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "linear": "conical",
        "straight": "conical",
        "segment": "conical",
        "segmented": "conical",
        "le_cleach": "lecleach",
        "lecleac_h": "lecleach",
        "lecleac_h": "lecleach",
        "le_cleac_h": "lecleach",
    }
    normalized = aliases.get(normalized, normalized)
    assert normalized in SUPPORTED_GRAPH_PROFILES, f"unsupported POC3 graph profile in authority: {profile!r}"
    return normalized


def _length_m(item: Mapping[str, Any]) -> float:
    if "length_m" in item:
        return _quantity(item["length_m"], "m")
    if "length_cm" in item:
        return _quantity(item["length_cm"], "cm")
    return _quantity(_lookup(item, ("length", "L")), "m")


def _area_m2(item: Mapping[str, Any], start_aliases: tuple[str, ...]) -> float:
    value = _lookup(item, start_aliases)
    default = "cm2" if any(alias.endswith("_cm2") for alias in start_aliases) else "m2"
    return _quantity(value, default)


def _volume_m3(item: Mapping[str, Any]) -> float:
    if "volume_m3" in item:
        return _quantity(item["volume_m3"], "m3")
    if "volume_l" in item:
        return _quantity(item["volume_l"], "l")
    return _quantity(_lookup(item, ("volume", "Vb", "Vrc", "Vtc")), "m3")


def _radiation_space(item: Mapping[str, Any]) -> str:
    raw = str(item.get("radiation_space", "2pi")).strip().lower().replace(" ", "")
    raw = raw.replace("2*pi", "2pi").replace("2π", "2pi")
    assert raw == "2pi", f"POC3 graph anchor currently accepts only 2pi radiation, got {raw!r}"
    return "2pi"


def _poc3_graph_from_authority(model: Mapping[str, Any]) -> dict[str, Any]:
    components = _all_authority_components(model)
    driver = _driver_block(model)
    front_node, rear_node = _driver_nodes(driver)
    driver_params = _canonical_driver_parameters(driver)

    segments = _segment_components(components)
    chambers = _chamber_components(components)
    radiators = _radiation_components(components)
    closed = _closed_components(components)

    nodes: set[str] = {front_node, rear_node}
    elements: list[dict[str, Any]] = [
        {
            "id": str(driver.get("id", "poc3_driver")),
            "type": "electrodynamic_driver",
            "front_node": front_node,
            "rear_node": rear_node,
            "parameters": {
                "Sd_m2": driver_params["Sd_m2"],
                "Bl_Tm": driver_params["Bl_Tm"],
                "Cms_m_per_N": driver_params["Cms_m_per_N"],
                "Rms_Ns_per_m": driver_params["Rms_Ns_per_m"],
                "Mmd_kg": driver_params["Mmd_kg"],
                "Re_ohm": driver_params["Re_ohm"],
                "Le_H": driver_params["Le_H"],
            },
        }
    ]

    for chamber_index, chamber in enumerate(chambers):
        node = str(chamber.get("node", chamber.get("node_a", chamber.get("node_b", rear_node))))
        nodes.add(node)
        elements.append(
            {
                "id": str(chamber.get("id", f"poc3_chamber_{chamber_index}")),
                "type": "acoustic_chamber",
                "node": node,
                "volume_m3": _volume_m3(chamber),
            }
        )

    for index, segment in enumerate(segments):
        node_a = str(segment["node_a"])
        node_b = str(segment["node_b"])
        nodes.update((node_a, node_b))
        elements.append(
            {
                "id": str(segment.get("id", f"poc3_segment_{index}")),
                "type": "horn_or_duct_segment",
                "node_a": node_a,
                "node_b": node_b,
                "length_m": _length_m(segment),
                "area_a_m2": _area_m2(segment, ("area_a_m2", "area_a_cm2", "area_a", "area_start")),
                "area_b_m2": _area_m2(segment, ("area_b_m2", "area_b_cm2", "area_b", "area_end")),
                "profile": _normalize_profile(segment.get("profile", segment.get("flare", "conical"))),
            }
        )

    for index, termination in enumerate(closed):
        node = str(termination.get("node", termination.get("node_a", termination.get("node_b", ""))))
        if not node:
            continue
        nodes.add(node)
        elements.append(
            {
                "id": str(termination.get("id", f"poc3_closed_termination_{index}")),
                "type": "closed_termination",
                "node": node,
            }
        )

    if not radiators:
        # Use the final segment endpoint as an explicit mouth radiation fallback
        # only when the authority does not expose a radiator element. The value
        # is still derived from the accepted hand-mapped construction.
        mouth_segment = segments[-1]
        radiators = [
            {
                "id": "poc3_mouth_radiation_from_final_segment",
                "node": mouth_segment["node_b"],
                "area_m2": _area_m2(mouth_segment, ("area_b_m2", "area_b_cm2", "area_b", "area_end")),
                "radiation_space": "2pi",
            }
        ]

    for index, radiator in enumerate(radiators):
        node = str(radiator.get("node", radiator.get("node_a", radiator.get("node_b"))))
        nodes.add(node)
        elements.append(
            {
                "id": str(radiator.get("id", f"poc3_radiation_{index}")),
                "type": "radiation_load",
                "node": node,
                "area_m2": _area_m2(radiator, ("area_m2", "area_cm2", "area")),
                "radiation_space": _radiation_space(radiator),
            }
        )

    return {
        "metadata": {
            "name": "poc3_blh_graph_to_handmapped_construction_equivalence_smoke",
            "case_id": "poc3_blh_benchmark_pass1",
            "authority_path": "proof/poc3_blh_benchmark_pass1/model.yaml",
            "construction_equivalence_only": True,
        },
        "nodes": [{"id": node_id} for node_id in sorted(nodes)],
        "elements": elements,
    }


def _compile_poc3_graph() -> dict[str, Any]:
    graph = _poc3_graph_from_authority(_load_poc3_authority_model())
    result = compile_acoustic_graph_ir_to_model_dict(graph)
    assert result.is_success is True, result.errors
    assert result.model_dict is not None
    return result.model_dict


def _driver_projection_from_authority(model: Mapping[str, Any]) -> dict[str, Any]:
    driver = _driver_block(model)
    front, rear = _driver_nodes(driver)
    params = _canonical_driver_parameters(driver)
    return {"node_front": front, "node_rear": rear, **params}


def _driver_projection_from_compiled(model: Mapping[str, Any]) -> dict[str, Any]:
    driver = model["driver"]
    params = driver["parameters"]
    return {
        "node_front": driver["node_front"],
        "node_rear": driver["node_rear"],
        "Sd_m2": params["Sd_m2"],
        "Bl_Tm": params["Bl_Tm"],
        "Cms_m_per_N": params["Cms_m_per_N"],
        "Rms_Ns_per_m": params["Rms_Ns_per_m"],
        "Mmd_kg": params["Mmd_kg"],
        "Re_ohm": params["Re_ohm"],
        "Le_H": params["Le_H"],
    }


def _projection_from_authority(model: Mapping[str, Any]) -> dict[str, Any]:
    components = _all_authority_components(model)
    segments = _segment_components(components)
    chambers = _chamber_components(components)
    radiators = _radiation_components(components)
    if not radiators:
        mouth_segment = segments[-1]
        radiators = [
            {
                "id": "poc3_mouth_radiation_from_final_segment",
                "node": mouth_segment["node_b"],
                "area_m2": _area_m2(mouth_segment, ("area_b_m2", "area_b_cm2", "area_b", "area_end")),
                "radiation_space": "2pi",
            }
        ]
    return {
        "driver": _driver_projection_from_authority(model),
        "chambers": sorted(
            [
                {
                    "id": str(item.get("id")),
                    "node": str(item.get("node", item.get("node_a", item.get("node_b", _driver_nodes(_driver_block(model))[1])))),
                    "volume_m3": _volume_m3(item),
                }
                for item in chambers
            ],
            key=lambda item: item["id"],
        ),
        "segments": sorted(
            [
                {
                    "id": str(item.get("id")),
                    "node_a": str(item["node_a"]),
                    "node_b": str(item["node_b"]),
                    "length_m": _length_m(item),
                    "area_a_m2": _area_m2(item, ("area_a_m2", "area_a_cm2", "area_a", "area_start")),
                    "area_b_m2": _area_m2(item, ("area_b_m2", "area_b_cm2", "area_b", "area_end")),
                    "profile": _normalize_profile(item.get("profile", item.get("flare", "conical"))),
                }
                for item in segments
            ],
            key=lambda item: item["id"],
        ),
        "radiation": sorted(
            [
                {
                    "id": str(item.get("id")),
                    "node": str(item.get("node", item.get("node_a", item.get("node_b")))),
                    "area_m2": _area_m2(item, ("area_m2", "area_cm2", "area")),
                    "radiation_space": _radiation_space(item),
                }
                for item in radiators
            ],
            key=lambda item: item["id"],
        ),
    }


def _projection_from_compiled(model: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "driver": _driver_projection_from_compiled(model),
        "chambers": sorted(
            [
                {
                    "id": item["id"],
                    "node": item["node"],
                    "volume_m3": float(item["volume_m3"]),
                }
                for item in model.get("acoustic_chambers", [])
            ],
            key=lambda item: item["id"],
        ),
        "segments": sorted(
            [
                {
                    "id": item["id"],
                    "node_a": item["node_a"],
                    "node_b": item["node_b"],
                    "length_m": _quantity(item["length"], "m"),
                    "area_a_m2": _quantity(item["area_start"], "m2"),
                    "area_b_m2": _quantity(item["area_end"], "m2"),
                    "profile": item["profile"],
                }
                for item in model.get("elements", [])
                if item.get("type") == "waveguide_1d"
            ],
            key=lambda item: item["id"],
        ),
        "radiation": sorted(
            [
                {
                    "id": item["id"],
                    "node": item["node"],
                    "area_m2": _quantity(item["area"], "m2"),
                    "radiation_space": item["radiation_space"],
                }
                for item in model.get("elements", [])
                if item.get("type") == "radiator"
            ],
            key=lambda item: item["id"],
        ),
    }


def _assert_close(actual: float, expected: float, *, rel: float = 1.0e-9, abs_: float = 1.0e-12) -> None:
    assert math.isclose(actual, expected, rel_tol=rel, abs_tol=abs_), (actual, expected)


def _assert_projection_matches(compiled: Mapping[str, Any], authority: Mapping[str, Any]) -> None:
    assert compiled["driver"]["node_front"] == authority["driver"]["node_front"]
    assert compiled["driver"]["node_rear"] == authority["driver"]["node_rear"]
    assert compiled["driver"]["node_front"] != compiled["driver"]["node_rear"]
    for key in ("Sd_m2", "Bl_Tm", "Cms_m_per_N", "Rms_Ns_per_m", "Mmd_kg", "Re_ohm", "Le_H"):
        _assert_close(float(compiled["driver"][key]), float(authority["driver"][key]))

    assert compiled["chambers"] == pytest.approx(authority["chambers"])
    assert [item["id"] for item in compiled["segments"]] == [item["id"] for item in authority["segments"]]
    assert [item["id"] for item in compiled["radiation"]] == [item["id"] for item in authority["radiation"]]

    for compiled_segment, authority_segment in zip(compiled["segments"], authority["segments"], strict=True):
        assert compiled_segment["node_a"] == authority_segment["node_a"]
        assert compiled_segment["node_b"] == authority_segment["node_b"]
        assert compiled_segment["profile"] == authority_segment["profile"]
        _assert_close(compiled_segment["length_m"], authority_segment["length_m"])
        _assert_close(compiled_segment["area_a_m2"], authority_segment["area_a_m2"])
        _assert_close(compiled_segment["area_b_m2"], authority_segment["area_b_m2"])

    for compiled_radiation, authority_radiation in zip(compiled["radiation"], authority["radiation"], strict=True):
        assert compiled_radiation["node"] == authority_radiation["node"]
        assert compiled_radiation["radiation_space"] == authority_radiation["radiation_space"] == "2pi"
        _assert_close(compiled_radiation["area_m2"], authority_radiation["area_m2"])

    assert len(compiled["chambers"]) == len(authority["chambers"])
    for compiled_chamber, authority_chamber in zip(compiled["chambers"], authority["chambers"], strict=True):
        assert compiled_chamber["id"] == authority_chamber["id"]
        assert compiled_chamber["node"] == authority_chamber["node"]
        _assert_close(compiled_chamber["volume_m3"], authority_chamber["volume_m3"])


def test_poc3_graph_validates_and_compiles_without_solver_execution() -> None:
    authority = _load_poc3_authority_model()
    graph = _poc3_graph_from_authority(authority)
    validation = validate_acoustic_graph_ir(graph)
    compiled = compile_acoustic_graph_ir_to_model_dict(graph)

    assert validation.is_valid is True, validation.errors
    assert compiled.is_success is True, compiled.errors
    assert compiled.model_dict is not None
    assert "electrodynamic_driver" in validation.supported_element_types_seen
    assert "horn_or_duct_segment" in validation.supported_element_types_seen
    assert "radiation_load" in validation.supported_element_types_seen
    if _chamber_components(_all_authority_components(authority)):
        assert "acoustic_chamber" in validation.supported_element_types_seen


def test_poc3_graph_matches_handmapped_construction_on_bounded_projection() -> None:
    authority_model = _load_poc3_authority_model()
    compiled_projection = _projection_from_compiled(_compile_poc3_graph())
    authority_projection = _projection_from_authority(authority_model)

    _assert_projection_matches(compiled_projection, authority_projection)


def test_poc3_projection_checks_chambers_horns_driver_and_radiation_explicitly() -> None:
    authority_model = _load_poc3_authority_model()
    projection = _projection_from_authority(authority_model)

    assert projection["driver"]["node_front"] != projection["driver"]["node_rear"]
    assert projection["segments"], "POC3 construction-equivalence projection must include horn/duct segments"
    assert projection["radiation"], "POC3 construction-equivalence projection must include a mouth radiation load"
    # The accepted hand-mapped authority loaded from
    # proof/poc3_blh_benchmark_pass1/model.yaml currently exposes no explicit
    # acoustic_chamber records in the bounded construction projection. Keep the
    # chamber field visible, but report it as absent/uncompared instead of
    # inventing chamber authority that is not present in the hand-mapped source.
    assert "chambers" in projection
    assert projection["chambers"] == []


def test_poc3_graph_to_handmapped_equivalence_does_not_require_raw_dictionary_equality() -> None:
    authority_model = _load_poc3_authority_model()
    compiled_model = _compile_poc3_graph()

    assert compiled_model != authority_model
    assert compiled_model["meta"]["source"] == "acoustic_graph_ir"
    assert compiled_model["meta"]["compiler_skeleton"] is True
    _assert_projection_matches(_projection_from_compiled(compiled_model), _projection_from_authority(authority_model))


def test_no_solver_called_by_poc3_construction_equivalence_path(monkeypatch) -> None:
    import os_lem.api as api

    def fail_if_called(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - must not execute
        raise AssertionError("POC3 graph-to-handmapped construction equivalence must not call run_simulation")

    monkeypatch.setattr(api, "run_simulation", fail_if_called)

    authority_model = _load_poc3_authority_model()
    graph = _poc3_graph_from_authority(authority_model)
    compiled = compile_acoustic_graph_ir_to_model_dict(graph)

    assert validate_acoustic_graph_ir(graph).is_valid is True
    assert compiled.is_success is True
    assert compiled.model_dict is not None
    _assert_projection_matches(_projection_from_compiled(compiled.model_dict), _projection_from_authority(authority_model))
