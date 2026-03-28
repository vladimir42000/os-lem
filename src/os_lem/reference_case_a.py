from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import math

import numpy as np

from .assemble import assemble_system
from .parser import normalize_model
from .solve import radiator_observation_pressure, solve_frequency_sweep

CASE_A_TOPOLOGY = (
    "two parallel front paths between the same acoustic nodes, followed by one shared "
    "conical exit segment and one mouth radiator"
)

CASE_A_LIMITATIONS = (
    "The Akabak Enclosure Vb/Lb block is mapped into os-lem as a simple rear volume because "
    "the current repo snapshot has no dedicated enclosure element.",
    "This reference bundle does not include an Akabak input-impedance phase export, so the "
    "smoke comparison is limited to impedance magnitude and mouth pressure amplitude/phase.",
)


@dataclass(slots=True, frozen=True)
class ReferenceSeries:
    frequency_hz: np.ndarray
    values: np.ndarray
    unit: str
    label: str


@dataclass(slots=True, frozen=True)
class CaseAReferenceBundle:
    impedance_magnitude_ohm: ReferenceSeries
    pressure_db: ReferenceSeries
    pressure_pa: ReferenceSeries
    pressure_phase_deg: ReferenceSeries
    script_text: str


@dataclass(slots=True, frozen=True)
class CaseAComparison:
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


def load_case_a_reference_bundle(reference_dir: str | Path) -> CaseAReferenceBundle:
    ref_dir = Path(reference_dir)
    impedance = _load_two_column_series(
        ref_dir / "A_IMP.ZMA",
        unit="ohm",
        label="Akabak input impedance magnitude",
    )
    pressure_db = _load_two_column_series(
        ref_dir / "A_LP.FRD",
        unit="dB",
        label="Akabak mouth pressure level",
    )
    pressure_pa = _load_two_column_series(
        ref_dir / "A_AMP.FRD",
        unit="Pa",
        label="Akabak mouth pressure amplitude",
    )
    pressure_phase = _load_two_column_series(
        ref_dir / "A_PHS.FRD",
        unit="deg",
        label="Akabak mouth pressure phase",
    )

    if not (
        np.array_equal(impedance.frequency_hz, pressure_db.frequency_hz)
        and np.array_equal(impedance.frequency_hz, pressure_pa.frequency_hz)
        and np.array_equal(impedance.frequency_hz, pressure_phase.frequency_hz)
    ):
        raise ValueError("Case A reference files do not share an identical frequency grid")

    script_text = (ref_dir / "CASE_A.AKS").read_text(encoding="latin1")
    return CaseAReferenceBundle(
        impedance_magnitude_ohm=impedance,
        pressure_db=pressure_db,
        pressure_pa=pressure_pa,
        pressure_phase_deg=pressure_phase,
        script_text=script_text,
    )


