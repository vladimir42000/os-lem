from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import copy
import json

import numpy as np

from .assemble import assemble_system
from .elements.waveguide_1d import area_at_position
from .parser import normalize_model
from .reference_hyperbolic_flare_smoke import hyperbolic_model_dict
from .solve import radiator_observation_pressure, solve_frequency_sweep

HYPERBOLIC_FLARE_AKABAK_TOPOLOGY = (
    "one rear volume behind the driver, one hyperbolic-only rear-to-mouth flare path, "
    "one direct front radiator, and one mouth radiator"
)

HYPERBOLIC_FLARE_AKABAK_REFERENCE_KIND = "akabak_oriented_segmented_conical_surrogate"

HYPERBOLIC_FLARE_AKABAK_LIMITATIONS = (
    "This bundle is an Akabak-oriented smoke surface for the hyperbolic-only flare path: the reference files use "
    "Akabak-style .AKS/.ZMA/.FRD artifacts, but the bundled curve set is intentionally bounded and does not by itself "
    "establish broad external-solver parity.",
    "The bundled reference script approximates the same hyperbolic flare with a fixed 12-section conical chain because "
    "the current milestone stays inside the segmented 1D discipline and does not open any generalized horn-law machinery.",
    "This reference bundle does not include an input-impedance phase export, so the smoke comparison remains limited to "
    "impedance magnitude plus mouth-pressure level / amplitude / phase.",
)


@dataclass(slots=True, frozen=True)
class ReferenceSeries:
    frequency_hz: np.ndarray
    values: np.ndarray
    unit: str
    label: str


@dataclass(slots=True, frozen=True)
class HyperbolicFlareAkabakReferenceBundle:
    impedance_magnitude_ohm: ReferenceSeries
    pressure_db: ReferenceSeries
    pressure_pa: ReferenceSeries
    pressure_phase_deg: ReferenceSeries
    script_text: str


@dataclass(slots=True, frozen=True)
class HyperbolicFlareAkabakComparison:
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


FREQUENCY_GRID_HZ = np.geomspace(20.0, 20000.0, 120)
REFERENCE_SEGMENTS = 12


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


def load_hyperbolic_flare_akabak_reference_bundle(
    reference_dir: str | Path,
) -> HyperbolicFlareAkabakReferenceBundle:
    ref_dir = Path(reference_dir)
    impedance = _load_two_column_series(
        ref_dir / "HYP_Z.ZMA",
        unit="ohm",
        label="Akabak-oriented hyperbolic-flare input impedance magnitude",
    )
    pressure_db = _load_two_column_series(
        ref_dir / "HYP_LP.FRD",
        unit="dB",
        label="Akabak-oriented hyperbolic-flare mouth pressure level",
    )
    pressure_pa = _load_two_column_series(
        ref_dir / "HYP_AMP.FRD",
        unit="Pa",
        label="Akabak-oriented hyperbolic-flare mouth pressure amplitude",
    )
    pressure_phase = _load_two_column_series(
        ref_dir / "HYP_PHS.FRD",
        unit="deg",
        label="Akabak-oriented hyperbolic-flare mouth pressure phase",
    )

    if not (
        np.array_equal(impedance.frequency_hz, pressure_db.frequency_hz)
        and np.array_equal(impedance.frequency_hz, pressure_pa.frequency_hz)
        and np.array_equal(impedance.frequency_hz, pressure_phase.frequency_hz)
    ):
        raise ValueError("Hyperbolic flare reference files do not share an identical frequency grid")

    script_text = (ref_dir / "HYP.aks").read_text(encoding="latin1")
    return HyperbolicFlareAkabakReferenceBundle(
        impedance_magnitude_ohm=impedance,
        pressure_db=pressure_db,
        pressure_pa=pressure_pa,
        pressure_phase_deg=pressure_phase,
        script_text=script_text,
    )


def build_hyperbolic_flare_model_dict() -> dict[str, Any]:
    model_dict = copy.deepcopy(hyperbolic_model_dict())
    model_dict["meta"] = {
        "name": "hyperbolic_flare_akabak_oriented_smoke",
        "radiation_space": "2pi",
    }
    model_dict["driver"]["source_voltage_rms"] = 2.83
    model_dict["observations"] = [{"id": "zin", "type": "input_impedance", "target": "drv1"}]
    return model_dict


