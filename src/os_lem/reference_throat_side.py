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
from .reference_rear_chamber_tapped import ReferenceSeries, RearChamberReferenceBundle, load_rear_chamber_reference_bundle
from .solve import radiator_observation_pressure, solve_frequency_sweep

THROAT_SIDE_TOPOLOGY = (
    "one rear chamber volume, one explicit rear-port injection branch, one dedicated throat chamber, "
    "one blind throat-side horn segment, one tapped horn path with an interior tap node, one shared downstream exit path, "
    "and one mouth radiator"
)

THROAT_SIDE_LIMITATIONS = (
    "The current supported throat-side topology still approximates the Akabak TH structure because the single driver front couples at the interior tap node rather than through a dedicated throat-chamber-side driver chamber topology.",
    "This reference bundle does not include an Akabak input-impedance phase export, so the smoke comparison is limited to impedance magnitude plus mouth-pressure level / amplitude / phase.",
    "The blind throat-side observables in the generated observables CSV come from os-lem only because matching Akabak blind-segment branch exports are not present in this bundle.",
)

NO_FRONTEND_CONTRACT_CHANGE = True


@dataclass(slots=True, frozen=True)
class ThroatSideComparison:
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


def build_throat_side_model_dict() -> dict[str, Any]:
    fs_hz = 42.0
    cms_m_per_n = 1.09e-4
    mms_kg = 1.0 / (((2.0 * math.pi * fs_hz) ** 2) * cms_m_per_n)

    return {
        "meta": {"name": "throat_side_th_smoke", "radiation_space": "2pi"},
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
            "node_front": "tap",
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
                "id": "blind_segment",
                "type": "waveguide_1d",
                "node_a": "throat",
                "node_b": "blind",
                "length": "20.00 cm",
                "area_start": "60.00 cm2",
                "area_end": "81.34 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "throat",
                "node_b": "split",
                "length": "5.00 cm",
                "area_start": "81.34 cm2",
                "area_end": "81.34 cm2",
                "profile": "conical",
                "segments": 1,
            },
            {
                "id": "main_leg",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "250.00 cm",
                "area_start": "81.34 cm2",
                "area_end": "621.41 cm2",
                "profile": "conical",
                "segments": 16,
                "loss": 0.03,
            },
            {
                "id": "tap_upstream",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "tap",
                "length": "1.00 cm",
                "area_start": "531.00 cm2",
                "area_end": "531.00 cm2",
                "profile": "conical",
                "segments": 1,
            },
            {
                "id": "tap_downstream",
                "type": "waveguide_1d",
                "node_a": "tap",
                "node_b": "merge",
                "length": "250.00 cm",
                "area_start": "60.00 cm2",
                "area_end": "81.34 cm2",
                "profile": "conical",
                "segments": 16,
                "loss": 0.03,
            },
            {
                "id": "exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "mouth",
                "length": "20.00 cm",
                "area_start": "621.41 cm2",
                "area_end": "686.49 cm2",
                "profile": "conical",
                "segments": 4,
                "loss": 0.03,
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
            {"id": "p_throat", "type": "node_pressure", "target": "throat"},
            {"id": "p_blind", "type": "node_pressure", "target": "blind"},
            {"id": "p_tap", "type": "node_pressure", "target": "tap"},
            {"id": "rear_port_q_b", "type": "element_volume_velocity", "target": "rear_port", "location": "b"},
            {"id": "throat_entry_q_a", "type": "element_volume_velocity", "target": "throat_entry", "location": "a"},
            {"id": "blind_q_a", "type": "element_volume_velocity", "target": "blind_segment", "location": "a"},
            {"id": "blind_q_b", "type": "element_volume_velocity", "target": "blind_segment", "location": "b"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "main_leg", "location": "a"},
            {"id": "tap_up_q_a", "type": "element_volume_velocity", "target": "tap_upstream", "location": "a"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "main_leg", "location": "b"},
            {"id": "tap_down_q_b", "type": "element_volume_velocity", "target": "tap_downstream", "location": "b"},
            {"id": "exit_q_a", "type": "element_volume_velocity", "target": "exit", "location": "a"},
            {"id": "exit_q_b", "type": "element_volume_velocity", "target": "exit", "location": "b"},
            {"id": "mouth_rad_q", "type": "element_volume_velocity", "target": "mouth_rad"},
            {"id": "spl_total", "type": "spl", "target": "mouth_rad", "distance": "1 m", "radiation_space": "2pi"},
        ],
    }


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    matrix = np.corrcoef(a, b)
    return float(matrix[0, 1])


def _wrapped_phase_delta_deg(a_deg: np.ndarray, b_deg: np.ndarray) -> np.ndarray:
    return (a_deg - b_deg + 180.0) % 360.0 - 180.0