def build_case_a_model_dict(*, exit_segments: int = 1) -> dict[str, Any]:
    return {
        "meta": {"name": "case_a_parallel_bundle_shared_exit", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "em_explicit",
            "Re": "5.00 ohm",
            "Le": "1.40 mH",
            "Bl": 21.30,
            "Cms": 1.50e-04,
            "Rms": 4.10,
            "Mms": 0.094,
            "Sd": "531.00 cm2",
            "node_front": "front",
            "node_rear": "rear",
            "source_voltage_rms": 2.83,
        },
        "elements": [
            {"id": "rear_box", "type": "volume", "node": "rear", "value": "5.00 l"},
            {"id": "path1", "type": "duct", "node_a": "front", "node_b": "merge", "length": "30.00 cm", "area": "250.00 cm2"},
            {"id": "path2", "type": "duct", "node_a": "front", "node_b": "merge", "length": "45.00 cm", "area": "350.00 cm2"},
            {
                "id": "exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "mouth",
                "length": "10.00 cm",
                "area_start": "600.00 cm2",
                "area_end": "800.00 cm2",
                "profile": "conical",
                "segments": int(exit_segments),
            },
            {"id": "mouth", "type": "radiator", "node": "mouth", "model": "flanged_piston", "area": "800.00 cm2"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
        ],
    }


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    matrix = np.corrcoef(a, b)
    return float(matrix[0, 1])


def _wrapped_phase_delta_deg(a_deg: np.ndarray, b_deg: np.ndarray) -> np.ndarray:
    return (a_deg - b_deg + 180.0) % 360.0 - 180.0


def compare_case_a_against_akabak(reference_dir: str | Path, *, exit_segments: int = 1) -> CaseAComparison:
    bundle = load_case_a_reference_bundle(reference_dir)
    model_dict = build_case_a_model_dict(exit_segments=exit_segments)
    model, warnings = normalize_model(model_dict)
    if warnings:
        raise ValueError(f"Case A smoke model produced unexpected normalization warnings: {warnings}")
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, bundle.impedance_magnitude_ohm.frequency_hz)
    mouth_pressure = radiator_observation_pressure(sweep, system, "mouth", 1.0, radiation_space="2pi")

    oslem_zmag = np.abs(sweep.input_impedance)
    oslem_pressure_pa = np.abs(mouth_pressure)
    oslem_pressure_db = 20.0 * np.log10(np.maximum(oslem_pressure_pa, 1.0e-30) / 2.0e-5)
    oslem_pressure_phase_deg = (np.rad2deg(np.angle(mouth_pressure)) + 180.0) % 360.0 - 180.0

    freq = bundle.impedance_magnitude_ohm.frequency_hz
    low_band = (freq >= 20.0) & (freq <= 100.0)
    high_band = (freq >= 1000.0) & (freq <= 20000.0)

    phase_delta = _wrapped_phase_delta_deg(oslem_pressure_phase_deg, bundle.pressure_phase_deg.values)

    metrics: dict[str, float | bool | str] = {
        "exit_segments": int(exit_segments),
        "frequency_grid_shared": True,
        "frequency_point_count": int(freq.size),
        "zmag_overall_mae_ohm": float(np.mean(np.abs(oslem_zmag - bundle.impedance_magnitude_ohm.values))),
        "zmag_high_band_corr": _corrcoef(oslem_zmag[high_band], bundle.impedance_magnitude_ohm.values[high_band]),
        "pressure_db_overall_mae": float(np.mean(np.abs(oslem_pressure_db - bundle.pressure_db.values))),
        "pressure_db_low_band_corr": _corrcoef(oslem_pressure_db[low_band], bundle.pressure_db.values[low_band]),
        "pressure_pa_overall_mae": float(np.mean(np.abs(oslem_pressure_pa - bundle.pressure_pa.values))),
        "pressure_phase_overall_mae_deg": float(np.mean(np.abs(phase_delta))),
        "pressure_phase_low_band_corr": _corrcoef(
            oslem_pressure_phase_deg[low_band],
            bundle.pressure_phase_deg.values[low_band],
        ),
        "reference_impedance_phase_available": False,
        "case_topology": CASE_A_TOPOLOGY,
    }

    return CaseAComparison(
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
        limitations=CASE_A_LIMITATIONS,
        topology=CASE_A_TOPOLOGY,
    )


def write_case_a_compare_outputs(
    reference_dir: str | Path,
    outdir: str | Path,
    *,
    exit_segments: int = 1,
) -> CaseAComparison:
    comparison = compare_case_a_against_akabak(reference_dir, exit_segments=exit_segments)
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    csv_path = out_path / "case_a_compare.csv"
    header = (
        "frequency_hz,akabak_zmag_ohm,oslem_zmag_ohm,delta_zmag_ohm,"
        "akabak_lp_db,oslem_lp_db,delta_lp_db,"
        "akabak_pressure_pa,oslem_pressure_pa,delta_pressure_pa,"
        "akabak_phase_deg,oslem_phase_deg,delta_phase_deg_wrapped"
    )
    phase_delta = _wrapped_phase_delta_deg(
        comparison.oslem_pressure_phase_deg,
        comparison.akabak_pressure_phase_deg,
    )
    table = np.column_stack(
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
    np.savetxt(csv_path, table, delimiter=",", header=header, comments="")

    summary_path = out_path / "summary.json"
    summary = {
        "case": "Case A",
        "topology": comparison.topology,
        "limitations": list(comparison.limitations),
        "metrics": comparison.metrics,
        "generated_files": [csv_path.name, summary_path.name],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return comparison
