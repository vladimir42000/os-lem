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
    wanted = {
        "Ang": r"^Ang\s*=\s*([0-9.+\-Ee]+)\s*x\s*Pi",
        "Eg": r"^Eg\s*=\s*([0-9.+\-Ee]+)",
        "Rg": r"^Rg\s*=\s*([0-9.+\-Ee]+)",
        "S1": r"^S1\s*=\s*([0-9.+\-Ee]+)",
        "S2": r"^S2\s*=\s*([0-9.+\-Ee]+)",
        "Con1": r"^Con\s*=\s*([0-9.+\-Ee]+)",
        "S3": r"^S3\s*=\s*([0-9.+\-Ee]+)",
        "Con2": r"^Con\s*=\s*([0-9.+\-Ee]+)",
        "Sd": r"^Sd\s*=\s*([0-9.+\-Ee]+)",
        "Bl": r"^Bl\s*=\s*([0-9.+\-Ee]+)",
        "Cms": r"^Cms\s*=\s*([0-9.+\-Ee]+)",
        "Rms": r"^Rms\s*=\s*([0-9.+\-Ee]+)",
        "Mmd": r"^Mmd\s*=\s*([0-9.+\-Ee]+)",
        "Le": r"^Le\s*=\s*([0-9.+\-Ee]+)",
        "Re": r"^Re\s*=\s*([0-9.+\-Ee]+)",
        "Tal1": r"^Tal1\s*=\s*([0-9.+\-Ee]+)",
        "Tal2": r"^Tal2\s*=\s*([0-9.+\-Ee]+)",
    }
    lines = text.splitlines()
    out: dict[str, float] = {}
    con_values: list[float] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Con") and "=" in stripped:
            con_values.append(float(stripped.split("=", 1)[1].strip()))
        for key in ("Ang", "Eg", "Rg", "S1", "S2", "S3", "Sd", "Bl", "Cms", "Rms", "Mmd", "Le", "Re", "Tal1", "Tal2"):
            if key in out:
                continue
            m = re.match(wanted[key], stripped)
            if m:
                out[key] = float(m.group(1))
    if len(con_values) >= 2:
        out["Con1"] = con_values[0]
        out["Con2"] = con_values[1]
    missing = sorted({"Ang", "Eg", "Rg", "S1", "S2", "S3", "Con1", "Con2", "Sd", "Bl", "Cms", "Rms", "Mmd", "Le", "Re", "Tal1", "Tal2"} - out.keys())
    if missing:
        raise RuntimeError(f"Missing Hornresp case values: {missing}")
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


