from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np

from os_lem.api import run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.reference_direct_plus_branched_rear_path import (
    NO_FRONTEND_CONTRACT_CHANGE as BRANCHED_NO_FRONTEND_CONTRACT_CHANGE,
    build_direct_plus_branched_rear_path_model_dict,
)
from os_lem.reference_direct_plus_branched_split_merge_rear_path import (
    NO_FRONTEND_CONTRACT_CHANGE as BRANCHED_SPLIT_MERGE_NO_FRONTEND_CONTRACT_CHANGE,
    build_direct_plus_branched_split_merge_rear_path_model_dict,
)
from os_lem.reference_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side import (
    NO_FRONTEND_CONTRACT_CHANGE as FRONT_CHAMBER_NO_FRONTEND_CONTRACT_CHANGE,
    build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict,
)
from os_lem.solve import (
    direct_plus_branched_rear_path_front_contribution_pressure,
    direct_plus_branched_rear_path_rear_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_front_contribution_pressure,
    direct_plus_branched_split_merge_rear_path_rear_contribution_pressure,
    radiator_observation_pressure,
    solve_frequency_sweep,
    summed_radiator_observation_pressure,
)


FREQUENCIES_HZ = np.array([50.0, 80.0, 125.0, 200.0, 315.0, 500.0])


@dataclass(frozen=True)
class FamilyProbeConfig:
    name: str
    build_model_dict: object
    no_frontend_contract_change: bool
    contract_collection_attr: str
    skeleton_collection_attr: str
    front_pressure_fn: object
    rear_pressure_fn: object


FAMILY_CONFIGS: tuple[FamilyProbeConfig, ...] = (
    FamilyProbeConfig(
        name="direct_plus_branched_rear_path",
        build_model_dict=build_direct_plus_branched_rear_path_model_dict,
        no_frontend_contract_change=BRANCHED_NO_FRONTEND_CONTRACT_CHANGE,
        contract_collection_attr="direct_plus_branched_rear_path_contribution_contracts",
        skeleton_collection_attr="direct_plus_branched_rear_path_skeletons",
        front_pressure_fn=direct_plus_branched_rear_path_front_contribution_pressure,
        rear_pressure_fn=direct_plus_branched_rear_path_rear_contribution_pressure,
    ),
    FamilyProbeConfig(
        name="direct_plus_branched_split_merge_rear_path",
        build_model_dict=build_direct_plus_branched_split_merge_rear_path_model_dict,
        no_frontend_contract_change=BRANCHED_SPLIT_MERGE_NO_FRONTEND_CONTRACT_CHANGE,
        contract_collection_attr="direct_plus_branched_split_merge_rear_path_contribution_contracts",
        skeleton_collection_attr="direct_plus_branched_split_merge_rear_path_skeletons",
        front_pressure_fn=direct_plus_branched_split_merge_rear_path_front_contribution_pressure,
        rear_pressure_fn=direct_plus_branched_split_merge_rear_path_rear_contribution_pressure,
    ),
    FamilyProbeConfig(
        name="direct_plus_branched_split_merge_rear_path_front_chamber_throat_side",
        build_model_dict=build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict,
        no_frontend_contract_change=FRONT_CHAMBER_NO_FRONTEND_CONTRACT_CHANGE,
        contract_collection_attr="direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_contribution_contracts",
        skeleton_collection_attr="direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_skeletons",
        front_pressure_fn=direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_front_contribution_pressure,
        rear_pressure_fn=direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_rear_contribution_pressure,
    ),
)


def _rear_radiator_ids(contract: object) -> tuple[str, ...]:
    if hasattr(contract, "rear_mouth_radiator_ids"):
        return tuple(contract.rear_mouth_radiator_ids)
    ids: list[str] = []
    if hasattr(contract, "direct_rear_mouth_radiator_id"):
        ids.append(contract.direct_rear_mouth_radiator_id)
    if hasattr(contract, "merged_rear_mouth_radiator_id"):
        ids.append(contract.merged_rear_mouth_radiator_id)
    if hasattr(contract, "rear_mouth_radiator_id"):
        ids.append(contract.rear_mouth_radiator_id)
    if not ids:
        raise AssertionError(f"Could not infer rear radiator ids from contract {contract!r}")
    return tuple(ids)


def _normalize_centered(values: np.ndarray) -> np.ndarray:
    centered = values - np.mean(values)
    scale = max(float(np.max(np.abs(centered))), 1.0e-30)
    return centered / scale


