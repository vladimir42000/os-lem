from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

_REFERENCE_PRESSURE_PA = 2.0e-5


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


def _phase_wrap_deg(diff: np.ndarray) -> np.ndarray:
    return ((diff + 180.0) % 360.0) - 180.0


def _phase_diff_deg(sim_deg: np.ndarray, ref_deg: np.ndarray) -> np.ndarray:
    return _phase_wrap_deg(sim_deg - ref_deg)


def _db_metrics(sim_db: np.ndarray, ref_db: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(sim_db) & np.isfinite(ref_db)
    if not np.any(mask):
        return {"count": 0}
    diff = sim_db[mask] - ref_db[mask]
    return {
        "count": int(mask.sum()),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff * diff))),
        "max_abs_error": float(np.max(np.abs(diff))),
        "mean_signed_error": float(np.mean(diff)),
    }


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
        "mean_signed_error": float(np.mean(diff)),
    }


def _spl_db(pressure_pa: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(pressure_pa), 1.0e-30) / _REFERENCE_PRESSURE_PA)


def _series_summary(sim_pressure: np.ndarray, ref: dict[str, np.ndarray]) -> dict[str, object]:
    sim_spl = _spl_db(sim_pressure)
    sim_phase = np.angle(sim_pressure, deg=True)
    return {
        "spl_db": _db_metrics(sim_spl, ref["spl_db"]),
        "phase_deg": _phase_metrics(sim_phase, ref["phase_deg"]),
    }


