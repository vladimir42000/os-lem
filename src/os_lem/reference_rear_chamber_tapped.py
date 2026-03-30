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
from .solve import radiator_observation_pressure, solve_frequency_sweep

REAR_CHAMBER_TAPPED_TOPOLOGY = (
    "one rear chamber volume behind the driver, one true split junction, one direct main leg, "
    "one tapped side leg with an interior tap node, one true merge junction, one shared exit path, "
    "and one mouth radiator"
)

REAR_CHAMBER_TAPPED_LIMITATIONS = (
    "The Akabak TH case includes a dedicated throat chamber, a blind throat-side horn segment, and a rear chamber port "
    "injection point that are approximated here within the currently supported rear-chamber tapped skeleton path.",
    "This reference bundle does not include an Akabak input-impedance phase export, so the smoke comparison is limited "
    "to impedance magnitude plus mouth-pressure amplitude / level / phase.",
    "Key branch and junction observables in the generated observables CSV come from os-lem only because matching Akabak "
    "branch-observable exports are not present in this bundle.",
)

NO_FRONTEND_CONTRACT_CHANGE = True


@dataclass(slots=True, frozen=True)
class ReferenceSeries:
    frequency_hz: np.ndarray
    values: np.ndarray
    unit: str
    label: str


@dataclass(slots=True, frozen=True)
class RearChamberReferenceBundle:
    impedance_magnitude_ohm: ReferenceSeries
    pressure_db: ReferenceSeries
    pressure_pa: ReferenceSeries
    pressure_phase_deg: ReferenceSeries
    script_text: str


@dataclass(slots=True, frozen=True)
class RearChamberTappedComparison:
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


def _load_two_column_series(path: Path, *, unit: str, label: str) -> ReferenceSeries:
    xs: list[float] = []
    ys: list[float] = []
    with path.open("rb") as fh:
        for raw in fh:
            if raw.startswith(b"|") or not raw.strip():
                continue
            fields = raw.decode("latin1").split()
            if len(fields) < 2:
                continue
            xs.append(float(fields[0]))
            ys.append(float(fields[1]))
    return ReferenceSeries(
        frequency_hz=np.asarray(xs, dtype=float),
        values=np.asarray(ys, dtype=float),
        unit=unit,
        label=label,
    )


def load_rear_chamber_reference_bundle(reference_dir: str | Path) -> RearChamberReferenceBundle:
    ref_dir = Path(reference_dir)
    impedance = _load_two_column_series(
        ref_dir / "TH_Z.ZMA",
        unit="ohm",
        label="Akabak tapped-horn input impedance magnitude",
    )
    pressure_db = _load_two_column_series(
        ref_dir / "TH_LP1.FRD",
        unit="dB",
        label="Akabak tapped-horn mouth pressure level",
    )
    pressure_phase = _load_two_column_series(
        ref_dir / "TH_PH2.FRD",
        unit="deg",
        label="Akabak tapped-horn mouth pressure phase",
    )
    if not (
        np.array_equal(impedance.frequency_hz, pressure_db.frequency_hz)
        and np.array_equal(impedance.frequency_hz, pressure_phase.frequency_hz)
    ):
        raise ValueError("Rear-chamber tapped reference files do not share an identical frequency grid")

    pressure_pa = 2.0e-5 * np.power(10.0, pressure_db.values / 20.0)
    script_text = (ref_dir / "TH.aks").read_text(encoding="latin1")
    return RearChamberReferenceBundle(
        impedance_magnitude_ohm=impedance,
        pressure_db=pressure_db,
        pressure_pa=ReferenceSeries(
            frequency_hz=impedance.frequency_hz.copy(),
            values=pressure_pa,
            unit="Pa",
            label="Akabak tapped-horn mouth pressure amplitude derived from LP",
        ),
        pressure_phase_deg=pressure_phase,
        script_text=script_text,
    )


