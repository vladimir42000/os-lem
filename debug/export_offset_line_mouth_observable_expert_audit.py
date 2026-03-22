from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.special import j1

P_REF = 20.0e-6
C0 = 343.0
PI = math.pi
RHO0 = 1.2041


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
        raise ValueError("frequency_hz must be non-empty 1D")
    if np.any(~np.isfinite(freq)) or np.any(freq <= 0.0) or np.any(np.diff(freq) <= 0.0):
        raise ValueError("invalid frequency axis")


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


def _complex_from_spl_phase(spl_db: np.ndarray, phase_deg: np.ndarray) -> np.ndarray:
    mag_pa = P_REF * (10.0 ** (spl_db / 20.0))
    return mag_pa * np.exp(1j * np.deg2rad(phase_deg))


def _spl_db(x: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-30) / P_REF)


def _phase_deg(x: np.ndarray) -> np.ndarray:
    return np.angle(x, deg=True)


def _phase_wrap_deg(x: np.ndarray) -> np.ndarray:
    return ((x + 180.0) % 360.0) - 180.0


def _complex_rel_rmse(sim: np.ndarray, ref: np.ndarray) -> float:
    mask = np.isfinite(sim) & np.isfinite(ref)
    if not np.any(mask):
        return float("nan")
    denom = np.sqrt(np.mean(np.abs(ref[mask]) ** 2))
    if denom == 0.0:
        return float("nan")
    return float(np.sqrt(np.mean(np.abs(sim[mask] - ref[mask]) ** 2)) / denom)


def _mae(x: np.ndarray) -> float:
    mask = np.isfinite(x)
    return float(np.mean(np.abs(x[mask]))) if np.any(mask) else float("nan")


def _metrics(freq: np.ndarray, sim: np.ndarray, ref: np.ndarray, hf_min_hz: float) -> dict[str, float]:
    spl_sim = _spl_db(sim)
    spl_ref = _spl_db(ref)
    ph_sim = _phase_deg(sim)
    ph_ref = _phase_deg(ref)
    hf = freq >= hf_min_hz
    return {
        "all_spl_mae_db": _mae(spl_sim - spl_ref),
        "hf_spl_mae_db": _mae((spl_sim - spl_ref)[hf]),
        "all_phase_mae_deg": _mae(_phase_wrap_deg(ph_sim - ph_ref)),
        "hf_phase_mae_deg": _mae(_phase_wrap_deg(ph_sim[hf] - ph_ref[hf])),
        "all_complex_rel_rmse": _complex_rel_rmse(sim, ref),
        "hf_complex_rel_rmse": _complex_rel_rmse(sim[hf], ref[hf]),
    }


def _plot(freq: np.ndarray, curves: dict[str, np.ndarray], ylabel: str, title: str, outpath: Path) -> None:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    for label, values in curves.items():
        plt.semilogx(freq, values, label=label)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()


def _prop_factor(freq: np.ndarray, distance_m: float) -> np.ndarray:
    return np.exp(-1j * 2.0 * np.pi * freq * distance_m / C0)


def _directivity_on_axis(freq: np.ndarray, area_m2: float) -> np.ndarray:
    a = math.sqrt(area_m2 / PI)
    ka = (2.0 * np.pi * freq / C0) * a
    out = np.ones_like(freq, dtype=np.complex128)
    nz = np.abs(ka) > 1e-12
    out[nz] = (2.0 * j1(ka[nz]) / ka[nz]).astype(np.complex128)
    return out


def _find_mouth_path_length_m(model) -> float | None:
    source = model.driver.node_rear
    target = None
    for rad in model.radiators:
        if rad.id == "mouth_rad":
            target = rad.node
            break
    if target is None:
        return None

    graph: dict[str, list[tuple[str, float]]] = {}
    def add_edge(a: str, b: str, length: float) -> None:
        graph.setdefault(a, []).append((b, length))
        graph.setdefault(b, []).append((a, length))

    for wg in model.waveguides:
        add_edge(wg.node_a, wg.node_b, float(wg.length_m))
    for duct in model.ducts:
        add_edge(duct.node_a, duct.node_b, float(duct.length_m))

    import heapq
    dist: dict[str, float] = {source: 0.0}
    pq: list[tuple[float, str]] = [(0.0, source)]
    while pq:
        d, node = heapq.heappop(pq)
        if node == target:
            return d
        if d != dist.get(node, float("inf")):
            continue
        for nxt, w in graph.get(node, []):
            nd = d + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                heapq.heappush(pq, (nd, nxt))
    return None


