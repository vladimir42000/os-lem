from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_rear_path import (
    build_direct_plus_branched_rear_path_model_dict,
)
from os_lem.reference_direct_plus_branched_split_merge_rear_path import (
    build_direct_plus_branched_split_merge_rear_path_model_dict,
)
from os_lem.reference_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side import (
    build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict,
)
from os_lem.solve import (
    direct_plus_branched_rear_path_front_contribution_pressure,
    direct_plus_branched_rear_path_rear_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_rear_contribution_pressure,
    solve_frequency_sweep,
    summed_radiator_observation_pressure,
)


FREQUENCIES_HZ = np.geomspace(35.0, 1500.0, 28)
GEOMETRY_FACTORS = (0.95, 1.0, 1.05)
SEGMENT_FACTORS = (1, 2)


@dataclass(frozen=True)
class FamilyConfig:
    name: str
    build_model_dict: object
    contract_collection_attr: str
    front_pressure_fn: object
    rear_pressure_fn: object
    perturb_element_ids: tuple[str, ...]


FAMILY_CONFIGS: tuple[FamilyConfig, ...] = (
    FamilyConfig(
        name="direct_plus_branched_rear_path",
        build_model_dict=build_direct_plus_branched_rear_path_model_dict,
        contract_collection_attr="direct_plus_branched_rear_path_contribution_contracts",
        front_pressure_fn=direct_plus_branched_rear_path_front_contribution_pressure,
        rear_pressure_fn=direct_plus_branched_rear_path_rear_contribution_pressure,
        perturb_element_ids=("stem", "rear_main_leg", "rear_aux_leg"),
    ),
    FamilyConfig(
        name="direct_plus_branched_split_merge_rear_path",
        build_model_dict=build_direct_plus_branched_split_merge_rear_path_model_dict,
        contract_collection_attr="direct_plus_branched_split_merge_rear_path_contribution_contracts",
        front_pressure_fn=direct_plus_branched_split_merge_rear_path_front_contribution_pressure,
        rear_pressure_fn=direct_plus_branched_split_merge_rear_path_rear_contribution_pressure,
        perturb_element_ids=("stem", "direct_leg", "split_feed", "shared_exit"),
    ),
    FamilyConfig(
        name="direct_plus_branched_split_merge_rear_path_front_chamber_throat_side",
        build_model_dict=build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict,
        contract_collection_attr="direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts",
        front_pressure_fn=direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_pressure,
        rear_pressure_fn=direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_pressure,
        perturb_element_ids=("stem", "direct_leg", "throat_feed_up", "throat_feed_down", "shared_exit"),
    ),
)


def _scale_metric_string(value: str, factor: float) -> str:
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z0-9^]+)\s*", value)
    if match is None:
        raise AssertionError(f"Unsupported metric string: {value!r}")
    magnitude = float(match.group(1)) * factor
    unit = match.group(2)
    return f"{magnitude:.6g} {unit}"


def _rear_radiator_ids(contract: object) -> tuple[str, ...]:
    if hasattr(contract, "rear_mouth_radiator_ids"):
        return tuple(contract.rear_mouth_radiator_ids)
    ids: list[str] = []
    for attr in ("direct_rear_mouth_radiator_id", "merged_rear_mouth_radiator_id", "rear_mouth_radiator_id"):
        if hasattr(contract, attr):
            ids.append(getattr(contract, attr))
    if not ids:
        raise AssertionError(f"Could not infer rear radiator ids from contract {contract!r}")
    return tuple(ids)


def _build_variant_model_dict(config: FamilyConfig, *, segment_factor: int, geometry_factor: float) -> dict[str, object]:
    model_dict = deepcopy(config.build_model_dict(segment_factor=segment_factor))
    for element in model_dict["elements"]:
        if element["id"] in config.perturb_element_ids:
            element["length"] = _scale_metric_string(element["length"], geometry_factor)
    return model_dict


