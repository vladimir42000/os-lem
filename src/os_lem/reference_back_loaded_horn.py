from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import math

import numpy as np

from .api import run_simulation
from .assemble import assemble_system
from .parser import normalize_model
from .reference_rear_chamber_tapped import RearChamberReferenceBundle, load_rear_chamber_reference_bundle
from .solve import radiator_observation_pressure, solve_frequency_sweep

BACK_LOADED_HORN_TOPOLOGY = (
    "one direct front radiator on the driver front node, one rear chamber volume, one explicit rear-port injection path, "
    "one dedicated throat chamber, one blind throat-side sidebranch with a closed end, one direct rear horn leg, and one rear mouth radiator"
)

BACK_LOADED_HORN_LIMITATIONS = (
    "This smoke path reuses the existing TH-family Akabak rear-chamber tapped reference bundle as a bounded family-level comparison, not as a claim that the new back-loaded horn skeleton is a box-identical transcription of that script.",
    "The back-loaded horn skeleton intentionally removes the tapped front injection branch and replaces it with direct front radiation, so absolute impedance and level agreement are not acceptance targets here; the smoke check tracks bounded shared-grid coherence, broad mouth-response shape, and internal branch-balance invariants.",
    "This reference bundle does not include an Akabak input-impedance phase export, so the smoke comparison remains limited to impedance magnitude plus mouth-pressure level / amplitude / phase.",
    "Generated observables CSV entries beyond the shared impedance and mouth-pressure outputs are os-lem-only structural observables because matching Akabak branch-observable exports are not present in this bundle.",
)

NO_FRONTEND_CONTRACT_CHANGE = True
PRESSURE_DB_LOW_BAND_MAX_HZ = 2000.0


@dataclass(slots=True, frozen=True)
class BackLoadedHornComparison:
    frequency_hz: np.ndarray
    akabak_impedance_magnitude_ohm: np.ndarray
    oslem_impedance_magnitude_ohm: np.ndarray
    akabak_pressure_db: np.ndarray
    oslem_pressure_db: np.ndarray
    akabak_pressure_pa: np.ndarray
    oslem_pressure_pa: np.ndarray
    akabak_pressure_phase_deg: np.ndarray
    oslem_pressure_phase_deg: np.ndarray
    metrics: dict[str, float | bool | str]
    limitations: tuple[str, ...]
    topology: str
    observables: dict[str, np.ndarray]


def build_back_loaded_horn_model_dict() -> dict[str, Any]:
    fs_hz = 42.0
    cms_m_per_n = 1.09e-4
    mms_kg = 1.0 / (((2.0 * math.pi * fs_hz) ** 2) * cms_m_per_n)

    return {
        "meta": {"name": "back_loaded_horn_th_family_smoke", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "em_explicit",
            "Re": "5.10 ohm",
            "Le": "1.40 mH",
            "Bl": 29.06,
            "Cms": cms_m_per_n,
            "Rms": 9.66,
            "Mms": mms_kg,
            "Sd": "531.00 cm2",
            "node_front": "front",
            "node_rear": "rear",
            "source_voltage_rms": 2.83,
        },
        "elements": [
            {"id": "rear_chamber", "type": "volume", "node": "rear", "value": "20.00 l"},
            {"id": "throat_chamber", "type": "volume", "node": "throat", "value": "10.00 l"},
            {
                "id": "rear_port",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "inject",
                "length": "10.00 cm",
                "area_start": "38.00 cm2",
                "area_end": "38.00 cm2",
                "profile": "conical",
                "segments": 2,
            },
            {
                "id": "throat_entry",
                "type": "waveguide_1d",
                "node_a": "inject",
                "node_b": "throat",
                "length": "18.83 cm",
                "area_start": "531.00 cm2",
                "area_end": "531.00 cm2",
                "profile": "conical",
                "segments": 2,
            },
            {
                "id": "blind_upstream",
                "type": "waveguide_1d",
                "node_a": "throat",
                "node_b": "throat_side",
                "length": "5.00 cm",
                "area_start": "60.00 cm2",
                "area_end": "70.00 cm2",
                "profile": "conical",
                "segments": 2,
            },
            {
                "id": "blind_downstream",
                "type": "waveguide_1d",
                "node_a": "throat_side",
                "node_b": "blind",
                "length": "15.00 cm",
                "area_start": "70.00 cm2",
                "area_end": "81.34 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "rear_leg",
                "type": "waveguide_1d",
                "node_a": "throat",
                "node_b": "mouth",
                "length": "270.00 cm",
                "area_start": "81.34 cm2",
                "area_end": "686.49 cm2",
                "profile": "conical",
                "segments": 20,
                "loss": 0.03,
            },
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "flanged_piston",
                "area": "531.00 cm2",
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "flanged_piston",
                "area": "686.49 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_front", "type": "node_pressure", "target": "front"},
            {"id": "p_throat", "type": "node_pressure", "target": "throat"},
            {"id": "p_throat_side", "type": "node_pressure", "target": "throat_side"},
            {"id": "p_mouth", "type": "node_pressure", "target": "mouth"},
            {"id": "front_q", "type": "element_volume_velocity", "target": "front_rad"},
            {"id": "rear_leg_q_a", "type": "element_volume_velocity", "target": "rear_leg", "location": "a"},
            {"id": "rear_leg_q_b", "type": "element_volume_velocity", "target": "rear_leg", "location": "b"},
            {"id": "blind_up_q_b", "type": "element_volume_velocity", "target": "blind_upstream", "location": "b"},
            {"id": "blind_down_q_a", "type": "element_volume_velocity", "target": "blind_downstream", "location": "a"},
            {"id": "blind_down_q_b", "type": "element_volume_velocity", "target": "blind_downstream", "location": "b"},
            {"id": "mouth_q", "type": "element_volume_velocity", "target": "mouth_rad"},
            {"id": "spl_total", "type": "spl", "target": "mouth_rad", "distance": "1 m", "radiation_space": "2pi"},
        ],
    }


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    matrix = np.corrcoef(a, b)
    return float(matrix[0, 1])


