from __future__ import annotations

import csv
import math
import os
import re
import sys
from pathlib import Path

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from os_lem.api import run_simulation  # noqa: E402

BENCH_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BENCH_DIR / "source_inputs"
COMPARE_DIR = BENCH_DIR / "comparison_outputs"
MODEL_PATH = BENCH_DIR / "model.yaml"


def _parse_number_and_unit(value: str) -> tuple[float, str | None]:
    m = re.match(r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z0-9]+)?\s*$", value)
    if not m:
        raise RuntimeError(f"Cannot parse scalar {value!r}")
    return float(m.group(1)), m.group(2)


def _load_model() -> dict:
    with MODEL_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _parse_hornresp_case(case_path: Path) -> dict[str, float]:
    text = case_path.read_text(encoding="utf-8")
    out: dict[str, float] = {}
    con_values: list[float] = []
    exact_scalar_keys = {
        "Eg", "Rg", "S1", "S2", "S3", "Sd", "Bl", "Cms", "Rms", "Mmd", "Le", "Re", "Vtc", "Atc", "Tal1", "Tal2"
    }
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Ang") and "x Pi" in stripped:
            out["Ang"] = float(stripped.split("=", 1)[1].split("x", 1)[0].strip())
            continue
        m = re.match(r"^([A-Za-z0-9]+)\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$", stripped)
        if not m:
            continue
        key = m.group(1)
        value = float(m.group(2))
        if key == "Con":
            con_values.append(value)
        elif key in exact_scalar_keys and key not in out:
            out[key] = value
    if len(con_values) >= 2:
        out["Con1"] = con_values[0]
        out["Con2"] = con_values[1]
    missing = sorted({"Ang", "Eg", "Rg", "S1", "S2", "S3", "Con1", "Con2", "Sd", "Bl", "Cms", "Rms", "Mmd", "Le", "Re", "Vtc", "Atc", "Tal1", "Tal2"} - out.keys())
    if missing:
        raise RuntimeError(f"Missing Hornresp case values: {missing}")
    return out


