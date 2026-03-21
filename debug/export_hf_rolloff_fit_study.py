from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

def _candidate_repo_roots(start: Path) -> list[Path]:
    candidates: list[Path] = []
    for p in [start, *start.parents]:
        if (p / "src" / "os_lem").exists():
            candidates.append(p)
    uniq: list[Path] = []
    seen: set[Path] = set()
    for p in candidates:
        rp = p.resolve()
        if rp not in seen:
            uniq.append(rp)
            seen.add(rp)
    return uniq

def _validate_frequency_axis(freq: np.ndarray) -> None:
    if freq.ndim != 1 or freq.size == 0:
        raise ValueError("frequency_hz must be a non-empty 1D column")
    if np.any(~np.isfinite(freq)):
        raise ValueError("frequency_hz contains non-finite values")
    if np.any(freq <= 0.0):
        raise ValueError("frequency_hz must be > 0")
    if np.any(np.diff(freq) <= 0.0):
        raise ValueError("frequency_hz must be strictly increasing")

def _load_frd(path: Path) -> dict[str, np.ndarray]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    header_idx = None
    header = None
    for i, line in enumerate(lines):
        if "Freq" in line and "SPL" in line and "WPhase" in line:
            header_idx = i
            header = [c.strip() for c in re.split(r"\t+", line.strip()) if c.strip()]
            break
    if header_idx is None or header is None:
        raise ValueError(f"Could not find FRD header in {path}")
    cols = {name: [] for name in header}
    for line in lines[header_idx + 1 :]:
        raw = line.strip()
        if not raw:
            continue
        parts = [c.strip() for c in re.split(r"\t+", raw) if c.strip()]
        if len(parts) != len(header):
            continue
        try:
            vals = [float(p) for p in parts]
        except ValueError:
            continue
        for key, val in zip(header, vals):
            cols[key].append(val)
    out = {
        "frequency_hz": np.asarray(cols["Freq (hertz)"], dtype=float),
        "spl_db": np.asarray(cols["SPL (dB)"], dtype=float),
        "phase_deg": np.asarray(cols["WPhase (deg)"], dtype=float),
    }
    _validate_frequency_axis(out["frequency_hz"])
    return out

def _load_txt_amp_phase(path: Path) -> dict[str, np.ndarray]:
    freq: list[float] = []
    amp: list[float] = []
    phase: list[float] = []
    saw_phase = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or raw.startswith("|"):
            continue
        parts = raw.split()
        if len(parts) < 2:
            continue
        try:
            f = float(parts[0])
            a = float(parts[1])
        except ValueError:
            continue
        freq.append(f)
        amp.append(a)
        if len(parts) >= 3:
            try:
                phase.append(float(parts[2]))
                saw_phase = True
            except ValueError:
                phase.append(float("nan"))
        else:
            phase.append(float("nan"))
    if not freq:
        raise ValueError(f"Could not parse amplitude table from {path}")
    out = {
        "frequency_hz": np.asarray(freq, dtype=float),
        "amp": np.asarray(amp, dtype=float),
        "phase_deg": np.asarray(phase, dtype=float),
        "has_phase": saw_phase,
    }
    _validate_frequency_axis(out["frequency_hz"])
    return out

def _safedb(amp: np.ndarray, pref: float = 20e-6) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(amp), 1e-30) / pref)

def _pressure_amp_db_from_txt(path: Path) -> tuple[np.ndarray, np.ndarray]:
    tab = _load_txt_amp_phase(path)
    return tab["frequency_hz"], _safedb(tab["amp"])

def _piston_radius_from_area(area_m2: float) -> float:
    return math.sqrt(area_m2 / math.pi)

def _f_ka1(area_m2: float, c0: float = 343.0) -> float:
    a = _piston_radius_from_area(area_m2)
    return c0 / (2.0 * math.pi * a)

def _residual_db(sim_db: np.ndarray, ref_db: np.ndarray) -> np.ndarray:
    return ref_db - sim_db

def _candidate_envelope(freq_hz: np.ndarray, f0_hz: float, order: int) -> np.ndarray:
    x = np.maximum(freq_hz / f0_hz, 1e-30)
    return -10.0 * order * np.log10(1.0 + x * x)

