from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

P_REF = 20.0e-6


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


def _phase_wrap_deg(x: np.ndarray) -> np.ndarray:
    return ((x + 180.0) % 360.0) - 180.0


def _complex_from_spl_phase(spl_db: np.ndarray, phase_deg: np.ndarray) -> np.ndarray:
    mag_pa = P_REF * (10.0 ** (spl_db / 20.0))
    return mag_pa * np.exp(1j * np.deg2rad(phase_deg))


def _spl_db(x: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-30) / P_REF)


def _phase_deg(x: np.ndarray) -> np.ndarray:
    return np.angle(x, deg=True)


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


def _matrix_from_json(obj: dict[str, object]) -> np.ndarray:
    e = obj["entries"]
    return np.array(
        [
            [complex(e["front_from_front"]["real"], e["front_from_front"]["imag"]), complex(e["front_from_mouth"]["real"], e["front_from_mouth"]["imag"])],
            [complex(e["mouth_from_front"]["real"], e["mouth_from_front"]["imag"]), complex(e["mouth_from_mouth"]["real"], e["mouth_from_mouth"]["imag"])],
        ],
        dtype=np.complex128,
    )


def _apply_two_band_mix(freq: np.ndarray, front: np.ndarray, mouth: np.ndarray, summary: dict[str, object]) -> tuple[np.ndarray, np.ndarray]:
    mix = summary["best_two_band_basis_mix"]
    crossover_hz = float(mix["crossover_hz"])
    low_m = _matrix_from_json(mix["low_matrix"])
    high_m = _matrix_from_json(mix["high_matrix"])
    in_vec = np.vstack([front, mouth])
    out_front = np.empty_like(front)
    out_mouth = np.empty_like(mouth)
    lo = freq < crossover_hz
    hi = ~lo
    if np.any(lo):
        out = low_m @ in_vec[:, lo]
        out_front[lo] = out[0]
        out_mouth[lo] = out[1]
    if np.any(hi):
        out = high_m @ in_vec[:, hi]
        out_front[hi] = out[0]
        out_mouth[hi] = out[1]
    return out_front, out_mouth


def _prop_factor(freq: np.ndarray, distance_m: float) -> np.ndarray:
    return np.exp(-1j * 2.0 * np.pi * freq * distance_m / 343.0)


