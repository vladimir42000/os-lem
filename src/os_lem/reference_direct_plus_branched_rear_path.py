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


DIRECT_PLUS_BRANCHED_REAR_PATH_TOPOLOGY = (
    "one direct front radiator plus one rear stem that branches into two bounded rear exits, each terminated by a radiator"
)

DIRECT_PLUS_BRANCHED_REAR_PATH_LIMITATIONS = (
    "This smoke path uses an internally refined-segmentation version of the same direct-plus-branched-rear-path graph as a bounded repo-native reference surrogate, not an external Akabak parity claim.",
    "Acceptance targets here are shared-grid coherence, stable front/rear branch split behavior, and preserved junction flow balance under refinement rather than exact pointwise equality.",
)

NO_FRONTEND_CONTRACT_CHANGE = True
REFERENCE_REFINEMENT_FACTOR = 2
DEFAULT_FREQUENCIES_HZ = np.geomspace(30.0, 2000.0, 72)


@dataclass(slots=True, frozen=True)
class DirectPlusBranchedRearPathComparison:
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


def build_direct_plus_branched_rear_path_model_dict(*, segment_factor: int = 1) -> dict[str, Any]:
    if segment_factor < 1:
        raise ValueError("segment_factor must be >= 1")

    model = {
        "meta": {"name": "direct_plus_branched_rear_path_smoke", "radiation_space": "2pi"},
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
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "flanged_piston",
                "area": "132 cm2",
            },
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "junction",
                "length": "30 cm",
                "area_start": "90 cm2",
                "area_end": "95 cm2",
                "profile": "conical",
                "segments": 4 * segment_factor,
            },
            {
                "id": "rear_main_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_main",
                "length": "45 cm",
                "area_start": "95 cm2",
                "area_end": "110 cm2",
                "profile": "conical",
                "segments": 6 * segment_factor,
            },
            {
                "id": "rear_aux_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_aux",
                "length": "26 cm",
                "area_start": "40 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 4 * segment_factor,
            },
            {
                "id": "rear_main_rad",
                "type": "radiator",
                "node": "rear_mouth_main",
                "model": "flanged_piston",
                "area": "110 cm2",
            },
            {
                "id": "rear_aux_rad",
                "type": "radiator",
                "node": "rear_mouth_aux",
                "model": "flanged_piston",
                "area": "55 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_junction", "type": "node_pressure", "target": "junction"},
            {"id": "front_q", "type": "element_volume_velocity", "target": "front_rad"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "rear_main_leg", "location": "a"},
            {"id": "aux_q_a", "type": "element_volume_velocity", "target": "rear_aux_leg", "location": "a"},
            {"id": "main_rad_q", "type": "element_volume_velocity", "target": "rear_main_rad"},
            {"id": "aux_rad_q", "type": "element_volume_velocity", "target": "rear_aux_rad"},
            {"id": "spl_front", "type": "spl", "target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_main", "type": "spl", "target": "rear_main_rad", "distance": "1 m", "radiation_space": "2pi"},
            {"id": "spl_aux", "type": "spl", "target": "rear_aux_rad", "distance": "1 m", "radiation_space": "2pi"},
            {
                "id": "spl_rear_sum",
                "type": "spl_sum",
                "radiation_space": "2pi",
                "terms": [
                    {"target": "rear_main_rad", "distance": "1 m"},
                    {"target": "rear_aux_rad", "distance": "1 m"},
                ],
            },
            {
                "id": "spl_total",
                "type": "spl_sum",
                "radiation_space": "2pi",
                "terms": [
                    {"target": "front_rad", "distance": "1 m"},
                    {"target": "rear_main_rad", "distance": "1 m"},
                    {"target": "rear_aux_rad", "distance": "1 m"},
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


def compare_direct_plus_branched_rear_path_against_refined_reference(
    frequencies_hz: np.ndarray | None = None,
) -> DirectPlusBranchedRearPathComparison:
    frequencies = DEFAULT_FREQUENCIES_HZ if frequencies_hz is None else np.asarray(frequencies_hz, dtype=float)

    base_model_dict = build_direct_plus_branched_rear_path_model_dict(segment_factor=1)
    refined_model_dict = build_direct_plus_branched_rear_path_model_dict(segment_factor=REFERENCE_REFINEMENT_FACTOR)

    base_model, base_warnings = normalize_model(base_model_dict)
    refined_model, refined_warnings = normalize_model(refined_model_dict)
    if base_warnings or refined_warnings:
        raise ValueError(
            f"Direct-plus-branched-rear-path smoke model produced unexpected normalization warnings: {base_warnings} / {refined_warnings}"
        )

    base_system = assemble_system(base_model)
    refined_system = assemble_system(refined_model)
    if len(base_system.direct_plus_branched_rear_path_skeletons) != 1:
        raise ValueError("Base smoke model did not assemble exactly one direct-plus-branched-rear-path skeleton")
    if len(refined_system.direct_plus_branched_rear_path_skeletons) != 1:
        raise ValueError("Refined smoke model did not assemble exactly one direct-plus-branched-rear-path skeleton")

    base_result = run_simulation(base_model_dict, frequencies)
    refined_result = run_simulation(refined_model_dict, frequencies)

    base_main_aux_delta_db = base_result.series["spl_main"] - base_result.series["spl_aux"]
    refined_main_aux_delta_db = refined_result.series["spl_main"] - refined_result.series["spl_aux"]
    base_rear_sum_minus_front_db = base_result.series["spl_rear_sum"] - base_result.series["spl_front"]
    base_total_minus_front_db = base_result.series["spl_total"] - base_result.series["spl_front"]

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
        "main_aux_delta_centered_mae": _centered_mae(base_main_aux_delta_db, refined_main_aux_delta_db),
        "junction_branch_balance_mae_m3_s": float(
            np.mean(np.abs(base_result.series["stem_q_b"] - (base_result.series["main_q_a"] + base_result.series["aux_q_a"])))
        ),
        "main_aux_delta_span_db": float(np.max(base_main_aux_delta_db) - np.min(base_main_aux_delta_db)),
        "rear_sum_minus_front_span_db": float(
            np.max(base_rear_sum_minus_front_db) - np.min(base_rear_sum_minus_front_db)
        ),
        "total_minus_front_span_db": float(np.max(base_total_minus_front_db) - np.min(base_total_minus_front_db)),
    }

    observables = {
        "base_p_junction_real_pa": base_result.series["p_junction"].real,
        "base_front_q_mag_m3_s": np.abs(base_result.series["front_q"]),
        "base_stem_q_b_mag_m3_s": np.abs(base_result.series["stem_q_b"]),
        "base_main_q_a_mag_m3_s": np.abs(base_result.series["main_q_a"]),
        "base_aux_q_a_mag_m3_s": np.abs(base_result.series["aux_q_a"]),
        "base_main_rad_q_mag_m3_s": np.abs(base_result.series["main_rad_q"]),
        "base_aux_rad_q_mag_m3_s": np.abs(base_result.series["aux_rad_q"]),
        "base_main_aux_delta_db": base_main_aux_delta_db,
        "base_rear_sum_minus_front_db": base_rear_sum_minus_front_db,
        "base_total_minus_front_db": base_total_minus_front_db,
        "refined_main_aux_delta_db": refined_main_aux_delta_db,
    }

    return DirectPlusBranchedRearPathComparison(
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
        limitations=DIRECT_PLUS_BRANCHED_REAR_PATH_LIMITATIONS,
        topology=DIRECT_PLUS_BRANCHED_REAR_PATH_TOPOLOGY,
        observables=observables,
    )


def write_direct_plus_branched_rear_path_compare_outputs(outdir: str | Path) -> DirectPlusBranchedRearPathComparison:
    comparison = compare_direct_plus_branched_rear_path_against_refined_reference()
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    compare_csv = out_path / "direct_plus_branched_rear_path_compare.csv"
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

    observables_csv = out_path / "direct_plus_branched_rear_path_observables.csv"
    observable_names = tuple(comparison.observables.keys())
    with observables_csv.open("w", encoding="utf-8") as fh:
        fh.write("frequency_hz," + ",".join(observable_names) + "\n")
        for index, frequency_hz in enumerate(comparison.frequency_hz):
            values = [comparison.observables[name][index] for name in observable_names]
            fh.write(",".join([f"{float(frequency_hz):.12g}", *[f"{float(value):.12g}" for value in values]]) + "\n")

    summary = {
        "case": "direct-plus-branched-rear-path smoke",
        "topology": comparison.topology,
        "no_frontend_contract_change": NO_FRONTEND_CONTRACT_CHANGE,
        "generated_files": [compare_csv.name, observables_csv.name],
        "metrics": comparison.metrics,
        "limitations": list(comparison.limitations),
    }
    (out_path / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return comparison