def _evaluate_family(config: FamilyProbeConfig) -> dict[str, object]:
    model_dict = config.build_model_dict()
    model, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(model)
    contracts = getattr(system, config.contract_collection_attr)
    skeletons = getattr(system, config.skeleton_collection_attr)
    assert len(contracts) == 1
    assert len(skeletons) == 1

    result = run_simulation(model_dict, FREQUENCIES_HZ)
    sweep = solve_frequency_sweep(model, system, FREQUENCIES_HZ)
    contract = contracts[0]
    rear_radiator_ids = _rear_radiator_ids(contract)

    front_pressure = config.front_pressure_fn(sweep, system, contract, 1.0, radiation_space="2pi")
    rear_pressure = config.rear_pressure_fn(sweep, system, contract, 1.0, radiation_space="2pi")
    expected_front_pressure = radiator_observation_pressure(
        sweep,
        system,
        contract.front_radiator_id,
        1.0,
        radiation_space="2pi",
    )
    expected_rear_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [{"target": rid, "distance": 1.0} for rid in rear_radiator_ids],
        radiation_space="2pi",
    )
    expected_total_pressure = summed_radiator_observation_pressure(
        sweep,
        system,
        [{"target": contract.front_radiator_id, "distance": 1.0}] + [
            {"target": rid, "distance": 1.0} for rid in rear_radiator_ids
        ],
        radiation_space="2pi",
    )

    return {
        "config": config,
        "model": model,
        "system": system,
        "result": result,
        "contract": contract,
        "rear_radiator_ids": rear_radiator_ids,
        "front_pressure": front_pressure,
        "rear_pressure": rear_pressure,
        "expected_front_pressure": expected_front_pressure,
        "expected_rear_pressure": expected_rear_pressure,
        "expected_total_pressure": expected_total_pressure,
    }


def test_multi_family_probe_assembles_and_exposes_consistent_contribution_contracts() -> None:
    for config in FAMILY_CONFIGS:
        evaluated = _evaluate_family(config)
        result = evaluated["result"]
        contract = evaluated["contract"]
        rear_radiator_ids = evaluated["rear_radiator_ids"]

        assert config.no_frontend_contract_change is True
        assert contract.front_radiator_id == "front_rad"
        assert len(rear_radiator_ids) >= 2
        assert len(set(rear_radiator_ids)) == len(rear_radiator_ids)
        assert result.units["spl_front"] == "dB"
        assert result.units["spl_rear_sum"] == "dB"
        assert result.units["spl_total"] == "dB"
        assert np.array_equal(result.frequencies_hz, FREQUENCIES_HZ)
        assert np.all(np.isfinite(result.zin_mag_ohm))
        assert float(np.max(result.zin_mag_ohm) - np.min(result.zin_mag_ohm)) > 0.5


def test_multi_family_probe_preserves_contribution_decomposition_consistency() -> None:
    for config in FAMILY_CONFIGS:
        evaluated = _evaluate_family(config)
        result = evaluated["result"]
        front_pressure = evaluated["front_pressure"]
        rear_pressure = evaluated["rear_pressure"]
        expected_front_pressure = evaluated["expected_front_pressure"]
        expected_rear_pressure = evaluated["expected_rear_pressure"]
        expected_total_pressure = evaluated["expected_total_pressure"]

        np.testing.assert_allclose(front_pressure, expected_front_pressure, rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(rear_pressure, expected_rear_pressure, rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(front_pressure + rear_pressure, expected_total_pressure, rtol=1e-10, atol=1e-12)

        assert np.all(np.isfinite(front_pressure.real))
        assert np.all(np.isfinite(front_pressure.imag))
        assert np.all(np.isfinite(rear_pressure.real))
        assert np.all(np.isfinite(rear_pressure.imag))
        assert np.max(np.abs(rear_pressure)) > 0.0
        assert np.max(np.abs(front_pressure)) > 0.0

        assert not np.allclose(result.series["spl_total"], result.series["spl_front"])
        assert not np.allclose(result.series["spl_total"], result.series["spl_rear_sum"])
        assert not np.allclose(result.series["spl_rear_sum"], result.series["spl_front"])

        rear_minus_front_db = np.asarray(result.series["spl_rear_sum"] - result.series["spl_front"], dtype=float)
        total_minus_front_db = np.asarray(result.series["spl_total"] - result.series["spl_front"], dtype=float)
        assert float(np.max(np.abs(rear_minus_front_db))) > 1.0
        assert float(np.max(np.abs(total_minus_front_db))) > 1.0


def test_multi_family_probe_basic_observable_signatures_are_not_accidentally_identical() -> None:
    evaluated = [_evaluate_family(config) for config in FAMILY_CONFIGS]

    for left, right in combinations(evaluated, 2):
        left_name = left["config"].name
        right_name = right["config"].name

        left_z = _normalize_centered(np.asarray(left["result"].zin_mag_ohm, dtype=float))
        right_z = _normalize_centered(np.asarray(right["result"].zin_mag_ohm, dtype=float))
        left_total = _normalize_centered(np.asarray(left["result"].series["spl_total"], dtype=float))
        right_total = _normalize_centered(np.asarray(right["result"].series["spl_total"], dtype=float))
        left_rear_front = _normalize_centered(np.asarray(left["result"].series["spl_rear_sum"] - left["result"].series["spl_front"], dtype=float))
        right_rear_front = _normalize_centered(np.asarray(right["result"].series["spl_rear_sum"] - right["result"].series["spl_front"], dtype=float))

        assert not np.allclose(left_z, right_z, rtol=1e-4, atol=1e-4), (left_name, right_name)
        assert not np.allclose(left_total, right_total, rtol=1e-4, atol=1e-4), (left_name, right_name)
        assert not np.allclose(left_rear_front, right_rear_front, rtol=1e-4, atol=1e-4), (left_name, right_name)
