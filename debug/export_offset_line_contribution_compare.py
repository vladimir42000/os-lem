from __future__ import annotations

import argparse
import csv
import json
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


def _metrics(sim: np.ndarray, ref: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(sim) & np.isfinite(ref)
    if not np.any(mask):
        return {"count": 0}
    diff = sim[mask] - ref[mask]
    return {
        "count": int(mask.sum()),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff * diff))),
        "max_abs_error": float(np.max(np.abs(diff))),
    }


def _phase_wrap_deg(diff: np.ndarray) -> np.ndarray:
    return ((diff + 180.0) % 360.0) - 180.0


def _phase_diff_deg(sim_deg: np.ndarray, ref_deg: np.ndarray) -> np.ndarray:
    return _phase_wrap_deg(sim_deg - ref_deg)


def _phase_metrics(sim_deg: np.ndarray, ref_deg: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(sim_deg) & np.isfinite(ref_deg)
    if not np.any(mask):
        return {"count": 0}
    diff = _phase_diff_deg(sim_deg[mask], ref_deg[mask])
    return {
        "count": int(mask.sum()),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff * diff))),
        "max_abs_error": float(np.max(np.abs(diff))),
    }


def _band_metrics(freq: np.ndarray, sim: np.ndarray, ref: np.ndarray, bands: list[tuple[float, float]], phase: bool = False) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for f_lo, f_hi in bands:
        mask = (freq >= f_lo) & (freq < f_hi) & np.isfinite(sim) & np.isfinite(ref)
        key = f"{f_lo:g}-{f_hi:g}_Hz"
        if not np.any(mask):
            out[key] = {"count": 0}
            continue
        diff = _phase_diff_deg(sim[mask], ref[mask]) if phase else (sim[mask] - ref[mask])
        out[key] = {
            "count": int(mask.sum()),
            "mae": float(np.mean(np.abs(diff))),
            "rmse": float(np.sqrt(np.mean(diff * diff))),
            "max_abs_error": float(np.max(np.abs(diff))),
        }
    return out


def _normalize_phase_reference(phase_deg: np.ndarray, freqs_hz: np.ndarray, distance_m: float, polarity_flip: bool) -> np.ndarray:
    k_d_deg = 360.0 * freqs_hz * distance_m / 343.0
    out = phase_deg + k_d_deg
    if polarity_flip:
        out = out - 180.0
    return _phase_wrap_deg(out)