def _write_ranked_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    here = Path(__file__).resolve()
    repo_candidates = _candidate_repo_roots(here.parent)
    if not repo_candidates:
        raise SystemExit("Could not locate repo root containing src/os_lem")
    repo_root = repo_candidates[0]
    if str(repo_root / "src") not in sys.path:
        sys.path.insert(0, str(repo_root / "src"))

    from os_lem.assemble import assemble_system
    from os_lem.elements.radiator import radiator_observation_transfer
    from os_lem.parser import load_and_normalize
    from os_lem.solve import radiator_observation_pressure, solve_frequency_sweep

    parser = argparse.ArgumentParser(description="Audit expert mouth-observable hypotheses while keeping front/raw unchanged.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_mouth_observable_expert_audit_out"))
    parser.add_argument("--distance-m", type=float, default=1.0)
    parser.add_argument("--radiation-space-front", default="2pi")
    parser.add_argument("--radiation-space-mouth-raw", default="2pi")
    parser.add_argument("--phase-source-position-m", type=float, default=None)
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    sum_frd = _load_frd(Path(args.sum_frd))
    drv_frd = _load_frd(Path(args.drv_frd))
    port_frd = _load_frd(Path(args.port_frd))
    freqs = sum_frd["frequency_hz"]

    model, warnings = load_and_normalize(Path(args.model))
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)

    p_front_raw = radiator_observation_pressure(sweep, system, "front_rad", args.distance_m, radiation_space=args.radiation_space_front)
    p_mouth_raw = radiator_observation_pressure(sweep, system, "mouth_rad", args.distance_m, radiation_space=args.radiation_space_mouth_raw)

    mouth_rad = next(rad for rad in model.radiators if rad.id == "mouth_rad")
    h_mouth_raw = np.array([
        radiator_observation_transfer(mouth_rad.model, float(omega), args.distance_m, radiation_space=args.radiation_space_mouth_raw)
        for omega in sweep.omega_rad_s
    ], dtype=np.complex128)
    q_mouth = p_mouth_raw / h_mouth_raw

    h_mouth_4pi = np.array([
        radiator_observation_transfer(mouth_rad.model, float(omega), args.distance_m, radiation_space="4pi")
        for omega in sweep.omega_rad_s
    ], dtype=np.complex128)
    directivity = _directivity_on_axis(freqs, mouth_rad.area_m2)

    inferred_phase_source_position_m = _find_mouth_path_length_m(model)
    phase_source_position_m = args.phase_source_position_m
    if phase_source_position_m is None:
        phase_source_position_m = inferred_phase_source_position_m
    include_phase = phase_source_position_m is not None

    scenarios: dict[str, np.ndarray] = {
        "raw_2pi": p_mouth_raw,
        "mouth_4pi_only": h_mouth_4pi * q_mouth,
        "mouth_directivity_only": h_mouth_raw * directivity * q_mouth,
        "mouth_4pi_plus_directivity": h_mouth_4pi * directivity * q_mouth,
    }
    if include_phase:
        phase_factor = _prop_factor(freqs, float(phase_source_position_m))
        scenarios["mouth_4pi_plus_directivity_plus_phase"] = h_mouth_4pi * directivity * phase_factor * q_mouth

    ref_front = -_complex_from_spl_phase(drv_frd["spl_db"], drv_frd["phase_deg"])
    ref_mouth = -_complex_from_spl_phase(port_frd["spl_db"], port_frd["phase_deg"])
    ref_sum = -_complex_from_spl_phase(sum_frd["spl_db"], sum_frd["phase_deg"])

    ranked: list[dict[str, object]] = []
    scenario_metrics: dict[str, dict[str, object]] = {}
    mouth_spl_residuals: dict[str, np.ndarray] = {}
    mouth_phase_residuals: dict[str, np.ndarray] = {}
    sum_spl_residuals: dict[str, np.ndarray] = {}
    sum_phase_residuals: dict[str, np.ndarray] = {}

    for name, p_mouth in scenarios.items():
        p_sum = p_front_raw + p_mouth
        mouth_metrics = _metrics(freqs, p_mouth, ref_mouth, args.hf_min_hz)
        sum_metrics = _metrics(freqs, p_sum, ref_sum, args.hf_min_hz)
        front_metrics = _metrics(freqs, p_front_raw, ref_front, args.hf_min_hz)
        scenario_metrics[name] = {
            "front_all": front_metrics,
            "mouth_all": mouth_metrics,
            "sum_all": sum_metrics,
        }
        mouth_spl_residuals[name] = _spl_db(p_mouth) - _spl_db(ref_mouth)
        mouth_phase_residuals[name] = _phase_wrap_deg(_phase_deg(p_mouth) - _phase_deg(ref_mouth))
        sum_spl_residuals[name] = _spl_db(p_sum) - _spl_db(ref_sum)
        sum_phase_residuals[name] = _phase_wrap_deg(_phase_deg(p_sum) - _phase_deg(ref_sum))
        ranked.append({
            "scenario": name,
            "mouth_hf_spl_mae_db": mouth_metrics["hf_spl_mae_db"],
            "mouth_hf_phase_mae_deg": mouth_metrics["hf_phase_mae_deg"],
            "mouth_hf_complex_rel_rmse": mouth_metrics["hf_complex_rel_rmse"],
            "sum_hf_spl_mae_db": sum_metrics["hf_spl_mae_db"],
            "sum_hf_phase_mae_deg": sum_metrics["hf_phase_mae_deg"],
            "sum_hf_complex_rel_rmse": sum_metrics["hf_complex_rel_rmse"],
        })

    ranked.sort(key=lambda r: (float(r["sum_hf_complex_rel_rmse"]), float(r["sum_hf_phase_mae_deg"]), float(r["sum_hf_spl_mae_db"])))
    best = ranked[0] if ranked else None

    _write_ranked_csv(outdir / "offset_line_mouth_observable_ranked.csv", ranked)
    _plot(freqs, mouth_spl_residuals, "Mouth SPL residual (dB)", "Offset-line mouth observable expert audit: mouth SPL residual", outdir / "offset_line_mouth_observable_mouth_spl_residual.png")
    _plot(freqs, mouth_phase_residuals, "Mouth phase residual (deg)", "Offset-line mouth observable expert audit: mouth phase residual", outdir / "offset_line_mouth_observable_mouth_phase_residual.png")
    _plot(freqs, sum_spl_residuals, "Sum SPL residual (dB)", "Offset-line mouth observable expert audit: sum SPL residual", outdir / "offset_line_mouth_observable_sum_spl_residual.png")
    _plot(freqs, sum_phase_residuals, "Sum phase residual (deg)", "Offset-line mouth observable expert audit: sum phase residual", outdir / "offset_line_mouth_observable_sum_phase_residual.png")

    summary = {
        "model": args.model,
        "phase_reference_distance_m": args.distance_m,
        "mouth_source_position_m": phase_source_position_m,
        "inferred_mouth_source_position_m": inferred_phase_source_position_m,
        "phase_scenario_included": include_phase,
        "warnings": warnings,
        "ranked_scenarios": ranked,
        "best_scenario": best,
        "scenario_metrics": scenario_metrics,
        "pm_interpretation": {
            "purpose": "test expert mouth-observable hypotheses while keeping front/raw unchanged",
            "decision_rules": {
                "mouth_4pi_plus_directivity_best": "expert amplitude/radiation-space hypothesis is strongly supported in the observation layer",
                "mouth_4pi_plus_directivity_plus_phase_best": "expert amplitude/radiation-space hypothesis helps, and an additional mouth source-position phase hypothesis is also useful",
                "raw_2pi_best": "current raw mouth observation remains the closest practical contract; residual mismatch stays an observable-definition issue"
            }
        },
    }
    (outdir / "offset_line_mouth_observable_expert_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({
        "summary_json": str(outdir / "offset_line_mouth_observable_expert_audit_summary.json"),
        "best_scenario": best,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