def build_hyperbolic_flare_segmented_conical_reference_model_dict() -> dict[str, Any]:
    model_dict = build_hyperbolic_flare_model_dict()
    waveguide = next(element for element in model_dict["elements"] if element["id"] == "wg1")
    length_cm = 40.0
    area_start_cm2 = 10.0
    area_end_cm2 = 50.0
    segments = REFERENCE_SEGMENTS
    xs = np.linspace(0.0, length_cm / 100.0, segments + 1)
    boundary_areas_m2 = [
        area_at_position(
            length_cm / 100.0,
            area_start_cm2 * 1.0e-4,
            area_end_cm2 * 1.0e-4,
            float(x),
            profile="hyperbolic",
        )
        for x in xs
    ]

    conical_segments: list[dict[str, Any]] = []
    for idx in range(segments):
        conical_segments.append(
            {
                "id": f"hyp_seg_{idx + 1:02d}",
                "type": "waveguide_1d",
                "node_a": "rear" if idx == 0 else f"hyp_node_{idx}",
                "node_b": "mouth" if idx == segments - 1 else f"hyp_node_{idx + 1}",
                "length": f"{length_cm / segments:.12f} cm",
                "area_start": f"{boundary_areas_m2[idx] * 1.0e4:.12f} cm2",
                "area_end": f"{boundary_areas_m2[idx + 1] * 1.0e4:.12f} cm2",
                "profile": "conical",
                "segments": 1,
            }
        )

    rebuilt_elements = []
    for element in model_dict["elements"]:
        if element["id"] == waveguide["id"]:
            rebuilt_elements.extend(conical_segments)
        else:
            rebuilt_elements.append(element)
    model_dict["elements"] = rebuilt_elements
    model_dict["meta"]["name"] = "hyperbolic_flare_akabak_segmented_conical_reference"
    return model_dict


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    matrix = np.corrcoef(a, b)
    return float(matrix[0, 1])


def _wrapped_phase_delta_deg(a_deg: np.ndarray, b_deg: np.ndarray) -> np.ndarray:
    return (a_deg - b_deg + 180.0) % 360.0 - 180.0


def compare_hyperbolic_flare_against_akabak_oriented_reference(
    reference_dir: str | Path,
) -> HyperbolicFlareAkabakComparison:
    bundle = load_hyperbolic_flare_akabak_reference_bundle(reference_dir)
    model, warnings = normalize_model(build_hyperbolic_flare_model_dict())
    if warnings:
        raise ValueError(f"Hyperbolic flare smoke model produced unexpected normalization warnings: {warnings}")
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, bundle.impedance_magnitude_ohm.frequency_hz)
    mouth_pressure = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space="2pi")

    oslem_zmag = np.abs(sweep.input_impedance)
    oslem_pressure_pa = np.abs(mouth_pressure)
    oslem_pressure_db = 20.0 * np.log10(np.maximum(oslem_pressure_pa, 1.0e-30) / 2.0e-5)
    oslem_pressure_phase_deg = (np.rad2deg(np.angle(mouth_pressure)) + 180.0) % 360.0 - 180.0

    freq = bundle.impedance_magnitude_ohm.frequency_hz
    low_band = (freq >= 20.0) & (freq <= 300.0)
    high_band = (freq >= 1000.0) & (freq <= 20000.0)
    phase_delta = _wrapped_phase_delta_deg(oslem_pressure_phase_deg, bundle.pressure_phase_deg.values)

    metrics: dict[str, float | bool | str] = {
        "frequency_grid_shared": True,
        "frequency_point_count": int(freq.size),
        "reference_kind": HYPERBOLIC_FLARE_AKABAK_REFERENCE_KIND,
        "reference_segments": int(REFERENCE_SEGMENTS),
        "reference_impedance_phase_available": False,
        "zmag_overall_mae_ohm": float(np.mean(np.abs(oslem_zmag - bundle.impedance_magnitude_ohm.values))),
        "zmag_high_band_corr": _corrcoef(oslem_zmag[high_band], bundle.impedance_magnitude_ohm.values[high_band]),
        "zmag_max_abs_delta_ohm": float(np.max(np.abs(oslem_zmag - bundle.impedance_magnitude_ohm.values))),
        "pressure_db_overall_mae": float(np.mean(np.abs(oslem_pressure_db - bundle.pressure_db.values))),
        "pressure_db_low_band_corr": _corrcoef(oslem_pressure_db[low_band], bundle.pressure_db.values[low_band]),
        "pressure_db_max_abs_delta": float(np.max(np.abs(oslem_pressure_db - bundle.pressure_db.values))),
        "pressure_pa_overall_mae": float(np.mean(np.abs(oslem_pressure_pa - bundle.pressure_pa.values))),
        "pressure_phase_overall_mae_deg": float(np.mean(np.abs(phase_delta))),
        "pressure_phase_max_abs_delta_deg": float(np.max(np.abs(phase_delta))),
        "case_topology": HYPERBOLIC_FLARE_AKABAK_TOPOLOGY,
    }

    return HyperbolicFlareAkabakComparison(
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
        limitations=HYPERBOLIC_FLARE_AKABAK_LIMITATIONS,
        topology=HYPERBOLIC_FLARE_AKABAK_TOPOLOGY,
    )


def write_hyperbolic_flare_akabak_compare_outputs(
    reference_dir: str | Path,
    outdir: str | Path,
) -> HyperbolicFlareAkabakComparison:
    comparison = compare_hyperbolic_flare_against_akabak_oriented_reference(reference_dir)
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    csv_path = out_path / "hyperbolic_flare_akabak_compare.csv"
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
        "case": "Hyperbolic flare Akabak-oriented smoke",
        "topology": comparison.topology,
        "limitations": list(comparison.limitations),
        "metrics": comparison.metrics,
        "generated_files": [csv_path.name, summary_path.name],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return comparison