def build_rear_chamber_tapped_model_dict() -> dict[str, Any]:
    fs_hz = 42.0
    cms_m_per_n = 1.09e-4
    mms_kg = 1.0 / (((2.0 * math.pi * fs_hz) ** 2) * cms_m_per_n)

    return {
        "meta": {"name": "rear_chamber_tapped_th_smoke", "radiation_space": "2pi"},
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
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "split",
                "length": "20.00 cm",
                "area_start": "60.00 cm2",
                "area_end": "81.34 cm2",
                "profile": "conical",
                "segments": 4,
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
                "length": "18.83 cm",
                "area_start": "531.00 cm2",
                "area_end": "531.00 cm2",
                "profile": "conical",
                "segments": 2,
            },
            {
                "id": "tap_downstream",
                "type": "waveguide_1d",
                "node_a": "tap",
                "node_b": "merge",
                "length": "20.00 cm",
                "area_start": "60.00 cm2",
                "area_end": "81.34 cm2",
                "profile": "conical",
                "segments": 4,
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
            {"id": "p_tap", "type": "node_pressure", "target": "tap"},
            {"id": "p_merge", "type": "node_pressure", "target": "merge"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "main_leg", "location": "a"},
            {"id": "tap_up_q_a", "type": "element_volume_velocity", "target": "tap_upstream", "location": "a"},
            {"id": "tap_down_q_b", "type": "element_volume_velocity", "target": "tap_downstream", "location": "b"},
            {"id": "exit_q_a", "type": "element_volume_velocity", "target": "exit", "location": "a"},
            {"id": "exit_q_b", "type": "element_volume_velocity", "target": "exit", "location": "b"},
            {"id": "mouth_rad_q", "type": "element_volume_velocity", "target": "mouth_rad"},
            {
                "id": "spl_total",
                "type": "spl",
                "target": "mouth_rad",
                "distance": "1 m",
                "radiation_space": "2pi",
            },
        ],
    }


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    matrix = np.corrcoef(a, b)
    return float(matrix[0, 1])


def _wrapped_phase_delta_deg(a_deg: np.ndarray, b_deg: np.ndarray) -> np.ndarray:
    return (a_deg - b_deg + 180.0) % 360.0 - 180.0


def compare_rear_chamber_tapped_against_akabak(reference_dir: str | Path) -> RearChamberTappedComparison:
    bundle = load_rear_chamber_reference_bundle(reference_dir)
    model_dict = build_rear_chamber_tapped_model_dict()
    model, warnings = normalize_model(model_dict)
    if warnings:
        raise ValueError(f"Rear-chamber tapped smoke model produced unexpected normalization warnings: {warnings}")
    system = assemble_system(model)
    if len(system.rear_chamber_tapped_skeletons) != 1:
        raise ValueError("Rear-chamber tapped smoke model did not assemble exactly one rear-chamber tapped skeleton")

    api_result = run_simulation(model_dict, bundle.impedance_magnitude_ohm.frequency_hz)
    sweep = solve_frequency_sweep(model, system, bundle.impedance_magnitude_ohm.frequency_hz)
    mouth_pressure = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")

    oslem_zmag = api_result.zin_mag_ohm
    oslem_pressure_db = api_result.series["spl_total"]
    oslem_pressure_pa = np.abs(mouth_pressure)
    oslem_pressure_phase_deg = (np.rad2deg(np.angle(mouth_pressure)) + 180.0) % 360.0 - 180.0

    freq = bundle.impedance_magnitude_ohm.frequency_hz
    low_band = (freq >= 20.0) & (freq <= 100.0)
    high_band = (freq >= 1000.0) & (freq <= 20000.0)
    phase_delta = _wrapped_phase_delta_deg(oslem_pressure_phase_deg, bundle.pressure_phase_deg.values)

    observables = {
        "p_tap_pa": np.abs(api_result.series["p_tap"]),
        "p_merge_pa": np.abs(api_result.series["p_merge"]),
        "stem_q_b_mag_m3_s": np.abs(api_result.series["stem_q_b"]),
        "main_q_a_mag_m3_s": np.abs(api_result.series["main_q_a"]),
        "tap_up_q_a_mag_m3_s": np.abs(api_result.series["tap_up_q_a"]),
        "tap_down_q_b_mag_m3_s": np.abs(api_result.series["tap_down_q_b"]),
        "exit_q_a_mag_m3_s": np.abs(api_result.series["exit_q_a"]),
        "exit_q_b_mag_m3_s": np.abs(api_result.series["exit_q_b"]),
        "mouth_rad_q_mag_m3_s": np.abs(api_result.series["mouth_rad_q"]),
    }

    metrics: dict[str, float | bool | str] = {
        "frequency_grid_shared": True,
        "frequency_point_count": int(freq.size),
        "zmag_overall_mae_ohm": float(np.mean(np.abs(oslem_zmag - bundle.impedance_magnitude_ohm.values))),
        "zmag_high_band_corr": _corrcoef(oslem_zmag[high_band], bundle.impedance_magnitude_ohm.values[high_band]),
        "pressure_db_overall_mae": float(np.mean(np.abs(oslem_pressure_db - bundle.pressure_db.values))),
        "pressure_db_low_band_corr": _corrcoef(oslem_pressure_db[low_band], bundle.pressure_db.values[low_band]),
        "pressure_pa_overall_mae": float(np.mean(np.abs(oslem_pressure_pa - bundle.pressure_pa.values))),
        "pressure_phase_overall_mae_deg": float(np.mean(np.abs(phase_delta))),
        "reference_impedance_phase_available": False,
        "no_frontend_contract_change": True,
        "case_topology": REAR_CHAMBER_TAPPED_TOPOLOGY,
    }

    return RearChamberTappedComparison(
        frequency_hz=freq.copy(),
        akabak_impedance_magnitude_ohm=bundle.impedance_magnitude_ohm.values.copy(),
        oslem_impedance_magnitude_ohm=oslem_zmag,
        akabak_pressure_db=bundle.pressure_db.values.copy(),
        oslem_pressure_db=oslem_pressure_db,
        akabak_pressure_pa=bundle.pressure_pa.values.copy(),
        oslem_pressure_pa=oslem_pressure_pa,
        akabak_pressure_phase_deg=bundle.pressure_phase_deg.values.copy(),
        oslem_pressure_phase_deg=oslem_pressure_phase_deg,
        metrics=metrics,
        limitations=REAR_CHAMBER_TAPPED_LIMITATIONS,
        topology=REAR_CHAMBER_TAPPED_TOPOLOGY,
        observables=observables,
    )


