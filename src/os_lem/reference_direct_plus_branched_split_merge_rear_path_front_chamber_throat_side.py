from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import numpy as np

from .api import run_simulation
from .assemble import assemble_system
from .parser import normalize_model


DIRECT_PLUS_BRANCHED_SPLIT_MERGE_REAR_PATH_FRONT_CHAMBER_THROAT_SIDE_TOPOLOGY = (
    "one direct front radiator plus one rear stem that branches into one bounded direct rear exit and one bounded split/merge rear exit, with one front-chamber throat-side coupling path into the split/merge leg"
)

DIRECT_PLUS_BRANCHED_SPLIT_MERGE_REAR_PATH_FRONT_CHAMBER_THROAT_SIDE_LIMITATIONS = (
    "This smoke path uses an internally refined-segmentation version of the same direct-plus-branched-split-merge-rear-path front-chamber throat-side coupling graph as a bounded repo-native reference surrogate, not an external Akabak parity claim.",
    "Acceptance targets here are shared-grid coherence, stable direct-vs-merged rear behavior, preserved junction/throat-side/split/merge flow balance under refinement, and bounded coupling behavior rather than exact pointwise equality.",
)

NO_FRONTEND_CONTRACT_CHANGE = True
REFERENCE_REFINEMENT_FACTOR = 2
DEFAULT_FREQUENCIES_HZ = np.geomspace(30.0, 2000.0, 72)


@dataclass(slots=True, frozen=True)
class DirectPlusBranchedSplitMergeRearPathFrontChamberThroatSideComparison:
    frequency_hz: np.ndarray
    base_impedance_magnitude_ohm: np.ndarray
    refined_impedance_magnitude_ohm: np.ndarray
    base_front_spl_db: np.ndarray
    refined_front_spl_db: np.ndarray
    base_rear_sum_spl_db: np.ndarray
    refined_rear_sum_spl_db: np.ndarray
    base_total_spl_db: np.ndarray
    refined_total_spl_db: np.ndarray
    metrics: dict[str, float | bool | str]
    limitations: tuple[str, ...]
    topology: str
    observables: dict[str, np.ndarray]