def main() -> int:
    here = Path(__file__).resolve()
    repo_candidates = _candidate_repo_roots(here.parent)
    if not repo_candidates:
        raise SystemExit("Could not locate repo root containing src/os_lem")
    repo_root = repo_candidates[0]

    if str(repo_root / "src") not in sys.path:
        sys.path.insert(0, str(repo_root / "src"))

    from os_lem.assemble import assemble_system
    from os_lem.constants import P_REF
    from os_lem.parser import load_and_normalize
    from os_lem.solve import radiator_observation_pressure, solve_frequency_sweep

    parser = argparse.ArgumentParser(description="Compare Hornresp vs os-lem driver, port, and total radiated responses.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_contribution_compare_out"))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--phase-reference-distance-m", type=float, default=1.0)
    parser.add_argument("--phase-polarity-flip", action="store_true")
    args = parser.parse_args()

    sum_frd = _load_frd(Path(args.sum_frd))
    drv_frd = _load_frd(Path(args.drv_frd))
    port_frd = _load_frd(Path(args.port_frd))

    freqs = sum_frd["frequency_hz"]
    for name, frd in {"drv": drv_frd, "port": port_frd}.items():
        if frd["frequency_hz"].shape != freqs.shape or not np.allclose(frd["frequency_hz"], freqs, rtol=0, atol=1e-9):
            raise ValueError(f"{name} FRD frequency axis does not match sum FRD")

    model, warnings = load_and_normalize(Path(args.model))
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)

    p_drv = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space=args.radiation_space)
    p_port = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space=args.radiation_space)
    p_sum = p_drv + p_port

    spl_drv = 20.0 * np.log10(np.maximum(np.abs(p_drv), 1e-30) / P_REF)
    spl_port = 20.0 * np.log10(np.maximum(np.abs(p_port), 1e-30) / P_REF)
    spl_sum = 20.0 * np.log10(np.maximum(np.abs(p_sum), 1e-30) / P_REF)

    phase_drv = np.angle(p_drv, deg=True)
    phase_port = np.angle(p_port, deg=True)
    phase_sum = np.angle(p_sum, deg=True)

    phase_drv_norm = _normalize_phase_reference(phase_drv, freqs, args.phase_reference_distance_m, args.phase_polarity_flip)
    phase_port_norm = _normalize_phase_reference(phase_port, freqs, args.phase_reference_distance_m, args.phase_polarity_flip)
    phase_sum_norm = _normalize_phase_reference(phase_sum, freqs, args.phase_reference_distance_m, args.phase_polarity_flip)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "offset_line_contribution_compare.csv"
    json_path = outdir / "offset_line_contribution_summary.json"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "frequency_hz",
                "hornresp_drv_spl_db", "oslem_drv_spl_db", "delta_drv_spl_db",
                "hornresp_drv_phase_deg", "oslem_drv_phase_deg", "oslem_drv_phase_norm_deg", "delta_drv_phase_deg", "delta_drv_phase_norm_deg",
                "hornresp_port_spl_db", "oslem_port_spl_db", "delta_port_spl_db",
                "hornresp_port_phase_deg", "oslem_port_phase_deg", "oslem_port_phase_norm_deg", "delta_port_phase_deg", "delta_port_phase_norm_deg",
                "hornresp_sum_spl_db", "oslem_sum_spl_db", "delta_sum_spl_db",
                "hornresp_sum_phase_deg", "oslem_sum_phase_deg", "oslem_sum_phase_norm_deg", "delta_sum_phase_deg", "delta_sum_phase_norm_deg",
            ],
        )
        writer.writeheader()
        for i, f_hz in enumerate(freqs):
            writer.writerow(
                {
                    "frequency_hz": float(f_hz),
                    "hornresp_drv_spl_db": float(drv_frd["spl_db"][i]),
                    "oslem_drv_spl_db": float(spl_drv[i]),
                    "delta_drv_spl_db": float(spl_drv[i] - drv_frd["spl_db"][i]),
                    "hornresp_drv_phase_deg": float(drv_frd["phase_deg"][i]),
                    "oslem_drv_phase_deg": float(phase_drv[i]),
                    "oslem_drv_phase_norm_deg": float(phase_drv_norm[i]),
                    "delta_drv_phase_deg": float(_phase_diff_deg(np.array([phase_drv[i]]), np.array([drv_frd["phase_deg"][i]]))[0]),
                    "delta_drv_phase_norm_deg": float(_phase_diff_deg(np.array([phase_drv_norm[i]]), np.array([drv_frd["phase_deg"][i]]))[0]),
                    "hornresp_port_spl_db": float(port_frd["spl_db"][i]),
                    "oslem_port_spl_db": float(spl_port[i]),
                    "delta_port_spl_db": float(spl_port[i] - port_frd["spl_db"][i]),
                    "hornresp_port_phase_deg": float(port_frd["phase_deg"][i]),
                    "oslem_port_phase_deg": float(phase_port[i]),
                    "oslem_port_phase_norm_deg": float(phase_port_norm[i]),
                    "delta_port_phase_deg": float(_phase_diff_deg(np.array([phase_port[i]]), np.array([port_frd["phase_deg"][i]]))[0]),
                    "delta_port_phase_norm_deg": float(_phase_diff_deg(np.array([phase_port_norm[i]]), np.array([port_frd["phase_deg"][i]]))[0]),
                    "hornresp_sum_spl_db": float(sum_frd["spl_db"][i]),
                    "oslem_sum_spl_db": float(spl_sum[i]),
                    "delta_sum_spl_db": float(spl_sum[i] - sum_frd["spl_db"][i]),
                    "hornresp_sum_phase_deg": float(sum_frd["phase_deg"][i]),
                    "oslem_sum_phase_deg": float(phase_sum[i]),
                    "oslem_sum_phase_norm_deg": float(phase_sum_norm[i]),
                    "delta_sum_phase_deg": float(_phase_diff_deg(np.array([phase_sum[i]]), np.array([sum_frd["phase_deg"][i]]))[0]),
                    "delta_sum_phase_norm_deg": float(_phase_diff_deg(np.array([phase_sum_norm[i]]), np.array([sum_frd["phase_deg"][i]]))[0]),
                }
            )

    bands = [(10.0, 200.0), (200.0, 1000.0), (1000.0, 5000.0), (5000.0, 20000.1)]
    summary = {
        "model": str(args.model),
        "sum_frd": str(args.sum_frd),
        "drv_frd": str(args.drv_frd),
        "port_frd": str(args.port_frd),
        "points": int(freqs.size),
        "radiation_space": args.radiation_space,
        "phase_reference_distance_m": float(args.phase_reference_distance_m),
        "phase_polarity_flip": bool(args.phase_polarity_flip),
        "warnings": list(warnings or []),
        "driver_spl_db": _metrics(spl_drv, drv_frd["spl_db"]),
        "driver_phase_deg_raw": _phase_metrics(phase_drv, drv_frd["phase_deg"]),
        "driver_phase_deg_norm": _phase_metrics(phase_drv_norm, drv_frd["phase_deg"]),
        "port_spl_db": _metrics(spl_port, port_frd["spl_db"]),
        "port_phase_deg_raw": _phase_metrics(phase_port, port_frd["phase_deg"]),
        "port_phase_deg_norm": _phase_metrics(phase_port_norm, port_frd["phase_deg"]),
        "sum_spl_db": _metrics(spl_sum, sum_frd["spl_db"]),
        "sum_phase_deg_raw": _phase_metrics(phase_sum, sum_frd["phase_deg"]),
        "sum_phase_deg_norm": _phase_metrics(phase_sum_norm, sum_frd["phase_deg"]),
        "driver_phase_bands_norm": _band_metrics(freqs, phase_drv_norm, drv_frd["phase_deg"], bands, phase=True),
        "port_phase_bands_norm": _band_metrics(freqs, phase_port_norm, port_frd["phase_deg"], bands, phase=True),
        "sum_phase_bands_norm": _band_metrics(freqs, phase_sum_norm, sum_frd["phase_deg"], bands, phase=True),
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Contribution comparison artifacts written:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    print("")
    print("Overall SPL metrics:")
    print(f"  driver: {summary['driver_spl_db']}")
    print(f"  port:   {summary['port_spl_db']}")
    print(f"  sum:    {summary['sum_spl_db']}")
    print("")
    print("Overall phase metrics:")
    print(f"  driver raw:  {summary['driver_phase_deg_raw']}")
    print(f"  driver norm: {summary['driver_phase_deg_norm']}")
    print(f"  port raw:    {summary['port_phase_deg_raw']}")
    print(f"  port norm:   {summary['port_phase_deg_norm']}")
    print(f"  sum raw:     {summary['sum_phase_deg_raw']}")
    print(f"  sum norm:    {summary['sum_phase_deg_norm']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