def write_rear_chamber_tapped_compare_outputs(reference_dir: str | Path, outdir: str | Path) -> RearChamberTappedComparison:
    comparison = compare_rear_chamber_tapped_against_akabak(reference_dir)
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    csv_path = out_path / "rear_chamber_tapped_compare.csv"
    phase_delta = _wrapped_phase_delta_deg(
        comparison.oslem_pressure_phase_deg,
        comparison.akabak_pressure_phase_deg,
    )
    compare_table = np.column_stack(
        [
            comparison.frequency_hz,
            comparison.akabak_impedance_magnitude_ohm,
            comparison.oslem_impedance_magnitude_ohm,
            comparison.oslem_impedance_magnitude_ohm - comparison.akabak_impedance_magnitude_ohm,
            comparison.akabak_pressure_db,
            comparison.oslem_pressure_db,
            comparison.oslem_pressure_db - comparison.akabak_pressure_db,
            comparison.akabak_pressure_pa,
            comparison.oslem_pressure_pa,
            comparison.oslem_pressure_pa - comparison.akabak_pressure_pa,
            comparison.akabak_pressure_phase_deg,
            comparison.oslem_pressure_phase_deg,
            phase_delta,
        ]
    )
    np.savetxt(
        csv_path,
        compare_table,
        delimiter=",",
        header=(
            "frequency_hz,akabak_zmag_ohm,oslem_zmag_ohm,delta_zmag_ohm,"
            "akabak_lp_db,oslem_lp_db,delta_lp_db,"
            "akabak_pressure_pa,oslem_pressure_pa,delta_pressure_pa,"
            "akabak_phase_deg,oslem_phase_deg,delta_phase_deg_wrapped"
        ),
        comments="",
    )

    observables_path = out_path / "rear_chamber_tapped_observables.csv"
    observable_names = tuple(comparison.observables.keys())
    observable_table = np.column_stack([comparison.frequency_hz, *[comparison.observables[name] for name in observable_names]])
    np.savetxt(
        observables_path,
        observable_table,
        delimiter=",",
        header="frequency_hz," + ",".join(observable_names),
        comments="",
    )

    summary_path = out_path / "summary.json"
    summary = {
        "case": "TH rear-chamber tapped smoke",
        "topology": comparison.topology,
        "limitations": list(comparison.limitations),
        "metrics": comparison.metrics,
        "generated_files": [csv_path.name, observables_path.name, summary_path.name],
        "no_frontend_contract_change": True,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return comparison