def build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict(*, segment_factor: int = 1) -> dict[str, Any]:
    if segment_factor < 1:
        raise ValueError("segment_factor must be >= 1")

    model = {
        "meta": {"name": "direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_smoke", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "front",
            "node_rear": "rear",
        },
        "elements": [
            {"id": "front_rad", "type": "radiator", "node": "front", "model": "flanged_piston", "area": "132 cm2"},
            {"id": "front_chamber", "type": "volume", "node": "front", "value": "0.55 l"},
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "junction",
                "length": "20 cm",
                "area_start": "82 cm2",
                "area_end": "88 cm2",
                "profile": "conical",
                "segments": 4 * segment_factor,
            },
            {
                "id": "direct_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_direct",
                "length": "34 cm",
                "area_start": "88 cm2",
                "area_end": "96 cm2",
                "profile": "conical",
                "segments": 5 * segment_factor,
            },
            {
                "id": "throat_feed_up",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "throat_side",
                "length": "14 cm",
                "area_start": "46 cm2",
                "area_end": "52 cm2",
                "profile": "conical",
                "segments": 3 * segment_factor,
            },
            {
                "id": "throat_feed_down",
                "type": "waveguide_1d",
                "node_a": "throat_side",
                "node_b": "split",
                "length": "12 cm",
                "area_start": "52 cm2",
                "area_end": "50 cm2",
                "profile": "conical",
                "segments": 3 * segment_factor,
            },
            {
                "id": "front_coupling",
                "type": "waveguide_1d",
                "node_a": "front",
                "node_b": "throat_side",
                "length": "6 cm",
                "area_start": "18 cm2",
                "area_end": "20 cm2",
                "profile": "conical",
                "segments": 2 * segment_factor,
            },
            {
                "id": "merge_main",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "26 cm",
                "area_start": "50 cm2",
                "area_end": "58 cm2",
                "profile": "conical",
                "segments": 4 * segment_factor,
            },
            {
                "id": "merge_aux",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "31 cm",
                "area_start": "42 cm2",
                "area_end": "47 cm2",
                "profile": "conical",
                "segments": 4 * segment_factor,
            },
            {
                "id": "shared_exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "rear_mouth_merged",
                "length": "22 cm",
                "area_start": "58 cm2",
                "area_end": "62 cm2",
                "profile": "conical",
                "segments": 4 * segment_factor,
            },
            {"id": "rear_direct_rad", "type": "radiator", "node": "rear_mouth_direct", "model": "flanged_piston", "area": "96 cm2"},
            {"id": "rear_merged_rad", "type": "radiator", "node": "rear_mouth_merged", "model": "flanged_piston", "area": "62 cm2"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_front", "type": "node_pressure", "target": "front"},
            {"id": "p_junction", "type": "node_pressure", "target": "junction"},
            {"id": "p_throat_side", "type": "node_pressure", "target": "throat_side"},
            {"id": "p_split", "type": "node_pressure", "target": "split"},
            {"id": "p_merge", "type": "node_pressure", "target": "merge"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "direct_q_a", "type": "element_volume_velocity", "target": "direct_leg", "location": "a"},
            {"id": "direct_q_b", "type": "element_volume_velocity", "target": "direct_leg", "location": "b"},
            {"id": "throat_up_q_a", "type": "element_volume_velocity", "target": "throat_feed_up", "location": "a"},
            {"id": "throat_up_q_b", "type": "element_volume_velocity", "target": "throat_feed_up", "location": "b"},
            {"id": "throat_down_q_a", "type": "element_volume_velocity", "target": "throat_feed_down", "location": "a"},
            {"id": "throat_down_q_b", "type": "element_volume_velocity", "target": "throat_feed_down", "location": "b"},
            {"id": "front_cpl_q_b", "type": "element_volume_velocity", "target": "front_coupling", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "merge_main", "location": "a"},
            {"id": "aux_q_a", "type": "element_volume_velocity", "target": "merge_aux", "location": "a"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "merge_main", "location": "b"},
            {"id": "aux_q_b", "type": "element_volume_velocity", "target": "merge_aux", "location": "b"},
            {"id": "exit_q_a", "type": "element_volume_velocity", "target": "shared_exit", "location": "a"},
            {"id": "direct_rad_q", "type": "element_volume_velocity", "target": "rear_direct_rad"},
            {"id": "merged_rad_q", "type": "element_volume_velocity", "target": "rear_merged_rad"},
            {"id": "spl_front", "type": "spl", "target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_direct_rear", "type": "spl", "target": "rear_direct_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_merged_rear", "type": "spl", "target": "rear_merged_rad", "distance": "1 m", "radiation_space": "2pi"},
            {
                "id": "spl_rear_sum",
                "type": "spl_sum",
                "radiation_space": "2pi",
                "terms": [
                    {"target": "rear_direct_rad", "distance": "1 m"},
                    {"target": "rear_merged_rad", "distance": "1 m"},
                ],
            },
            {
                "id": "spl_total",
                "type": "spl_sum",
                "radiation_space": "2pi",
                "terms": [
                    {"target": "front_rad", "distance": "1 m"},
                    {"target": "rear_direct_rad", "distance": "1 m"},
                    {"target": "rear_merged_rad", "distance": "1 m"},
                ],
            },
        ],
    }
    return deepcopy(model)


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    matrix = np.corrcoef(a, b)
    return float(matrix[0, 1])


def _shape_normalized_mae(a: np.ndarray, b: np.ndarray) -> float:
    a_scale = max(float(np.max(np.abs(a))), 1.0e-30)
    b_scale = max(float(np.max(np.abs(b))), 1.0e-30)
    return float(np.mean(np.abs((a / a_scale) - (b / b_scale))))


def _centered_mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs((a - np.mean(a)) - (b - np.mean(b)))))