def _parse_two_column_reference(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rows: list[tuple[float, float]] = []
    with path.open("r", encoding="latin1", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("|"):
                continue
            parts = stripped.split()
            if len(parts) < 2:
                continue
            try:
                rows.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    if not rows:
        raise RuntimeError(f"No numeric rows found in {path.name}")
    arr = np.asarray(rows, dtype=float)
    return arr[:, 0], arr[:, 1]


def _validate_mapping(model: dict) -> dict[str, float]:
    case = _parse_hornresp_case(SOURCE_DIR / "poc2_hornresp.txt")
    drv = model["driver"]
    re_value, re_unit = _parse_number_and_unit(drv["Re"])
    le_value, le_unit = _parse_number_and_unit(drv["Le"])
    sd_value, sd_unit = _parse_number_and_unit(drv["Sd"])
    assert re_unit == "ohm" and math.isclose(re_value, case["Re"], rel_tol=0.0, abs_tol=1e-12)
    assert le_unit == "mH" and math.isclose(le_value, case["Le"], rel_tol=0.0, abs_tol=1e-12)
    assert sd_unit == "cm2" and math.isclose(sd_value, case["Sd"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["Bl"]), case["Bl"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["Cms"]), case["Cms"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["Rms"]), case["Rms"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["Mms"]), case["Mmd"] * 1.0e-3, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(float(drv["source_voltage_rms"]), case["Eg"], rel_tol=0.0, abs_tol=1e-12)
    elements = {element["id"]: element for element in model["elements"]}
    rear_stub = elements["rear_stub"]
    rear_main = elements["rear_main"]
    front_rad = elements["front_rad"]
    mouth_rad = elements["mouth_rad"]
    for key, expected in ((rear_stub["area_start"], case["S2"]), (rear_stub["area_end"], case["S1"]), (rear_main["area_start"], case["S2"]), (rear_main["area_end"], case["S3"])):
        value, unit = _parse_number_and_unit(key)
        assert unit == "cm2" and math.isclose(value, expected, rel_tol=0.0, abs_tol=1e-12)
    for key, expected in ((rear_stub["length"], case["Con1"]), (rear_main["length"], case["Con2"])):
        value, unit = _parse_number_and_unit(key)
        assert unit == "cm" and math.isclose(value, expected, rel_tol=0.0, abs_tol=1e-12)
    for key, expected in ((front_rad["area"], case["Sd"]), (mouth_rad["area"], case["S3"])):
        value, unit = _parse_number_and_unit(key)
        assert unit == "cm2" and math.isclose(value, expected, rel_tol=0.0, abs_tol=1e-12)
    return case


def _write_two_column(path: Path, x: np.ndarray, y: np.ndarray, header: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(header.split("\t"))
        for xv, yv in zip(x, y, strict=True):
            writer.writerow([f"{xv:.6f}", f"{yv:.12e}"])


def _write_three_column(path: Path, x: np.ndarray, y1: np.ndarray, y2: np.ndarray, header: tuple[str, str, str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(list(header))
        for xv, a, b in zip(x, y1, y2, strict=True):
            writer.writerow([f"{xv:.6f}", f"{a:.12e}", f"{b:.12e}", f"{(b-a):.12e}"])


def _write_excursion(path: Path, freq: np.ndarray, excursion_mm: np.ndarray, displacement_m: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["frequency_hz", "excursion_mm", "displacement_abs_m"])
        for f_hz, x_mm, x_m in zip(freq, excursion_mm, displacement_m, strict=True):
            writer.writerow([f"{f_hz:.6f}", f"{x_mm:.12e}", f"{x_m:.12e}"])


def _write_comparison_outputs(freq_oslem: np.ndarray, spl_total_db: np.ndarray, zin_complex: np.ndarray, excursion_mm: np.ndarray) -> dict[str, float]:
    COMPARE_DIR.mkdir(parents=True, exist_ok=True)

    hr = _parse_hornresp_table(SOURCE_DIR / "poc2.txt")
    _write_three_column(
        COMPARE_DIR / "hornresp_vs_oslem_spl_magnitude_db.txt",
        hr["frequency_hz"],
        hr["spl_db"],
        np.interp(hr["frequency_hz"], freq_oslem, spl_total_db),
        ("frequency_hz", "hornresp_spl_db", "oslem_spl_db", "delta_db"),
    )
    _write_three_column(
        COMPARE_DIR / "hornresp_vs_oslem_impedance_magnitude_ohm.txt",
        hr["frequency_hz"],
        hr["ze_ohm"],
        np.interp(hr["frequency_hz"], freq_oslem, np.abs(zin_complex)),
        ("frequency_hz", "hornresp_impedance_ohm", "oslem_impedance_ohm", "delta_ohm"),
    )
    _write_three_column(
        COMPARE_DIR / "hornresp_vs_oslem_impedance_phase_deg.txt",
        hr["frequency_hz"],
        hr["ze_phase_deg"],
        np.interp(hr["frequency_hz"], freq_oslem, np.angle(zin_complex, deg=True)),
        ("frequency_hz", "hornresp_impedance_phase_deg", "oslem_impedance_phase_deg", "delta_deg"),
    )
    _write_three_column(
        COMPARE_DIR / "hornresp_vs_oslem_cone_excursion_mm.txt",
        hr["frequency_hz"],
        hr["xd_mm"],
        np.interp(hr["frequency_hz"], freq_oslem, excursion_mm),
        ("frequency_hz", "hornresp_excursion_mm", "oslem_excursion_mm", "delta_mm"),
    )

    ak_spl_f, ak_spl_db = _parse_two_column_reference(SOURCE_DIR / "POC2.FRD")
    ak_imp_f, ak_imp_ohm = _parse_two_column_reference(SOURCE_DIR / "POC2IMP.TXT")
    ak_xc_f, ak_xc_m = _parse_two_column_reference(SOURCE_DIR / "POC2XC.TXT")

    _write_three_column(
        COMPARE_DIR / "akabak_vs_oslem_spl_magnitude_db.txt",
        ak_spl_f,
        ak_spl_db,
        np.interp(ak_spl_f, freq_oslem, spl_total_db),
        ("frequency_hz", "akabak_spl_db", "oslem_spl_db", "delta_db"),
    )
    _write_three_column(
        COMPARE_DIR / "akabak_vs_oslem_impedance_magnitude_ohm.txt",
        ak_imp_f,
        ak_imp_ohm,
        np.interp(ak_imp_f, freq_oslem, np.abs(zin_complex)),
        ("frequency_hz", "akabak_impedance_ohm", "oslem_impedance_ohm", "delta_ohm"),
    )
    _write_three_column(
        COMPARE_DIR / "akabak_vs_oslem_cone_excursion_mm.txt",
        ak_xc_f,
        ak_xc_m * 1.0e3,
        np.interp(ak_xc_f, freq_oslem, excursion_mm),
        ("frequency_hz", "akabak_excursion_mm", "oslem_excursion_mm", "delta_mm"),
    )

    summary = {
        "hornresp_spl_mae_db": float(np.mean(np.abs(np.interp(hr["frequency_hz"], freq_oslem, spl_total_db) - hr["spl_db"]))),
        "hornresp_impedance_mae_ohm": float(np.mean(np.abs(np.interp(hr["frequency_hz"], freq_oslem, np.abs(zin_complex)) - hr["ze_ohm"]))),
        "hornresp_phase_mae_deg": float(np.mean(np.abs(np.interp(hr["frequency_hz"], freq_oslem, np.angle(zin_complex, deg=True)) - hr["ze_phase_deg"]))),
        "hornresp_excursion_mae_mm": float(np.mean(np.abs(np.interp(hr["frequency_hz"], freq_oslem, excursion_mm) - hr["xd_mm"]))),
        "akabak_spl_mae_db": float(np.mean(np.abs(np.interp(ak_spl_f, freq_oslem, spl_total_db) - ak_spl_db))),
        "akabak_impedance_mae_ohm": float(np.mean(np.abs(np.interp(ak_imp_f, freq_oslem, np.abs(zin_complex)) - ak_imp_ohm))),
        "akabak_excursion_mae_mm": float(np.mean(np.abs(np.interp(ak_xc_f, freq_oslem, excursion_mm) - ak_xc_m * 1.0e3))),
    }
    (COMPARE_DIR / "comparison_summary.txt").write_text(
        "\n".join([
            "poc2_conical_no_fill_benchmark_comparison_summary",
            *(f"{k}={v:.6f}" for k, v in summary.items()),
        ]) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    model = _load_model()
    case = _validate_mapping(model)
    hr = _parse_hornresp_table(SOURCE_DIR / "poc2.txt")
    frequencies_hz = hr["frequency_hz"]
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

    _write_two_column(BENCH_DIR / "oslem_spl_magnitude_db.txt", frequencies_hz, spl_total_db, "frequency_hz\toslem_spl_total_db")
    _write_two_column(BENCH_DIR / "oslem_impedance_magnitude_ohm.txt", frequencies_hz, np.abs(zin), "frequency_hz\toslem_impedance_magnitude_ohm")
    _write_two_column(BENCH_DIR / "oslem_impedance_phase_deg.txt", frequencies_hz, np.angle(zin, deg=True), "frequency_hz\toslem_impedance_phase_deg")
    _write_excursion(BENCH_DIR / "oslem_cone_excursion_displacement.txt", frequencies_hz, excursion_mm, np.abs(displacement_m))
    _write_two_column(BENCH_DIR / "oslem_spl_front_db.txt", frequencies_hz, spl_front_db, "frequency_hz\toslem_spl_front_db")
    _write_two_column(BENCH_DIR / "oslem_spl_mouth_db.txt", frequencies_hz, spl_mouth_db, "frequency_hz\toslem_spl_mouth_db")

    summary = _write_comparison_outputs(frequencies_hz, spl_total_db, zin, excursion_mm)
    (BENCH_DIR / "run_summary.txt").write_text(
        "\n".join([
            "poc2_conical_no_fill_benchmark_realignment",
            f"frequency_points={frequencies_hz.size}",
            f"spl_min_db={spl_total_db.min():.6f}",
            f"spl_max_db={spl_total_db.max():.6f}",
            f"zin_min_ohm={np.abs(zin).min():.6f}",
            f"zin_max_ohm={np.abs(zin).max():.6f}",
            f"excursion_max_mm={excursion_mm.max():.6f}",
            f"radiation_space={model['meta']['radiation_space']}",
            f"hornresp_ang_pi={case['Ang']:.6f}",
            "driver_mass_mapping=Mmd_direct_to_Mms_declared_approximation",
            "spl_phase_exported=false",
            *(f"{k}={v:.6f}" for k, v in summary.items()),
        ]) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
