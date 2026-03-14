from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from os_lem.parser import load_and_normalize
from os_lem.assemble import assemble_system
from os_lem.solve import solve_frequency_sweep, radiator_spl


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

HORNRESP_PATH = REPO_ROOT / "debug" / "hornresp_closed_box_all.txt"

OUT_DIR = REPO_ROOT / "debug"
OUT_TS_CSV = OUT_DIR / "closed_box_ts_classic_export.csv"
OUT_EXPL_CSV = OUT_DIR / "closed_box_em_explicit_export.csv"
OUT_LARGE_CSV = OUT_DIR / "closed_box_em_explicit_large_back_export.csv"
OUT_COMPARE_CSV = OUT_DIR / "closed_box_compare_all.csv"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def load_hornresp_txt(path: Path):
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Freq (hertz)"):
            header_idx = i
            break

    if header_idx is None:
        raise RuntimeError(f"Could not find Hornresp data table header in {path}")

    headers = [h.strip() for h in lines[header_idx].strip().split("\t")]

    for line in lines[header_idx + 1:]:
        s = line.strip()
        if not s:
            continue
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) != len(headers):
            continue

        row = {}
        ok = True
        for h, p in zip(headers, parts):
            try:
                row[h] = float(p)
            except ValueError:
                ok = False
                break
        if ok:
            rows.append(row)

    if not rows:
        raise RuntimeError(f"No numeric Hornresp rows parsed from {path}")

    return headers, rows


def pick_col(rows, *names):
    for name in names:
        if name in rows[0]:
            return np.array([r[name] for r in rows], dtype=float)
    raise KeyError(f"None of these columns found: {names}. Available: {list(rows[0].keys())}")


def solve_model_dict(model_dict: dict, export_csv_path: Path, label: str):
    temp_yaml = OUT_DIR / f"__tmp_{label}.yaml"
    with temp_yaml.open("w", encoding="utf-8") as f:
        yaml.safe_dump(model_dict, f, sort_keys=False)

    model, warnings = load_and_normalize(temp_yaml)
    system = assemble_system(model)

    freq = np.geomspace(10.0, 500.0, 400)
    sweep = solve_frequency_sweep(model, system, freq)

    zin = np.asarray(sweep.input_impedance)
    x_mm = np.abs(np.asarray(sweep.cone_displacement)) * 1e3
    spl_db = radiator_spl(sweep, system, "front_rad", 1.0)

    export_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with export_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "freq_hz",
                "zin_re_ohm",
                "zin_im_ohm",
                "zin_abs_ohm",
                "spl_db",
                "x_mm",
            ]
        )
        for fi, zi, si, xi in zip(freq, zin, spl_db, x_mm):
            writer.writerow([fi, zi.real, zi.imag, abs(zi), si, xi])

    try:
        temp_yaml.unlink()
    except OSError:
        pass

    return {
        "freq": freq,
        "zin": zin,
        "zabs": np.abs(zin),
        "spl_db": spl_db,
        "x_mm": x_mm,
        "warnings": warnings,
    }


def interp_at(freq_query, freq_src, values_src):
    return float(np.interp(freq_query, freq_src, values_src))


def print_summary(label, hr_freq, hr_ze, hr_spl, hr_xd, res):
    mask = (hr_freq >= 20.0) & (hr_freq <= 120.0)
    f_win = hr_freq[mask]
    z_win = np.interp(f_win, res["freq"], res["zabs"])

    hr_peak_idx = np.argmax(hr_ze[mask])
    os_peak_idx = np.argmax(z_win)

    print()
    print(f"{label} : 20–120 Hz summary")
    print(f"Hornresp peak: f = {f_win[hr_peak_idx]:.2f} Hz, |Ze| = {hr_ze[mask][hr_peak_idx]:.3f} ohm")
    print(f"os-lem peak  : f = {f_win[os_peak_idx]:.2f} Hz, |Zin| = {z_win[os_peak_idx]:.3f} ohm")

    sample_freqs = [20.0, 30.0, 40.0, 50.0, 60.0, 68.95, 80.0, 100.0]
    print()
    print("Sample points")
    print(f"{'f [Hz]':>8} {'HR Ze':>10} {'OS Ze':>10} {'HR SPL':>10} {'OS SPL':>10} {'HR Xd':>10} {'OS X':>10}")
    for sf in sample_freqs:
        hrz = interp_at(sf, hr_freq, hr_ze)
        osz = interp_at(sf, res["freq"], res["zabs"])
        hrs = interp_at(sf, hr_freq, hr_spl)
        oss = interp_at(sf, res["freq"], res["spl_db"])
        hrx = interp_at(sf, hr_freq, hr_xd)
        osx = interp_at(sf, res["freq"], res["x_mm"])
        print(f"{sf:8.2f} {hrz:10.3f} {osz:10.3f} {hrs:10.3f} {oss:10.3f} {hrx:10.3f} {osx:10.3f}")