def _parse_tsp(path: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = [item.strip() for item in line.split("=", 1)]
        number = re.search(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", value)
        if number:
            out[key] = float(number.group(0))
    return out


def _parse_hornresp_table(table_path: Path) -> dict[str, np.ndarray]:
    rows: list[list[float]] = []
    with table_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("Freq"):
                continue
            parts = stripped.split()
            try:
                rows.append(list(map(float, parts[:16])))
            except ValueError:
                continue
    if not rows:
        raise RuntimeError("No numeric rows found in Hornresp table")
    arr = np.asarray(rows, dtype=float)
    return {
        "frequency_hz": arr[:, 0],
        "spl_db": arr[:, 4],
        "ze_ohm": arr[:, 5],
        "xd_mm": arr[:, 6],
        "ze_phase_deg": arr[:, 15],
    }


def _parse_frd_or_table(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    rows = []
    with path.open("r", encoding="latin1", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("|") or stripped.startswith("Freq"):
                continue
            parts = stripped.split()
            try:
                nums = [float(p) for p in parts[:3]]
            except ValueError:
                continue
            rows.append(nums)
    if not rows:
        raise RuntimeError(f"No numeric rows found in {path.name}")
    arr = np.asarray(rows, dtype=float)
    if arr.shape[1] >= 3:
        return arr[:, 0], arr[:, 1], arr[:, 2]
    return arr[:, 0], arr[:, 1], None


def _parse_two_column_reference(path: Path) -> tuple[np.ndarray, np.ndarray]:
    x, y, _ = _parse_frd_or_table(path)
    return x, y


def _validate_mapping(model: dict) -> tuple[dict[str, float], dict[str, float]]:
    case = _parse_hornresp_case(SOURCE_DIR / "poc3.txt")
    tsp = _parse_tsp(SOURCE_DIR / "VisatonFRS8M.tsp")
    drv = model["driver"]
    re_value, re_unit = _parse_number_and_unit(drv["Re"])
    le_value, le_unit = _parse_number_and_unit(drv["Le"])
    sd_value, sd_unit = _parse_number_and_unit(drv["Sd"])
    mms_value = float(drv["Mms"])
    assert re_unit == "ohm" and math.isclose(re_value, case["Re"], rel_tol=0.0, abs_tol=1e-12)
    assert le_unit == "mH" and math.isclose(le_value, case["Le"], rel_tol=0.0, abs_tol=1e-12)
    assert sd_unit == "cm2" and math.isclose(sd_value, case["Sd"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["Bl"]), case["Bl"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["Cms"]), case["Cms"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["Rms"]), case["Rms"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["source_voltage_rms"]), case["Eg"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(mms_value, tsp["Mms"] * 1.0e-3, rel_tol=0.0, abs_tol=1e-12)
    elements = {element["id"]: element for element in model["elements"]}
    throat = elements["throat_chamber"]
    seg1 = elements["horn_seg1"]
    seg2 = elements["horn_seg2"]
    front_rad = elements["front_rad"]
    mouth_rad = elements["mouth_rad"]
    for key, expected in ((throat["area_start"], case["Atc"]), (throat["area_end"], case["Atc"]), (seg1["area_start"], case["S1"]), (seg1["area_end"], case["S2"]), (seg2["area_start"], case["S2"]), (seg2["area_end"], case["S3"])):
        value, unit = _parse_number_and_unit(key)
        assert unit == "cm2" and math.isclose(value, expected, rel_tol=0.0, abs_tol=1e-12)
    for key, expected in ((throat["length"], case["Vtc"] / case["Atc"]), (seg1["length"], case["Con1"]), (seg2["length"], case["Con2"])):
        value, unit = _parse_number_and_unit(key)
        assert unit == "cm" and math.isclose(value, expected, rel_tol=0.0, abs_tol=1e-12)
    for key, expected in ((front_rad["area"], case["Sd"]), (mouth_rad["area"], case["S3"])):
        value, unit = _parse_number_and_unit(key)
        assert unit == "cm2" and math.isclose(value, expected, rel_tol=0.0, abs_tol=1e-12)
    if not (math.isclose(case["Tal1"], 0.0) and math.isclose(case["Tal2"], 0.0)):
        raise RuntimeError("POC3 frozen source truth requires Tal1=0 and Tal2=0")
    return case, tsp


def _write_two_column(path: Path, x: np.ndarray, y: np.ndarray, header: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="	")
        writer.writerow(header.split("	"))
        for xv, yv in zip(x, y, strict=True):
            writer.writerow([f"{xv:.6f}", f"{yv:.12e}"])


def _write_three_or_four_columns(path: Path, x: np.ndarray, a: np.ndarray, b: np.ndarray, headers: tuple[str, str, str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="	")
        writer.writerow(list(headers))
        for xv, av, bv in zip(x, a, b, strict=True):
            writer.writerow([f"{xv:.6f}", f"{av:.12e}", f"{bv:.12e}", f"{(bv-av):.12e}"])


def _write_excursion(path: Path, freq: np.ndarray, excursion_mm: np.ndarray, displacement_m: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="	")
        writer.writerow(["frequency_hz", "excursion_mm", "displacement_abs_m"])
        for f_hz, x_mm, x_m in zip(freq, excursion_mm, displacement_m, strict=True):
            writer.writerow([f"{f_hz:.6f}", f"{x_mm:.12e}", f"{x_m:.12e}"])


def _interp(x_ref: np.ndarray, x_src: np.ndarray, y_src: np.ndarray) -> np.ndarray:
    return np.interp(x_ref, x_src, y_src)


def _classify(summary: dict[str, float], finite_ok: bool) -> tuple[str, str]:
    if not finite_ok:
        return (
            "solver/pathology",
            "non-finite benchmark traces were produced, so the dominant issue is treated as a solver/pathology stop signal",
        )
    imp = summary["hornresp_impedance_mag_mae_ohm"]
    exc = summary["hornresp_excursion_mae_mm"]
    spl = summary["hornresp_total_spl_mae_db"]
    front = summary["hornresp_front_spl_mae_db"]
    mouth = summary["hornresp_mouth_spl_mae_db"]
    if imp <= 1.5 and exc <= 0.35 and max(spl, front, mouth) >= 3.0:
        return (
            "model-equivalence",
            "electro-mechanical traces remain materially closer than the acoustic superposition traces, so the dominant mismatch is classified as model-equivalence rather than stuffing or numerical failure",
        )
    return (
        "missing-physics",
        "after conical no-fill alignment, the remaining mismatch is broader than a pure topology/radiation semantic gap, so the dominant residual is classified as missing-physics rather than stuffing omission",
    )


def _write_comparison_outputs(freq_oslem: np.ndarray, spl_total_db: np.ndarray, spl_front_db: np.ndarray, spl_mouth_db: np.ndarray, zin_complex: np.ndarray, excursion_mm: np.ndarray) -> dict[str, float | str]:
    COMPARE_DIR.mkdir(parents=True, exist_ok=True)

    hr_all = _parse_hornresp_table(SOURCE_DIR / "poc3_hr_all.txt")
    hr_drv_f, hr_drv_db, _ = _parse_frd_or_table(SOURCE_DIR / "poc3_hr_drv.txt")
    hr_mth_f, hr_mth_db, _ = _parse_frd_or_table(SOURCE_DIR / "poc3_hr_mth.txt")
    ak_spl_f, ak_spl_db, _ = _parse_frd_or_table(SOURCE_DIR / "POC3SP.FRD")
    _, ak_phase_deg, _ = _parse_frd_or_table(SOURCE_DIR / "POC3PHS.FRD")
    ak_imp_f, ak_imp_ohm = _parse_two_column_reference(SOURCE_DIR / "POC3IMP.ZMA")
    ak_xc_f, ak_xc_m, _ = _parse_frd_or_table(SOURCE_DIR / "POC3XCR.TXT")

    _write_three_or_four_columns(COMPARE_DIR / "hornresp_vs_oslem_total_spl_db.txt", hr_all["frequency_hz"], hr_all["spl_db"], _interp(hr_all["frequency_hz"], freq_oslem, spl_total_db), ("frequency_hz", "hornresp_total_spl_db", "oslem_total_spl_db", "delta_db"))
    _write_three_or_four_columns(COMPARE_DIR / "hornresp_vs_oslem_front_spl_db.txt", hr_drv_f, hr_drv_db, _interp(hr_drv_f, freq_oslem, spl_front_db), ("frequency_hz", "hornresp_front_spl_db", "oslem_front_spl_db", "delta_db"))
    _write_three_or_four_columns(COMPARE_DIR / "hornresp_vs_oslem_mouth_spl_db.txt", hr_mth_f, hr_mth_db, _interp(hr_mth_f, freq_oslem, spl_mouth_db), ("frequency_hz", "hornresp_mouth_spl_db", "oslem_mouth_spl_db", "delta_db"))
    _write_three_or_four_columns(COMPARE_DIR / "hornresp_vs_oslem_impedance_magnitude_ohm.txt", hr_all["frequency_hz"], hr_all["ze_ohm"], _interp(hr_all["frequency_hz"], freq_oslem, np.abs(zin_complex)), ("frequency_hz", "hornresp_impedance_ohm", "oslem_impedance_ohm", "delta_ohm"))
    _write_three_or_four_columns(COMPARE_DIR / "hornresp_vs_oslem_impedance_phase_deg.txt", hr_all["frequency_hz"], hr_all["ze_phase_deg"], _interp(hr_all["frequency_hz"], freq_oslem, np.angle(zin_complex, deg=True)), ("frequency_hz", "hornresp_impedance_phase_deg", "oslem_impedance_phase_deg", "delta_deg"))
    _write_three_or_four_columns(COMPARE_DIR / "hornresp_vs_oslem_cone_excursion_mm.txt", hr_all["frequency_hz"], hr_all["xd_mm"], _interp(hr_all["frequency_hz"], freq_oslem, excursion_mm), ("frequency_hz", "hornresp_excursion_mm", "oslem_excursion_mm", "delta_mm"))
    _write_three_or_four_columns(COMPARE_DIR / "akabak_vs_oslem_total_spl_db.txt", ak_spl_f, ak_spl_db, _interp(ak_spl_f, freq_oslem, spl_total_db), ("frequency_hz", "akabak_total_spl_db", "oslem_total_spl_db", "delta_db"))
    _write_three_or_four_columns(COMPARE_DIR / "akabak_vs_oslem_impedance_magnitude_ohm.txt", ak_imp_f, ak_imp_ohm, _interp(ak_imp_f, freq_oslem, np.abs(zin_complex)), ("frequency_hz", "akabak_impedance_ohm", "oslem_impedance_ohm", "delta_ohm"))
    _write_three_or_four_columns(COMPARE_DIR / "akabak_vs_oslem_cone_excursion_mm.txt", ak_xc_f, ak_xc_m * 1.0e3, _interp(ak_xc_f, freq_oslem, excursion_mm), ("frequency_hz", "akabak_excursion_mm", "oslem_excursion_mm", "delta_mm"))

    finite_ok = bool(np.all(np.isfinite(spl_total_db)) and np.all(np.isfinite(spl_front_db)) and np.all(np.isfinite(spl_mouth_db)) and np.all(np.isfinite(np.abs(zin_complex))) and np.all(np.isfinite(excursion_mm)))
    summary: dict[str, float | str] = {
        "hornresp_total_spl_mae_db": float(np.mean(np.abs(_interp(hr_all["frequency_hz"], freq_oslem, spl_total_db) - hr_all["spl_db"]))),
        "hornresp_front_spl_mae_db": float(np.mean(np.abs(_interp(hr_drv_f, freq_oslem, spl_front_db) - hr_drv_db))),
        "hornresp_mouth_spl_mae_db": float(np.mean(np.abs(_interp(hr_mth_f, freq_oslem, spl_mouth_db) - hr_mth_db))),
        "hornresp_impedance_mag_mae_ohm": float(np.mean(np.abs(_interp(hr_all["frequency_hz"], freq_oslem, np.abs(zin_complex)) - hr_all["ze_ohm"]))),
        "hornresp_impedance_phase_mae_deg": float(np.mean(np.abs(_interp(hr_all["frequency_hz"], freq_oslem, np.angle(zin_complex, deg=True)) - hr_all["ze_phase_deg"]))),
        "hornresp_excursion_mae_mm": float(np.mean(np.abs(_interp(hr_all["frequency_hz"], freq_oslem, excursion_mm) - hr_all["xd_mm"]))),
        "akabak_total_spl_mae_db": float(np.mean(np.abs(_interp(ak_spl_f, freq_oslem, spl_total_db) - ak_spl_db))),
        "akabak_total_phase_reference_available": "true",
        "akabak_impedance_mag_mae_ohm": float(np.mean(np.abs(_interp(ak_imp_f, freq_oslem, np.abs(zin_complex)) - ak_imp_ohm))),
        "akabak_excursion_mae_mm": float(np.mean(np.abs(_interp(ak_xc_f, freq_oslem, excursion_mm) - ak_xc_m * 1.0e3))),
    }
    klass, reason = _classify({k: float(v) for k, v in summary.items() if isinstance(v, float)}, finite_ok)
    summary["dominant_mismatch_classification"] = klass
    summary["classification_reason"] = reason
    summary["dominant_phase_reference_note"] = "akabak_total_phase_available_but_current_oslem_high_level_surface_does_not_export_truthful_total_spl_phase"
    summary["akabak_phase_span_deg"] = float(np.nanmax(ak_phase_deg) - np.nanmin(ak_phase_deg))

    lines = ["poc3_blh_benchmark_pass1_comparison_summary"]
    for key, value in summary.items():
        if isinstance(value, float):
            lines.append(f"{key}={value:.6f}")
        else:
            lines.append(f"{key}={value}")
    (COMPARE_DIR / "comparison_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    model = _load_model()
    case, tsp = _validate_mapping(model)
    hr_all = _parse_hornresp_table(SOURCE_DIR / "poc3_hr_all.txt")
    frequencies_hz = hr_all["frequency_hz"]
    result = run_simulation(model, frequencies_hz)

    zin = result.zin_complex_ohm
    if zin is None:
        raise RuntimeError("Input impedance observation missing")
    displacement_m = result.cone_displacement_m
    if displacement_m is None:
        raise RuntimeError("Cone displacement observation missing")
    excursion_mm = result.cone_excursion_mm
    if excursion_mm is None:
        raise RuntimeError("Cone excursion observation missing")

    spl_total_db = np.asarray(result.series["spl_total"], dtype=float)
    spl_front_db = np.asarray(result.series["spl_front"], dtype=float)
    spl_mouth_db = np.asarray(result.series["spl_mouth"], dtype=float)

    _write_two_column(BENCH_DIR / "oslem_spl_magnitude_db.txt", frequencies_hz, spl_total_db, "frequency_hz	oslem_total_spl_db")
    _write_two_column(BENCH_DIR / "oslem_impedance_magnitude_ohm.txt", frequencies_hz, np.abs(zin), "frequency_hz	oslem_impedance_magnitude_ohm")
    _write_two_column(BENCH_DIR / "oslem_impedance_phase_deg.txt", frequencies_hz, np.angle(zin, deg=True), "frequency_hz	oslem_impedance_phase_deg")
    _write_excursion(BENCH_DIR / "oslem_cone_excursion_displacement.txt", frequencies_hz, excursion_mm, np.abs(displacement_m))
    _write_two_column(BENCH_DIR / "oslem_spl_front_db.txt", frequencies_hz, spl_front_db, "frequency_hz	oslem_front_spl_db")
    _write_two_column(BENCH_DIR / "oslem_spl_mouth_db.txt", frequencies_hz, spl_mouth_db, "frequency_hz	oslem_mouth_spl_db")

    summary = _write_comparison_outputs(frequencies_hz, spl_total_db, spl_front_db, spl_mouth_db, zin, excursion_mm)
    lines = [
        "poc3_blh_benchmark_pass1",
        f"frequency_points={frequencies_hz.size}",
        f"spl_min_db={spl_total_db.min():.6f}",
        f"spl_max_db={spl_total_db.max():.6f}",
        f"zin_min_ohm={np.abs(zin).min():.6f}",
        f"zin_max_ohm={np.abs(zin).max():.6f}",
        f"excursion_max_mm={excursion_mm.max():.6f}",
        f"radiation_space={model['meta']['radiation_space']}",
        f"hornresp_ang_pi={case['Ang']:.6f}",
        f"hornresp_tal1={case['Tal1']:.6f}",
        f"hornresp_tal2={case['Tal2']:.6f}",
        "le_modeled=true",
        f"driver_mass_mapping=tsp_mms_used_{tsp['Mms']*1.0e-3:.8f}_kg_with_hornresp_mmd_recorded_{case['Mmd']*1.0e-3:.8f}_kg",
        "spl_phase_exported=false",
    ]
    for key, value in summary.items():
        if isinstance(value, float):
            lines.append(f"{key}={value:.6f}")
        else:
            lines.append(f"{key}={value}")
    (BENCH_DIR / "run_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