def generate_offset_line_compare_harness(
    *,
    repo_root: Path,
    model_path: Path,
    drv_frd_path: Path,
    port_frd_path: Path,
    sum_frd_path: Path,
    outdir: Path,
    radiation_space: str,
    distance_m: float,
) -> dict[str, object]:
    if str(repo_root / "src") not in sys.path:
        sys.path.insert(0, str(repo_root / "src"))

    from os_lem.assemble import assemble_system
    from os_lem.parser import load_and_normalize
    from os_lem.solve import radiator_observation_pressure, solve_frequency_sweep

    drv_ref = _load_frd(drv_frd_path)
    port_ref = _load_frd(port_frd_path)
    sum_ref = _load_frd(sum_frd_path)
    freqs = drv_ref["frequency_hz"]
    for label, ref in [("port", port_ref), ("sum", sum_ref)]:
        if ref["frequency_hz"].shape != freqs.shape or not np.allclose(ref["frequency_hz"], freqs, rtol=0, atol=1.0e-9):
            raise ValueError(f"{label} FRD frequency axis does not match driver FRD")

    model, warnings = load_and_normalize(model_path)
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)

    p_front_raw = radiator_observation_pressure(
        sweep,
        system,
        "front_rad",
        distance_m,
        radiation_space=radiation_space,
    )
    p_mouth_raw = radiator_observation_pressure(
        sweep,
        system,
        "mouth_rad",
        distance_m,
        radiation_space=radiation_space,
    )
    p_mouth_candidate = radiator_observation_pressure(
        sweep,
        system,
        "mouth_rad",
        distance_m,
        radiation_space=radiation_space,
        observable_contract="mouth_directivity_only",
    )
    p_sum_raw = p_front_raw + p_mouth_raw
    p_sum_candidate = p_front_raw + p_mouth_candidate

    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "offset_line_compare_harness.csv"
    json_path = outdir / "offset_line_compare_harness_summary.json"

    rows = []
    front_spl_raw = _spl_db(p_front_raw)
    mouth_spl_raw = _spl_db(p_mouth_raw)
    mouth_spl_candidate = _spl_db(p_mouth_candidate)
    sum_spl_raw = _spl_db(p_sum_raw)
    sum_spl_candidate = _spl_db(p_sum_candidate)
    front_phase_raw = np.angle(p_front_raw, deg=True)
    mouth_phase_raw = np.angle(p_mouth_raw, deg=True)
    mouth_phase_candidate = np.angle(p_mouth_candidate, deg=True)
    sum_phase_raw = np.angle(p_sum_raw, deg=True)
    sum_phase_candidate = np.angle(p_sum_candidate, deg=True)

    for i, f_hz in enumerate(freqs):
        rows.append(
            {
                "frequency_hz": float(f_hz),
                "front_ref_spl_db": float(drv_ref["spl_db"][i]),
                "front_raw_spl_db": float(front_spl_raw[i]),
                "front_raw_delta_spl_db": float(front_spl_raw[i] - drv_ref["spl_db"][i]),
                "front_ref_phase_deg": float(drv_ref["phase_deg"][i]),
                "front_raw_phase_deg": float(front_phase_raw[i]),
                "front_raw_delta_phase_deg": float(_phase_diff_deg(np.array([front_phase_raw[i]]), np.array([drv_ref["phase_deg"][i]]))[0]),
                "mouth_ref_spl_db": float(port_ref["spl_db"][i]),
                "mouth_raw_spl_db": float(mouth_spl_raw[i]),
                "mouth_raw_delta_spl_db": float(mouth_spl_raw[i] - port_ref["spl_db"][i]),
                "mouth_candidate_spl_db": float(mouth_spl_candidate[i]),
                "mouth_candidate_delta_spl_db": float(mouth_spl_candidate[i] - port_ref["spl_db"][i]),
                "mouth_ref_phase_deg": float(port_ref["phase_deg"][i]),
                "mouth_raw_phase_deg": float(mouth_phase_raw[i]),
                "mouth_raw_delta_phase_deg": float(_phase_diff_deg(np.array([mouth_phase_raw[i]]), np.array([port_ref["phase_deg"][i]]))[0]),
                "mouth_candidate_phase_deg": float(mouth_phase_candidate[i]),
                "mouth_candidate_delta_phase_deg": float(_phase_diff_deg(np.array([mouth_phase_candidate[i]]), np.array([port_ref["phase_deg"][i]]))[0]),
                "sum_ref_spl_db": float(sum_ref["spl_db"][i]),
                "sum_raw_spl_db": float(sum_spl_raw[i]),
                "sum_raw_delta_spl_db": float(sum_spl_raw[i] - sum_ref["spl_db"][i]),
                "sum_candidate_spl_db": float(sum_spl_candidate[i]),
                "sum_candidate_delta_spl_db": float(sum_spl_candidate[i] - sum_ref["spl_db"][i]),
                "sum_ref_phase_deg": float(sum_ref["phase_deg"][i]),
                "sum_raw_phase_deg": float(sum_phase_raw[i]),
                "sum_raw_delta_phase_deg": float(_phase_diff_deg(np.array([sum_phase_raw[i]]), np.array([sum_ref["phase_deg"][i]]))[0]),
                "sum_candidate_phase_deg": float(sum_phase_candidate[i]),
                "sum_candidate_delta_phase_deg": float(_phase_diff_deg(np.array([sum_phase_candidate[i]]), np.array([sum_ref["phase_deg"][i]]))[0]),
            }
        )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary: dict[str, object] = {
        "model": str(model_path),
        "drv_frd": str(drv_frd_path),
        "port_frd": str(port_frd_path),
        "sum_frd": str(sum_frd_path),
        "points": int(freqs.size),
        "radiation_space": radiation_space,
        "distance_m": float(distance_m),
        "candidate_contract": "mouth_directivity_only",
        "warnings": list(warnings or []),
        "series": {
            "front_raw": _series_summary(p_front_raw, drv_ref),
            "mouth_raw": _series_summary(p_mouth_raw, port_ref),
            "mouth_candidate": _series_summary(p_mouth_candidate, port_ref),
            "sum_raw": _series_summary(p_sum_raw, sum_ref),
            "sum_candidate": _series_summary(p_sum_candidate, sum_ref),
        },
        "paths": {
            "csv": str(csv_path),
            "json": str(json_path),
        },
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    here = Path(__file__).resolve()
    repo_candidates = _candidate_repo_roots(here.parent)
    if not repo_candidates:
        raise SystemExit("Could not locate repo root containing src/os_lem")
    repo_root = repo_candidates[0]

    parser = argparse.ArgumentParser(
        description="Generate one maintained offset-line compare harness for raw vs bounded mouth observation contracts."
    )
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_compare_harness_out"))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--distance-m", type=float, default=1.0)
    args = parser.parse_args()

    summary = generate_offset_line_compare_harness(
        repo_root=repo_root,
        model_path=Path(args.model),
        drv_frd_path=Path(args.drv_frd),
        port_frd_path=Path(args.port_frd),
        sum_frd_path=Path(args.sum_frd),
        outdir=Path(args.outdir),
        radiation_space=args.radiation_space,
        distance_m=args.distance_m,
    )

    print("Offset-line compare harness artifacts written:")
    print(f"  CSV:  {summary['paths']['csv']}")
    print(f"  JSON: {summary['paths']['json']}")
    print("")
    print("Summary metrics:")
    for key, value in summary["series"].items():
        print(f"  {key}:")
        print(f"    spl_db:   {value['spl_db']}")
        print(f"    phase_deg:{value['phase_deg']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