def print_delta_summary(closed_label, closed_res, large_label, large_res):
    sample_freqs = [20.0, 30.0, 40.0, 50.0, 60.0, 68.95, 80.0, 100.0]
    print()
    print(f"Delta summary: {closed_label} vs {large_label}")
    print(f"{'f [Hz]':>8} {'Z closed':>10} {'Z large':>10} {'X closed':>10} {'X large':>10} {'SPL closed':>12} {'SPL large':>12}")
    for sf in sample_freqs:
        zc = interp_at(sf, closed_res["freq"], closed_res["zabs"])
        zl = interp_at(sf, large_res["freq"], large_res["zabs"])
        xc = interp_at(sf, closed_res["freq"], closed_res["x_mm"])
        xl = interp_at(sf, large_res["freq"], large_res["x_mm"])
        sc = interp_at(sf, closed_res["freq"], closed_res["spl_db"])
        sl = interp_at(sf, large_res["freq"], large_res["spl_db"])
        print(f"{sf:8.2f} {zc:10.3f} {zl:10.3f} {xc:10.3f} {xl:10.3f} {sc:12.3f} {sl:12.3f}")


# ------------------------------------------------------------
# Reference models
# ------------------------------------------------------------

ts_classic_model = {
    "meta": {"name": "closed_box_ts_classic_debug"},
    "driver": {
        "id": "drv1",
        "model": "ts_classic",
        "Re": "5.8 ohm",
        "Le": "0.35 mH",
        "Fs": "34.0 Hz",
        "Qes": 0.42,
        "Qms": 4.1,
        "Vas": "55.0 l",
        "Sd": "132.0 cm2",
        "node_front": "front",
        "node_rear": "rear",
    },
    "elements": [
        {"id": "front_rad", "type": "radiator", "node": "front", "model": "infinite_baffle_piston", "area": "132.0 cm2"},
        {"id": "box", "type": "volume", "node": "rear", "value": "18.0 l"},
    ],
    "observations": [
        {"id": "zin", "type": "input_impedance", "target": "drv1"},
        {"id": "spl", "type": "spl", "target": "front_rad", "distance": "1 m"},
        {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
    ],
}

em_explicit_model = {
    "meta": {"name": "closed_box_em_explicit_debug"},
    "driver": {
        "id": "drv1",
        "model": "em_explicit",
        "Re": 5.8,
        "Le": 0.00035,
        "Bl": 5.41,
        "Cms": 2.21e-03,
        "Rms": 0.52,
        "Mms": 0.00991,
        "Sd": 0.0132,
        "node_front": "front",
        "node_rear": "rear",
    },
    "elements": [
        {"id": "front_rad", "type": "radiator", "node": "front", "model": "infinite_baffle_piston", "area": 0.0132},
        {"id": "box", "type": "volume", "node": "rear", "value": 0.018},
    ],
    "observations": [
        {"id": "zin", "type": "input_impedance", "target": "drv1"},
        {"id": "spl", "type": "spl", "target": "front_rad", "distance": 1.0},
        {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
    ],
}

em_explicit_large_back_model = {
    "meta": {"name": "closed_box_em_explicit_large_back_debug"},
    "driver": {
        "id": "drv1",
        "model": "em_explicit",
        "Re": 5.8,
        "Le": 0.00035,
        "Bl": 5.41,
        "Cms": 2.21e-03,
        "Rms": 0.52,
        "Mms": 0.00991,
        "Sd": 0.0132,
        "node_front": "front",
        "node_rear": "rear",
    },
    "elements": [
        {"id": "front_rad", "type": "radiator", "node": "front", "model": "infinite_baffle_piston", "area": 0.0132},
        {"id": "box", "type": "volume", "node": "rear", "value": 1000.0},
    ],
    "observations": [
        {"id": "zin", "type": "input_impedance", "target": "drv1"},
        {"id": "spl", "type": "spl", "target": "front_rad", "distance": 1.0},
        {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
    ],
}


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    if not HORNRESP_PATH.exists():
        raise FileNotFoundError(f"Hornresp file not found: {HORNRESP_PATH}")

    _, hr_rows = load_hornresp_txt(HORNRESP_PATH)

    hr_freq = pick_col(hr_rows, "Freq (hertz)")
    hr_ze = pick_col(hr_rows, "Ze (ohms)")
    hr_spl = pick_col(hr_rows, "SPL (dB)")
    hr_xd = pick_col(hr_rows, "Xd (mm)", "Xd (mm) ")

    ts_res = solve_model_dict(ts_classic_model, OUT_TS_CSV, "ts_classic")
    em_res = solve_model_dict(em_explicit_model, OUT_EXPL_CSV, "em_explicit")
    large_res = solve_model_dict(em_explicit_large_back_model, OUT_LARGE_CSV, "em_explicit_large_back")

    print(f"Wrote os-lem export: {OUT_TS_CSV}")
    print(f"Wrote os-lem export: {OUT_EXPL_CSV}")
    print(f"Wrote os-lem export: {OUT_LARGE_CSV}")

    if ts_res["warnings"]:
        print("\nts_classic parser warnings:")
        for w in ts_res["warnings"]:
            print(" -", w)

    if em_res["warnings"]:
        print("\nem_explicit parser warnings:")
        for w in em_res["warnings"]:
            print(" -", w)

    if large_res["warnings"]:
        print("\nem_explicit_large_back parser warnings:")
        for w in large_res["warnings"]:
            print(" -", w)

    print_summary("ts_classic", hr_freq, hr_ze, hr_spl, hr_xd, ts_res)
    print_summary("em_explicit", hr_freq, hr_ze, hr_spl, hr_xd, em_res)
    print_summary("em_explicit_large_back", hr_freq, hr_ze, hr_spl, hr_xd, large_res)
    print_delta_summary("em_explicit", em_res, "em_explicit_large_back", large_res)

    ts_z = np.interp(hr_freq, ts_res["freq"], ts_res["zabs"])
    ts_spl = np.interp(hr_freq, ts_res["freq"], ts_res["spl_db"])
    ts_x = np.interp(hr_freq, ts_res["freq"], ts_res["x_mm"])

    em_z = np.interp(hr_freq, em_res["freq"], em_res["zabs"])
    em_spl = np.interp(hr_freq, em_res["freq"], em_res["spl_db"])
    em_x = np.interp(hr_freq, em_res["freq"], em_res["x_mm"])

    large_z = np.interp(hr_freq, large_res["freq"], large_res["zabs"])
    large_spl = np.interp(hr_freq, large_res["freq"], large_res["spl_db"])
    large_x = np.interp(hr_freq, large_res["freq"], large_res["x_mm"])

    with OUT_COMPARE_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "freq_hz",
                "hr_ze_ohm",
                "ts_ze_ohm",
                "large_ze_ohm",
                "em_ze_ohm",
                "hr_spl_db",
                "ts_spl_db",
                "large_spl_db",
                "em_spl_db",
                "hr_xd_mm",
                "ts_x_mm",
                "large_x_mm",
                "em_x_mm",
            ]
        )
        for i in range(len(hr_freq)):
            writer.writerow(
                [
                    hr_freq[i],
                    hr_ze[i],
                    ts_z[i],
                    large_z[i],
                    em_z[i],
                    hr_spl[i],
                    ts_spl[i],
                    large_spl[i],
                    em_spl[i],
                    hr_xd[i],
                    ts_x[i],
                    large_x[i],
                    em_x[i],
                ]
            )

    print()
    print(f"Wrote comparison export: {OUT_COMPARE_CSV}")


if __name__ == "__main__":
    main()