def _wrapped_phase_delta_deg(a_deg: np.ndarray, b_deg: np.ndarray) -> np.ndarray:
    return (a_deg - b_deg + 180.0) % 360.0 - 180.0


def _shape_normalized_mae(a: np.ndarray, b: np.ndarray) -> float:
    a_scale = max(float(np.max(np.abs(a))), 1.0e-30)
    b_scale = max(float(np.max(np.abs(b))), 1.0e-30)
    return float(np.mean(np.abs((a / a_scale) - (b / b_scale))))


def _centered_mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs((a - np.mean(a)) - (b - np.mean(b)))))


def compare_back_loaded_horn_against_akabak(reference_dir: str | Path) -> BackLoadedHornComparison:
    bundle: RearChamberReferenceBundle = load_rear_chamber_reference_bundle(reference_dir)
    model_dict = build_back_loaded_horn_model_dict()
    model, warnings = normalize_model(model_dict)
    if warnings:
        raise ValueError(f"Back-loaded horn smoke model produced unexpected normalization warnings: {warnings}")
    system = assemble_system(model)
    if len(system.back_loaded_horn_skeletons) != 1:
        raise ValueError("Back-loaded horn smoke model did not assemble exactly one back-loaded horn skeleton")

    api_result = run_simulation(model_dict, bundle.impedance_magnitude_ohm.frequency_hz)
    sweep = solve_frequency_sweep(model, system, bundle.impedance_magnitude_ohm.frequency_hz)
    mouth_pressure = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")

    oslem_zmag = api_result.zin_mag_ohm
    oslem_pressure_pa = np.abs(mouth_pressure)
    oslem_pressure_db = 20.0 * np.log10(np.maximum(oslem_pressure_pa, 1.0e-30) / 2.0e-5)
    oslem_pressure_phase_deg = np.rad2deg(np.unwrap(np.angle(mouth_pressure)))

    low_band_mask = bundle.impedance_magnitude_ohm.frequency_hz <= PRESSURE_DB_LOW_BAND_MAX_HZ

    metrics: dict[str, float | bool | str] = {
        "frequency_grid_shared": bool(np.array_equal(bundle.impedance_magnitude_ohm.frequency_hz, api_result.frequencies_hz)),
        "frequency_point_count": float(bundle.impedance_magnitude_ohm.frequency_hz.size),
        "reference_impedance_phase_available": False,
        "no_frontend_contract_change": NO_FRONTEND_CONTRACT_CHANGE,
        "pressure_db_low_band_max_hz": PRESSURE_DB_LOW_BAND_MAX_HZ,
        "pressure_db_low_band_point_count": float(np.count_nonzero(low_band_mask)),
        "zmag_shape_corr": _corrcoef(oslem_zmag, bundle.impedance_magnitude_ohm.values),
        "zmag_shape_normalized_mae": _shape_normalized_mae(oslem_zmag, bundle.impedance_magnitude_ohm.values),
        "zmag_centered_mae_ohm": _centered_mae(oslem_zmag, bundle.impedance_magnitude_ohm.values),
        "pressure_db_shape_corr": _corrcoef(oslem_pressure_db, bundle.pressure_db.values),
        "pressure_db_shape_normalized_mae": _shape_normalized_mae(oslem_pressure_db, bundle.pressure_db.values),
        "pressure_db_centered_mae": _centered_mae(oslem_pressure_db, bundle.pressure_db.values),
        "pressure_db_low_band_centered_mae": _centered_mae(oslem_pressure_db[low_band_mask], bundle.pressure_db.values[low_band_mask]),
        "pressure_pa_shape_normalized_mae": _shape_normalized_mae(oslem_pressure_pa, bundle.pressure_pa.values),
        "pressure_phase_overall_mae_deg": float(
            np.mean(np.abs(_wrapped_phase_delta_deg(oslem_pressure_phase_deg, bundle.pressure_phase_deg.values)))
        ),
        "blind_closed_end_max_abs_m3_s": float(np.max(np.abs(api_result.series["blind_down_q_b"]))),
        "throat_side_sidebranch_balance_mae_m3_s": float(
            np.mean(np.abs(api_result.series["blind_down_q_a"] - api_result.series["blind_up_q_b"]))
        ),
    }

    observables = {
        "p_front_real_pa": api_result.series["p_front"].real,
        "p_throat_real_pa": api_result.series["p_throat"].real,
        "p_throat_side_real_pa": api_result.series["p_throat_side"].real,
        "p_mouth_real_pa": api_result.series["p_mouth"].real,
        "front_q_mag_m3_s": np.abs(api_result.series["front_q"]),
        "rear_leg_q_a_mag_m3_s": np.abs(api_result.series["rear_leg_q_a"]),
        "rear_leg_q_b_mag_m3_s": np.abs(api_result.series["rear_leg_q_b"]),
        "blind_up_q_b_mag_m3_s": np.abs(api_result.series["blind_up_q_b"]),
        "blind_down_q_a_mag_m3_s": np.abs(api_result.series["blind_down_q_a"]),
        "blind_down_q_b_mag_m3_s": np.abs(api_result.series["blind_down_q_b"]),
        "mouth_q_mag_m3_s": np.abs(api_result.series["mouth_q"]),
    }

    return BackLoadedHornComparison(
        frequency_hz=bundle.impedance_magnitude_ohm.frequency_hz.copy(),
        akabak_impedance_magnitude_ohm=bundle.impedance_magnitude_ohm.values.copy(),
        oslem_impedance_magnitude_ohm=oslem_zmag,
        akabak_pressure_db=bundle.pressure_db.values.copy(),
        oslem_pressure_db=oslem_pressure_db,
        akabak_pressure_pa=bundle.pressure_pa.values.copy(),
        oslem_pressure_pa=oslem_pressure_pa,
        akabak_pressure_phase_deg=bundle.pressure_phase_deg.values.copy(),
        oslem_pressure_phase_deg=oslem_pressure_phase_deg,
        metrics=metrics,
        limitations=BACK_LOADED_HORN_LIMITATIONS,
        topology=BACK_LOADED_HORN_TOPOLOGY,
        observables=observables,
    )