def _scenario_components(freq: np.ndarray, front: np.ndarray, mouth: np.ndarray, refdist_m: float, mouth_source_pos_m: float, scenario: str) -> tuple[np.ndarray, np.ndarray]:
    one = np.ones_like(freq, dtype=np.complex128)
    g = _prop_factor(freq, refdist_m)
    m = _prop_factor(freq, mouth_source_pos_m)
    if scenario == "raw":
        return front, mouth
    if scenario == "two_band":
        return front, mouth
    if scenario == "global_both":
        return front * g, mouth * g
    if scenario == "differential_mouth":
        return front * one, mouth * m
    if scenario == "global_plus_differential":
        return front * g, mouth * g * m
    raise ValueError(f"unknown scenario {scenario}")


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

    parser = argparse.ArgumentParser(description="Audit global observer phase vs mouth differential source phase after best two-band basis mixing.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--two-band-summary", default=str(repo_root / "debug" / "offset_line_two_band_basis_mixing_audit_out" / "offset_line_two_band_basis_mixing_summary.json"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_observer_phase_split_audit_out"))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--phase-reference-distance-m", type=float, default=1.0)
    parser.add_argument("--mouth-source-position-m", type=float, default=1.0)
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
    args = parser.parse_args()

    sum_frd = _load_frd(Path(args.sum_frd))
    drv_frd = _load_frd(Path(args.drv_frd))
    port_frd = _load_frd(Path(args.port_frd))
    freqs = sum_frd["frequency_hz"]

    model, _warnings = load_and_normalize(Path(args.model))
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)
    p_front = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space=args.radiation_space)
    p_mouth = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space=args.radiation_space)

    summary = json.loads(Path(args.two_band_summary).read_text(encoding="utf-8"))
    mixed_front, mixed_mouth = _apply_two_band_mix(freqs, p_front, p_mouth, summary)

    ref_front = -_complex_from_spl_phase(drv_frd["spl_db"], drv_frd["phase_deg"])
    ref_mouth = -_complex_from_spl_phase(port_frd["spl_db"], port_frd["phase_deg"])
    ref_sum = -_complex_from_spl_phase(sum_frd["spl_db"], sum_frd["phase_deg"])

    scenarios = {
        "raw": (p_front, p_mouth),
        "two_band": (mixed_front, mixed_mouth),
        "global_both": _scenario_components(freqs, mixed_front, mixed_mouth, args.phase_reference_distance_m, args.mouth_source_position_m, "global_both"),
        "differential_mouth": _scenario_components(freqs, mixed_front, mixed_mouth, args.phase_reference_distance_m, args.mouth_source_position_m, "differential_mouth"),
        "global_plus_differential": _scenario_components(freqs, mixed_front, mixed_mouth, args.phase_reference_distance_m, args.mouth_source_position_m, "global_plus_differential"),
    }

    ranked = []
    results: dict[str, dict[str, object]] = {}
    for name, (front_sim, mouth_sim) in scenarios.items():
        sum_sim = front_sim + mouth_sim
        res = {
            "front_all": _metrics(freqs, front_sim, ref_front, args.hf_min_hz),
            "mouth_all": _metrics(freqs, mouth_sim, ref_mouth, args.hf_min_hz),
            "sum_all": _metrics(freqs, sum_sim, ref_sum, args.hf_min_hz),
        }
        results[name] = {
            "front": front_sim,
            "mouth": mouth_sim,
            "sum": sum_sim,
            "metrics": res,
        }
        ranked.append({
            "scenario": name,
            "sum_hf_spl_mae_db": res["sum_all"]["hf_spl_mae_db"],
            "sum_hf_phase_mae_deg": res["sum_all"]["hf_phase_mae_deg"],
            "sum_hf_complex_rel_rmse": res["sum_all"]["hf_complex_rel_rmse"],
        })
    ranked.sort(key=lambda r: (r["sum_hf_complex_rel_rmse"], r["sum_hf_phase_mae_deg"]))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    summary_out = {
        "phase_reference_distance_m": float(args.phase_reference_distance_m),
        "mouth_source_position_m": float(args.mouth_source_position_m),
        "best_two_band_basis_mix": summary.get("best_crossover_hz", summary.get("best_two_band_basis_mix", {}).get("crossover_hz")),
        "ranked_scenarios": ranked,
        "pm_interpretation": {
            "purpose": "separate global observer propagation phase from mouth differential source-position phase after best two-band basis mixing",
            "decision_rules": {
                "global_both_best": "missing global observer-phase contract dominates",
                "differential_mouth_best": "missing mouth differential source-position phase dominates",
                "global_plus_differential_best": "both global observer phase and mouth differential source-position phase are needed",
            },
        },
        "scenario_metrics": {
            name: {
                "front_all": data["metrics"]["front_all"],
                "mouth_all": data["metrics"]["mouth_all"],
                "sum_all": data["metrics"]["sum_all"],
            }
            for name, data in results.items()
        },
    }
    (outdir / "offset_line_observer_phase_split_audit_summary.json").write_text(json.dumps(summary_out, indent=2), encoding="utf-8")

    def spl_res(sim, ref):
        return _spl_db(sim) - _spl_db(ref)
    def ph_res(sim, ref):
        return _phase_wrap_deg(_phase_deg(sim) - _phase_deg(ref))

    # plots focus on representative scenarios
    use = ["raw", "two_band", "global_both", "differential_mouth", "global_plus_differential"]
    _plot(freqs, {n: spl_res(results[n]["front"], ref_front) for n in use}, "Residual (dB)", "Offset-line front SPL residual vs observer-phase split", outdir / "offset_line_observer_phase_split_front_spl_residual.png")
    _plot(freqs, {n: ph_res(results[n]["front"], ref_front) for n in use}, "Residual (deg)", "Offset-line front phase residual vs observer-phase split", outdir / "offset_line_observer_phase_split_front_phase_residual.png")
    _plot(freqs, {n: spl_res(results[n]["mouth"], ref_mouth) for n in use}, "Residual (dB)", "Offset-line mouth SPL residual vs observer-phase split", outdir / "offset_line_observer_phase_split_mouth_spl_residual.png")
    _plot(freqs, {n: ph_res(results[n]["mouth"], ref_mouth) for n in use}, "Residual (deg)", "Offset-line mouth phase residual vs observer-phase split", outdir / "offset_line_observer_phase_split_mouth_phase_residual.png")
    _plot(freqs, {n: spl_res(results[n]["sum"], ref_sum) for n in use}, "Residual (dB)", "Offset-line sum SPL residual vs observer-phase split", outdir / "offset_line_observer_phase_split_sum_spl_residual.png")
    _plot(freqs, {n: ph_res(results[n]["sum"], ref_sum) for n in use}, "Residual (deg)", "Offset-line sum phase residual vs observer-phase split", outdir / "offset_line_observer_phase_split_sum_phase_residual.png")

    print(json.dumps({
        "summary_json": str(outdir / "offset_line_observer_phase_split_audit_summary.json"),
        "ranked_scenarios": ranked,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