def compare_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_against_refined_reference(
    frequencies_hz: np.ndarray | None = None,
) -> DirectPlusBranchedSplitMergeRearPathFrontChamberThroatSideComparison:
    frequencies = DEFAULT_FREQUENCIES_HZ if frequencies_hz is None else np.asarray(frequencies_hz, dtype=float)

    base_model_dict = build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict(segment_factor=1)
    refined_model_dict = build_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_model_dict(segment_factor=REFERENCE_REFINEMENT_FACTOR)

    base_model, base_warnings = normalize_model(base_model_dict)
    refined_model, refined_warnings = normalize_model(refined_model_dict)
    if base_warnings or refined_warnings:
        raise ValueError(
            f"Direct-plus-branched-split-merge rear-path front-chamber throat-side smoke model produced unexpected normalization warnings: {base_warnings} / {refined_warnings}"
        )

    base_system = assemble_system(base_model)
    refined_system = assemble_system(refined_model)
    if len(base_system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_skeletons) != 1:
        raise ValueError("Base smoke model did not assemble exactly one direct-plus-branched-split-merge rear-path front-chamber throat-side coupling skeleton")
    if len(refined_system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_skeletons) != 1:
        raise ValueError("Refined smoke model did not assemble exactly one direct-plus-branched-split-merge rear-path front-chamber throat-side coupling skeleton")

    base_result = run_simulation(base_model_dict, frequencies)
    refined_result = run_simulation(refined_model_dict, frequencies)

    base_direct_merged_delta_db = base_result.series["spl_direct_rear"] - base_result.series["spl_merged_rear"]
    refined_direct_merged_delta_db = refined_result.series["spl_direct_rear"] - refined_result.series["spl_merged_rear"]
    base_rear_sum_minus_front_db = base_result.series["spl_rear_sum"] - base_result.series["spl_front"]
    base_total_minus_front_db = base_result.series["spl_total"] - base_result.series["spl_front"]
    base_front_to_throat_delta_pa = np.abs(base_result.series["p_front"] - base_result.series["p_throat_side"])

    metrics: dict[str, float | bool | str] = {
        "frequency_grid_shared": bool(np.array_equal(base_result.frequencies_hz, refined_result.frequencies_hz)),
        "frequency_point_count": float(frequencies.size),
        "reference_kind": "refined_segmentation_surrogate",
        "reference_refinement_factor": float(REFERENCE_REFINEMENT_FACTOR),
        "no_frontend_contract_change": NO_FRONTEND_CONTRACT_CHANGE,
        "zmag_shape_corr": _corrcoef(base_result.zin_mag_ohm, refined_result.zin_mag_ohm),
        "zmag_shape_normalized_mae": _shape_normalized_mae(base_result.zin_mag_ohm, refined_result.zin_mag_ohm),
        "front_spl_centered_mae": _centered_mae(base_result.series["spl_front"], refined_result.series["spl_front"]),
        "rear_sum_spl_centered_mae": _centered_mae(base_result.series["spl_rear_sum"], refined_result.series["spl_rear_sum"]),
        "total_spl_centered_mae": _centered_mae(base_result.series["spl_total"], refined_result.series["spl_total"]),
        "direct_merged_delta_centered_mae": _centered_mae(base_direct_merged_delta_db, refined_direct_merged_delta_db),
        "junction_balance_mae_m3_s": float(np.mean(np.abs(base_result.series["stem_q_b"] - (base_result.series["direct_q_a"] + base_result.series["throat_up_q_a"])))),
        "throat_side_balance_mae_m3_s": float(np.mean(np.abs(base_result.series["throat_down_q_a"] - (base_result.series["throat_up_q_b"] + base_result.series["front_cpl_q_b"])))),
        "split_balance_mae_m3_s": float(np.mean(np.abs(base_result.series["throat_down_q_b"] - (base_result.series["main_q_a"] + base_result.series["aux_q_a"])))),
        "merge_balance_mae_m3_s": float(np.mean(np.abs(base_result.series["exit_q_a"] - (base_result.series["main_q_b"] + base_result.series["aux_q_b"])))),
        "direct_merged_delta_span_db": float(np.max(base_direct_merged_delta_db) - np.min(base_direct_merged_delta_db)),
        "rear_sum_minus_front_span_db": float(np.max(base_rear_sum_minus_front_db) - np.min(base_rear_sum_minus_front_db)),
        "total_minus_front_span_db": float(np.max(base_total_minus_front_db) - np.min(base_total_minus_front_db)),
        "front_to_throat_pressure_delta_span_pa": float(np.max(base_front_to_throat_delta_pa) - np.min(base_front_to_throat_delta_pa)),
    }

    observables = {
        "base_p_front_real_pa": base_result.series["p_front"].real,
        "base_p_junction_real_pa": base_result.series["p_junction"].real,
        "base_p_throat_side_real_pa": base_result.series["p_throat_side"].real,
        "base_p_split_real_pa": base_result.series["p_split"].real,
        "base_p_merge_real_pa": base_result.series["p_merge"].real,
        "base_stem_q_b_mag_m3_s": np.abs(base_result.series["stem_q_b"]),
        "base_direct_q_a_mag_m3_s": np.abs(base_result.series["direct_q_a"]),
        "base_throat_up_q_a_mag_m3_s": np.abs(base_result.series["throat_up_q_a"]),
        "base_throat_down_q_a_mag_m3_s": np.abs(base_result.series["throat_down_q_a"]),
        "base_front_cpl_q_b_mag_m3_s": np.abs(base_result.series["front_cpl_q_b"]),
        "base_main_q_a_mag_m3_s": np.abs(base_result.series["main_q_a"]),
        "base_aux_q_a_mag_m3_s": np.abs(base_result.series["aux_q_a"]),
        "base_direct_rad_q_mag_m3_s": np.abs(base_result.series["direct_rad_q"]),
        "base_merged_rad_q_mag_m3_s": np.abs(base_result.series["merged_rad_q"]),
        "base_direct_merged_delta_db": base_direct_merged_delta_db,
        "base_rear_sum_minus_front_db": base_rear_sum_minus_front_db,
        "base_total_minus_front_db": base_total_minus_front_db,
        "base_front_to_throat_delta_pa": base_front_to_throat_delta_pa,
        "refined_direct_merged_delta_db": refined_direct_merged_delta_db,
    }

    return DirectPlusBranchedSplitMergeRearPathFrontChamberThroatSideComparison(
        frequency_hz=frequencies.copy(),
        base_impedance_magnitude_ohm=base_result.zin_mag_ohm.copy(),
        refined_impedance_magnitude_ohm=refined_result.zin_mag_ohm.copy(),
        base_front_spl_db=np.asarray(base_result.series["spl_front"], dtype=float).copy(),
        refined_front_spl_db=np.asarray(refined_result.series["spl_front"], dtype=float).copy(),
        base_rear_sum_spl_db=np.asarray(base_result.series["spl_rear_sum"], dtype=float).copy(),
        refined_rear_sum_spl_db=np.asarray(refined_result.series["spl_rear_sum"], dtype=float).copy(),
        base_total_spl_db=np.asarray(base_result.series["spl_total"], dtype=float).copy(),
        refined_total_spl_db=np.asarray(refined_result.series["spl_total"], dtype=float).copy(),
        metrics=metrics,
        limitations=DIRECT_PLUS_BRANCHED_SPLIT_MERGE_REAR_PATH_FRONT_CHAMBER_THROAT_SIDE_LIMITATIONS,
        topology=DIRECT_PLUS_BRANCHED_SPLIT_MERGE_REAR_PATH_FRONT_CHAMBER_THROAT_SIDE_TOPOLOGY,
        observables=observables,
    )