def compare_throat_side_against_akabak(reference_dir: str | Path) -> ThroatSideComparison:
    bundle: RearChamberReferenceBundle = load_rear_chamber_reference_bundle(reference_dir)
    model_dict = build_throat_side_model_dict()
    model, warnings = normalize_model(model_dict)
    if warnings:
        raise ValueError(f"Throat-side smoke model produced unexpected normalization warnings: {warnings}")
    system = assemble_system(model)
    if len(system.blind_throat_side_segment_topologies) != 1:
        raise ValueError("Throat-side smoke model did not assemble exactly one blind throat-side topology")

    api_result = run_simulation(model_dict, bundle.impedance_magnitude_ohm.frequency_hz)
    sweep = solve_frequency_sweep(model, system, bundle.impedance_magnitude_ohm.frequency_hz)
    mouth_pressure = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")

    oslem_zmag = api_result.zin_mag_ohm
    oslem_pressure_pa = np.abs(mouth_pressure)
    oslem_pressure_db = 20.0 * np.log10(np.maximum(oslem_pressure_pa, 1.0e-30) / 2.0e-5)
    oslem_pressure_phase_deg = np.rad2deg(np.unwrap(np.angle(mouth_pressure)))

    metrics: dict[str, float | bool | str] = {
        "frequency_grid_shared": bool(np.array_equal(bundle.impedance_magnitude_ohm.frequency_hz, api_result.frequencies_hz)),
        "frequency_point_count": float(bundle.impedance_magnitude_ohm.frequency_hz.size),
        "reference_impedance_phase_available": False,
        "no_frontend_contract_change": NO_FRONTEND_CONTRACT_CHANGE,
        "zmag_overall_mae_ohm": float(np.mean(np.abs(oslem_zmag - bundle.impedance_magnitude_ohm.values))),
        "zmag_overall_corr": _corrcoef(oslem_zmag, bundle.impedance_magnitude_ohm.values),
        "pressure_db_overall_mae": float(np.mean(np.abs(oslem_pressure_db - bundle.pressure_db.values))),
        "pressure_db_overall_corr": _corrcoef(oslem_pressure_db, bundle.pressure_db.values),
        "pressure_pa_overall_mae": float(np.mean(np.abs(oslem_pressure_pa - bundle.pressure_pa.values))),
        "pressure_phase_overall_mae_deg": float(
            np.mean(np.abs(_wrapped_phase_delta_deg(oslem_pressure_phase_deg, bundle.pressure_phase_deg.values)))
        ),
        "blind_closed_end_max_abs_m3_s": float(np.max(np.abs(api_result.series["blind_q_b"]))),
    }

    observables = {
        "p_throat_real_pa": api_result.series["p_throat"].real,
        "p_blind_real_pa": api_result.series["p_blind"].real,
        "p_tap_real_pa": api_result.series["p_tap"].real,
        "rear_port_q_b_mag_m3_s": np.abs(api_result.series["rear_port_q_b"]),
        "throat_entry_q_a_mag_m3_s": np.abs(api_result.series["throat_entry_q_a"]),
        "blind_q_a_mag_m3_s": np.abs(api_result.series["blind_q_a"]),
        "blind_q_b_mag_m3_s": np.abs(api_result.series["blind_q_b"]),
        "stem_q_b_mag_m3_s": np.abs(api_result.series["stem_q_b"]),
        "main_q_a_mag_m3_s": np.abs(api_result.series["main_q_a"]),
        "tap_up_q_a_mag_m3_s": np.abs(api_result.series["tap_up_q_a"]),
        "main_q_b_mag_m3_s": np.abs(api_result.series["main_q_b"]),
        "tap_down_q_b_mag_m3_s": np.abs(api_result.series["tap_down_q_b"]),
        "exit_q_a_mag_m3_s": np.abs(api_result.series["exit_q_a"]),
        "exit_q_b_mag_m3_s": np.abs(api_result.series["exit_q_b"]),
        "mouth_rad_q_mag_m3_s": np.abs(api_result.series["mouth_rad_q"]),
    }

    return ThroatSideComparison(
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
        limitations=THROAT_SIDE_LIMITATIONS,
        topology=THROAT_SIDE_TOPOLOGY,
        observables=observables,
    )


def write_throat_side_compare_outputs(reference_dir: str | Path, outdir: str | Path) -> ThroatSideComparison:
    comparison = compare_throat_side_against_akabak(reference_dir)
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    compare_csv = out_path / "throat_side_compare.csv"
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
            strict=True,
        ):
            fh.write(
                ",".join(f"{float(value):.12g}" for value in row) + "\n"
            )

    observables_csv = out_path / "throat_side_observables.csv"
    observable_keys = list(comparison.observables.keys())
    with observables_csv.open("w", encoding="utf-8") as fh:
        fh.write("frequency_hz," + ",".join(observable_keys) + "\n")
        for i, freq in enumerate(comparison.frequency_hz):
            fields = [f"{float(freq):.12g}"]
            fields.extend(f"{float(comparison.observables[key][i]):.12g}" for key in observable_keys)
            fh.write(",".join(fields) + "\n")

    summary_path = out_path / "summary.json"
    summary = {
        "case": "TH throat-side smoke",
        "topology": THROAT_SIDE_TOPOLOGY,
        "metrics": comparison.metrics,
        "limitations": list(comparison.limitations),
        "generated_files": [compare_csv.name, observables_csv.name, summary_path.name],
        "no_frontend_contract_change": NO_FRONTEND_CONTRACT_CHANGE,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return comparison