def write_back_loaded_horn_compare_outputs(reference_dir: str | Path, outdir: str | Path) -> BackLoadedHornComparison:
    comparison = compare_back_loaded_horn_against_akabak(reference_dir)
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    compare_csv = out_path / "back_loaded_horn_compare.csv"
    header = (
        "frequency_hz,akabak_impedance_magnitude_ohm,oslem_impedance_magnitude_ohm,"
        "akabak_pressure_db,oslem_pressure_db,akabak_pressure_pa,oslem_pressure_pa,"
        "akabak_pressure_phase_deg,oslem_pressure_phase_deg\n"
    )
    with compare_csv.open("w", encoding="utf-8") as fh:
        fh.write(header)
        for row in zip(
            comparison.frequency_hz,
            comparison.akabak_impedance_magnitude_ohm,
            comparison.oslem_impedance_magnitude_ohm,
            comparison.akabak_pressure_db,
            comparison.oslem_pressure_db,
            comparison.akabak_pressure_pa,
            comparison.oslem_pressure_pa,
            comparison.akabak_pressure_phase_deg,
            comparison.oslem_pressure_phase_deg,
        ):
            fh.write(",".join(f"{float(value):.12g}" for value in row) + "\n")

    observables_csv = out_path / "back_loaded_horn_observables.csv"
    observable_names = tuple(comparison.observables.keys())
    with observables_csv.open("w", encoding="utf-8") as fh:
        fh.write("frequency_hz," + ",".join(observable_names) + "\n")
        for index, frequency_hz in enumerate(comparison.frequency_hz):
            values = [comparison.observables[name][index] for name in observable_names]
            fh.write(",".join([f"{float(frequency_hz):.12g}", *[f"{float(value):.12g}" for value in values]]) + "\n")

    summary = {
        "case": "TH-family back-loaded horn smoke",
        "topology": comparison.topology,
        "no_frontend_contract_change": NO_FRONTEND_CONTRACT_CHANGE,
        "reference_dir": str(reference_dir),
        "generated_files": [compare_csv.name, observables_csv.name],
        "metrics": comparison.metrics,
        "limitations": list(comparison.limitations),
    }
    (out_path / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return comparison