def write_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_compare_outputs(
    outdir: str | Path,
) -> DirectPlusBranchedSplitMergeRearPathFrontChamberThroatSideComparison:
    comparison = compare_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_against_refined_reference()
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    compare_csv = out_path / "direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_compare.csv"
    header = (
        "frequency_hz,base_impedance_magnitude_ohm,refined_impedance_magnitude_ohm,"
        "base_front_spl_db,refined_front_spl_db,base_rear_sum_spl_db,refined_rear_sum_spl_db,"
        "base_total_spl_db,refined_total_spl_db\n"
    )
    with compare_csv.open("w", encoding="utf-8") as fh:
        fh.write(header)
        for row in zip(
            comparison.frequency_hz,
            comparison.base_impedance_magnitude_ohm,
            comparison.refined_impedance_magnitude_ohm,
            comparison.base_front_spl_db,
            comparison.refined_front_spl_db,
            comparison.base_rear_sum_spl_db,
            comparison.refined_rear_sum_spl_db,
            comparison.base_total_spl_db,
            comparison.refined_total_spl_db,
        ):
            fh.write(",".join(f"{float(value):.12g}" for value in row) + "\n")

    observables_csv = out_path / "direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_observables.csv"
    observable_names = tuple(comparison.observables.keys())
    with observables_csv.open("w", encoding="utf-8") as fh:
        fh.write("frequency_hz," + ",".join(observable_names) + "\n")
        for index, frequency_hz in enumerate(comparison.frequency_hz):
            values = [comparison.observables[name][index] for name in observable_names]
            fh.write(",".join([f"{float(frequency_hz):.12g}", *[f"{float(value):.12g}" for value in values]]) + "\n")

    summary = {
        "case": "direct-plus-branched-split-merge-rear-path front-chamber throat-side smoke",
        "topology": comparison.topology,
        "no_frontend_contract_change": NO_FRONTEND_CONTRACT_CHANGE,
        "generated_files": [compare_csv.name, observables_csv.name],
        "metrics": comparison.metrics,
        "limitations": list(comparison.limitations),
    }
    (out_path / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return comparison