def _fit_envelope(freq_hz: np.ndarray, residual_db: np.ndarray, band_min_hz: float) -> dict[str, float]:
    mask = np.isfinite(freq_hz) & np.isfinite(residual_db) & (freq_hz >= band_min_hz)
    f = freq_hz[mask]
    r = residual_db[mask]
    if f.size == 0:
        return {"count": 0}
    fmin = max(float(np.min(f)), 10.0)
    fmax = max(float(np.max(f)), fmin * 1.01)
    grid = np.geomspace(fmin / 4.0, fmax * 2.0, 400)
    best: dict[str, float] | None = None
    for order in (1, 2):
        for f0 in grid:
            env = _candidate_envelope(f, f0, order)
            mae = float(np.mean(np.abs(r - env)))
            rmse = float(np.sqrt(np.mean((r - env) ** 2)))
            score = mae + 0.25 * rmse
            cand = {
                "order": int(order),
                "f0_hz": float(f0),
                "count": int(f.size),
                "mae_db": mae,
                "rmse_db": rmse,
                "score": score,
            }
            if best is None or cand["score"] < best["score"]:
                best = cand
    assert best is not None
    return best

def _write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def _maybe_plot(path: Path, freq: np.ndarray, residual: np.ndarray, fit: dict[str, float], title: str) -> str | None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None
    fig = plt.figure(figsize=(9, 5))
    ax = fig.add_subplot(111)
    ax.semilogx(freq, residual, label="reference - os-lem")
    env = _candidate_envelope(freq, fit["f0_hz"], int(fit["order"]))
    ax.semilogx(freq, env, label=f"study fit order={int(fit['order'])}, f0={fit['f0_hz']:.1f} Hz")
    ax.set_title(title)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Residual (dB)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return str(path)