def _evaluate_variant(config: FamilyConfig, *, segment_factor: int, geometry_factor: float) -> dict[str, object]:
    model_dict = _build_variant_model_dict(config, segment_factor=segment_factor, geometry_factor=geometry_factor)
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    contract = getattr(system, config.contract_collection_attr)[0]
    sweep = solve_frequency_sweep(model, system, FREQUENCIES_HZ)
    result = run_simulation(model_dict, FREQUENCIES_HZ)

    front_pressure = config.front_pressure_fn(sweep, system, contract, 1.0, radiation_space="2pi")
    rear_pressure = config.rear_pressure_fn(sweep, system, contract, 1.0, radiation_space="2pi")
    total_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [{"target": contract.front_radiator_id, "distance": 1.0}] + [
            {"target": rid, "distance": 1.0} for rid in _rear_radiator_ids(contract)
        ],
        radiation_space="2pi",
    )
    return {
        "result": result,
        "front_pressure": front_pressure,
        "rear_pressure": rear_pressure,
        "total_pressure": total_pressure,
    }


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(np.asarray(a, dtype=float), np.asarray(b, dtype=float))[0, 1])


def test_stability_envelope_small_geometry_variations_stay_finite_and_decomposable() -> None:
    for config in FAMILY_CONFIGS:
        for factor in GEOMETRY_FACTORS:
            evaluated = _evaluate_variant(config, segment_factor=1, geometry_factor=factor)
            result = evaluated["result"]
            front_pressure = evaluated["front_pressure"]
            rear_pressure = evaluated["rear_pressure"]
            total_pressure = evaluated["total_pressure"]

            np.testing.assert_allclose(front_pressure + rear_pressure, total_pressure, rtol=1e-10, atol=1e-12)
            assert np.all(np.isfinite(result.zin_mag_ohm))
            assert np.all(np.isfinite(result.series["spl_front"]))
            assert np.all(np.isfinite(result.series["spl_rear_sum"]))
            assert np.all(np.isfinite(result.series["spl_total"]))
            assert np.all(np.isfinite(front_pressure.real))
            assert np.all(np.isfinite(front_pressure.imag))
            assert np.all(np.isfinite(rear_pressure.real))
            assert np.all(np.isfinite(rear_pressure.imag))
            assert float(np.max(np.abs(np.diff(result.series["spl_total"])))) < 35.0
            assert float(np.max(np.abs(np.diff(result.zin_mag_ohm)))) < 80.0
            assert float(np.max(np.abs(rear_pressure))) > 0.0
            assert float(np.max(np.abs(front_pressure))) > 0.0


def test_stability_envelope_neighboring_geometry_steps_remain_trend_coherent() -> None:
    for config in FAMILY_CONFIGS:
        evaluations = [
            _evaluate_variant(config, segment_factor=1, geometry_factor=factor)["result"]
            for factor in GEOMETRY_FACTORS
        ]
        for left, right in zip(evaluations, evaluations[1:]):
            total_corr = _corrcoef(left.series["spl_total"], right.series["spl_total"])
            impedance_corr = _corrcoef(left.zin_mag_ohm, right.zin_mag_ohm)
            rear_corr = _corrcoef(left.series["spl_rear_sum"], right.series["spl_rear_sum"])
            assert total_corr > 0.75
            assert impedance_corr > 0.75
            assert rear_corr > 0.65
            assert float(np.max(np.abs(left.series["spl_total"] - right.series["spl_total"]))) < 25.0
            assert float(np.max(np.abs(left.zin_mag_ohm - right.zin_mag_ohm))) < 35.0


def test_minimal_release_surface_is_stable_under_segment_refinement() -> None:
    for config in FAMILY_CONFIGS:
        coarse = _evaluate_variant(config, segment_factor=SEGMENT_FACTORS[0], geometry_factor=1.0)["result"]
        refined = _evaluate_variant(config, segment_factor=SEGMENT_FACTORS[1], geometry_factor=1.0)["result"]

        assert _corrcoef(coarse.series["spl_total"], refined.series["spl_total"]) > 0.85
        assert _corrcoef(coarse.series["spl_rear_sum"], refined.series["spl_rear_sum"]) > 0.8
        assert _corrcoef(coarse.zin_mag_ohm, refined.zin_mag_ohm) > 0.8
        assert float(np.max(np.abs(coarse.series["spl_total"] - refined.series["spl_total"]))) < 18.0
        assert float(np.max(np.abs(coarse.zin_mag_ohm - refined.zin_mag_ohm))) < 25.0
        assert np.all(np.isfinite(coarse.series["spl_total"]))
        assert np.all(np.isfinite(refined.series["spl_total"]))
        assert np.all(np.isfinite(coarse.zin_mag_ohm))
        assert np.all(np.isfinite(refined.zin_mag_ohm))
