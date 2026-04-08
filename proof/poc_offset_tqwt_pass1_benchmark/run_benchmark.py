from __future__ import annotations

import csv
import math
import os
import re
import sys
from pathlib import Path

# Runtime safety: cap common BLAS/OpenMP thread pools unless the operator
# explicitly overrides them before launch.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from os_lem.api import run_simulation  # noqa: E402

BENCH_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BENCH_DIR / "hornresp_source"
MODEL_PATH = BENCH_DIR / "model.yaml"


def _read_hornresp_plot_frequencies() -> np.ndarray:
    rows = np.loadtxt(SOURCE_DIR / "poc-plots.txt", skiprows=1)
    return np.asarray(rows[:, 0], dtype=float)


def _parse_poc_driver_and_meta() -> dict[str, float]:
    text = (SOURCE_DIR / "poc.txt").read_text(encoding="utf-8")
    wanted = {
        "Eg": r"^Eg\s*=\s*([0-9.+\-Ee]+)",
        "Rg": r"^Rg\s*=\s*([0-9.+\-Ee]+)",
        "Sd": r"^Sd\s*=\s*([0-9.+\-Ee]+)",
        "Bl": r"^Bl\s*=\s*([0-9.+\-Ee]+)",
        "Cms": r"^Cms\s*=\s*([0-9.+\-Ee]+)",
        "Rms": r"^Rms\s*=\s*([0-9.+\-Ee]+)",
        "Mmd": r"^Mmd\s*=\s*([0-9.+\-Ee]+)",
        "Le": r"^Le\s*=\s*([0-9.+\-Ee]+)",
        "Re": r"^Re\s*=\s*([0-9.+\-Ee]+)",
    }
    out: dict[str, float] = {}
    flags = re.MULTILINE
    for key, pattern in wanted.items():
        m = re.search(pattern, text, flags)
        if not m:
            raise RuntimeError(f"Missing {key} in poc.txt")
        out[key] = float(m.group(1))
    return out


def _parse_geometry_sections() -> list[dict[str, float]]:
    text = (SOURCE_DIR / "poc-tl-geometry.txt").read_text(encoding="utf-8")
    tables = [chunk.strip() for chunk in text.strip().split("\n\n") if chunk.strip()]
    sections: list[dict[str, float]] = []
    for table in tables:
        lines = [line.strip() for line in table.splitlines() if line.strip()]
        data_lines = [line for line in lines if not line.startswith("Length")]
        if not data_lines:
            continue
        first = data_lines[0].split()
        last = data_lines[-1].split()
        sections.append(
            {
                "length_cm": float(last[0]) - float(first[0]),
                "area_start_cm2": float(first[1]),
                "area_end_cm2": float(last[1]),
            }
        )
    if len(sections) != 2:
        raise RuntimeError(f"Expected 2 geometry sections, got {len(sections)}")
    return sections


def _load_model() -> dict:
    with MODEL_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _parse_number_and_unit(value: str) -> tuple[float, str | None]:
    m = re.match(r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z0-9]+)?\s*$", value)
    if not m:
        raise RuntimeError(f"Cannot parse model scalar {value!r}")
    unit = m.group(2)
    return float(m.group(1)), unit


def _validate_frozen_translation(model: dict) -> None:
    drv = _parse_poc_driver_and_meta()
    sections = _parse_geometry_sections()

    model_driver = model["driver"]
    assert math.isclose(model_driver["Bl"], drv["Bl"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(model_driver["Cms"], drv["Cms"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(model_driver["Rms"], drv["Rms"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(model_driver["Mms"], drv["Mmd"] * 1.0e-3, rel_tol=0.0, abs_tol=1e-12)
    re_value, re_unit = _parse_number_and_unit(model_driver["Re"])
    le_value, le_unit = _parse_number_and_unit(model_driver["Le"])
    sd_value, sd_unit = _parse_number_and_unit(model_driver["Sd"])
    assert re_unit == "ohm" and math.isclose(re_value, drv["Re"], rel_tol=0.0, abs_tol=1e-12)
    assert le_unit == "mH" and math.isclose(le_value, drv["Le"], rel_tol=0.0, abs_tol=1e-12)
    assert sd_unit == "cm2" and math.isclose(sd_value, drv["Sd"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(model_driver["source_voltage_rms"], 2.83, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(drv["Eg"], 2.83, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(drv["Rg"], 0.0, rel_tol=0.0, abs_tol=1e-12)

    model_sections = [element for element in model["elements"] if element["type"] == "waveguide_1d"]
    if len(model_sections) != 2:
        raise RuntimeError("Expected exactly two waveguide_1d sections in model.yaml")
    for model_section, source_section in zip(model_sections, sections, strict=True):
        length_value, length_unit = _parse_number_and_unit(model_section["length"])
        area_start_value, area_start_unit = _parse_number_and_unit(model_section["area_start"])
        area_end_value, area_end_unit = _parse_number_and_unit(model_section["area_end"])
        assert length_unit == "cm" and math.isclose(length_value, source_section["length_cm"], rel_tol=0.0, abs_tol=1e-9)
        assert area_start_unit == "cm2" and math.isclose(area_start_value, source_section["area_start_cm2"], rel_tol=0.0, abs_tol=1e-9)
        assert area_end_unit == "cm2" and math.isclose(area_end_value, source_section["area_end_cm2"], rel_tol=0.0, abs_tol=1e-9)


def _write_two_column(path: Path, x: np.ndarray, y: np.ndarray, header: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(header.split("\t"))
        for xv, yv in zip(x, y, strict=True):
            writer.writerow([f"{xv:.6f}", f"{yv:.12e}"])


def _write_excursion(path: Path, freq: np.ndarray, excursion_mm: np.ndarray, displacement_m: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["frequency_hz", "excursion_mm", "displacement_abs_m"])
        for f_hz, x_mm, x_m in zip(freq, excursion_mm, displacement_m, strict=True):
            writer.writerow([f"{f_hz:.6f}", f"{x_mm:.12e}", f"{x_m:.12e}"])


def main() -> None:
    model = _load_model()
    _validate_frozen_translation(model)
    frequencies_hz = _read_hornresp_plot_frequencies()
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
    spl_db = np.asarray(result.series["spl_mouth"], dtype=float)

    _write_two_column(BENCH_DIR / "oslem_spl_magnitude_db.txt", frequencies_hz, spl_db, "frequency_hz\tspl_db")
    _write_two_column(BENCH_DIR / "oslem_impedance_magnitude_ohm.txt", frequencies_hz, np.abs(zin), "frequency_hz\timpedance_magnitude_ohm")
    _write_two_column(BENCH_DIR / "oslem_impedance_phase_deg.txt", frequencies_hz, np.angle(zin, deg=True), "frequency_hz\timpedance_phase_deg")
    _write_excursion(BENCH_DIR / "oslem_cone_excursion_displacement.txt", frequencies_hz, excursion_mm, np.abs(displacement_m))

    summary_path = BENCH_DIR / "run_summary.txt"
    summary_path.write_text(
        "\n".join(
            [
                "poc_offset_tqwt_pass1_benchmark",
                f"frequency_points={frequencies_hz.size}",
                f"spl_min_db={spl_db.min():.6f}",
                f"spl_max_db={spl_db.max():.6f}",
                f"zin_min_ohm={np.abs(zin).min():.6f}",
                f"zin_max_ohm={np.abs(zin).max():.6f}",
                f"excursion_max_mm={excursion_mm.max():.6f}",
                "spl_phase_exported=false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