def main() -> int:
    here = Path(__file__).resolve()
    repo_candidates = _candidate_repo_roots(here.parent)
    if not repo_candidates:
        raise SystemExit("Could not locate repo root containing src/os_lem")
    repo_root = repo_candidates[0]
    if str(repo_root / "src") not in sys.path:
        sys.path.insert(0, str(repo_root / "src"))

    from os_lem.assemble import assemble_system
    from os_lem.parser import load_and_normalize
    from os_lem.solve import radiator_observation_pressure, solve_frequency_sweep

    parser = argparse.ArgumentParser(description="Study missing HF attenuation against free-air and offset-line references.")
    parser.add_argument("--free-air-model", default=str(repo_root / "examples" / "free_air" / "model.yaml"))
    parser.add_argument("--offset-model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--akabak-pressure", default=str(Path("/home/vdemian/dos/spkr/AFOTEX2.TXT")))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--band-min-hz", type=float, default=1000.0)
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "hf_rolloff_fit_study_out"))
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    free_model, free_warnings = load_and_normalize(Path(args.free_air_model))
    free_sys = assemble_system(free_model)
    ak_freq, ak_spl_db = _pressure_amp_db_from_txt(Path(args.akabak_pressure))
    free_sweep = solve_frequency_sweep(free_model, free_sys, ak_freq)
    p_front = radiator_observation_pressure(free_sweep, free_sys, "rad_front", 1.0, radiation_space=args.radiation_space)
    os_free_spl = _safedb(np.abs(p_front))
    free_res = _residual_db(os_free_spl, ak_spl_db)
    free_fit = _fit_envelope(ak_freq, free_res, args.band_min_hz)
    rows_free = [{"frequency_hz": float(f), "reference_spl_db": float(r), "oslem_spl_db": float(s), "residual_db": float(d)} for f, r, s, d in zip(ak_freq, ak_spl_db, os_free_spl, free_res)]
    _write_csv(outdir / "free_air_hf_residual.csv", rows_free)
    free_png = _maybe_plot(outdir / "free_air_hf_residual.png", ak_freq, free_res, free_fit, "Free-air front radiator HF residual")

    drv_frd = _load_frd(Path(args.drv_frd))
    port_frd = _load_frd(Path(args.port_frd))
    sum_frd = _load_frd(Path(args.sum_frd))
    freqs = drv_frd["frequency_hz"]
    off_model, off_warnings = load_and_normalize(Path(args.offset_model))
    off_sys = assemble_system(off_model)
    off_sweep = solve_frequency_sweep(off_model, off_sys, freqs)
    offset_driver_radiator_id = "front_rad"
    offset_mouth_radiator_id = "mouth_rad"
    p_drv = radiator_observation_pressure(
        off_sweep,
        off_sys,
        offset_driver_radiator_id,
        1.0,
        radiation_space=args.radiation_space,
    )
    p_mouth = radiator_observation_pressure(
        off_sweep,
        off_sys,
        offset_mouth_radiator_id,
        1.0,
        radiation_space=args.radiation_space,
    )
    p_sum = p_drv + p_mouth
    os_drv = _safedb(np.abs(p_drv))
    os_mouth = _safedb(np.abs(p_mouth))
    os_sum = _safedb(np.abs(p_sum))
    drv_res = _residual_db(os_drv, drv_frd["spl_db"])
    mouth_res = _residual_db(os_mouth, port_frd["spl_db"])
    sum_res = _residual_db(os_sum, sum_frd["spl_db"])
    drv_fit = _fit_envelope(freqs, drv_res, args.band_min_hz)
    mouth_fit = _fit_envelope(freqs, mouth_res, args.band_min_hz)
    sum_fit = _fit_envelope(freqs, sum_res, args.band_min_hz)

    rows_offset = []
    for f, rd, od, dd, rp, op, dp, rs, osu, ds in zip(freqs, drv_frd["spl_db"], os_drv, drv_res, port_frd["spl_db"], os_mouth, mouth_res, sum_frd["spl_db"], os_sum, sum_res):
        rows_offset.append({
            "frequency_hz": float(f),
            "driver_ref_spl_db": float(rd),
            "driver_oslem_spl_db": float(od),
            "driver_residual_db": float(dd),
            "mouth_ref_spl_db": float(rp),
            "mouth_oslem_spl_db": float(op),
            "mouth_residual_db": float(dp),
            "sum_ref_spl_db": float(rs),
            "sum_oslem_spl_db": float(osu),
            "sum_residual_db": float(ds),
        })
    _write_csv(outdir / "offset_line_hf_residual.csv", rows_offset)
    drv_png = _maybe_plot(outdir / "offset_driver_hf_residual.png", freqs, drv_res, drv_fit, "Offset-line driver HF residual")
    mouth_png = _maybe_plot(outdir / "offset_mouth_hf_residual.png", freqs, mouth_res, mouth_fit, "Offset-line mouth HF residual")
    sum_png = _maybe_plot(outdir / "offset_sum_hf_residual.png", freqs, sum_res, sum_fit, "Offset-line total HF residual")

    area_front = next(r.area_m2 for r in free_model.radiators if r.id == "rad_front")
    summary = {
        "band_min_hz": float(args.band_min_hz),
        "free_air": {
            "model": str(args.free_air_model),
            "warnings": list(free_warnings or []),
            "f_ka1_hz_from_area": _f_ka1(float(area_front)),
            "fit": free_fit,
            "png": free_png,
        },
        "offset_line": {
            "model": str(args.offset_model),
            "warnings": list(off_warnings or []),
            "driver_radiator_id": offset_driver_radiator_id,
            "mouth_radiator_id": offset_mouth_radiator_id,
            "driver_fit": drv_fit,
            "mouth_fit": mouth_fit,
            "sum_fit": sum_fit,
            "driver_png": drv_png,
            "mouth_png": mouth_png,
            "sum_png": sum_png,
        },
        "pm_interpretation": {
            "purpose": "study whether the missing HF attenuation behaves like a shared post-knee radiator observation envelope",
            "decision_rule": {
                "free_air_and_offset_have_similar_fit": "HF discrepancy likely sits in radiator observation physics, not TL composition only",
                "offset_only_has_strong_fit": "HF discrepancy is more likely offset-line composition/discretization specific",
                "no_simple_fit": "do not inject a simple HF rolloff law into the kernel"
            },
        },
    }
    (outdir / "hf_rolloff_fit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
