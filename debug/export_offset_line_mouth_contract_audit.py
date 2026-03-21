from __future__ import annotations

import argparse
import json
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


def _fit_real_scalar(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    denom = float(np.vdot(x, x).real)
    if denom <= 0.0:
        return 1.0
    num = float(np.vdot(x, y).real)
    return num / denom


def _fit_real_two_band(freq: np.ndarray, x: np.ndarray, y: np.ndarray, candidates_hz: list[float], hf_min_hz: float) -> tuple[float, float, float]:
    best = None
    for crossover in candidates_hz:
        lo = freq < crossover
        hi = ~lo
        a_lo = _fit_real_scalar(x[lo], y[lo]) if np.any(lo) else 1.0
        a_hi = _fit_real_scalar(x[hi], y[hi]) if np.any(hi) else a_lo
        pred = x.copy()
        if np.any(lo):
            pred[lo] = a_lo * x[lo]
        if np.any(hi):
            pred[hi] = a_hi * x[hi]
        m = _metrics(freq, pred, y, hf_min_hz)
        score = (m["hf_complex_rel_rmse"], m["hf_spl_mae_db"])
        if best is None or score < best[0]:
            best = (score, crossover, a_lo, a_hi)
    assert best is not None
    return float(best[1]), float(best[2]), float(best[3])


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

    parser = argparse.ArgumentParser(description="Audit mouth-path amplitude semantics while preserving raw phase.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--two-band-summary", default=str(repo_root / "debug" / "offset_line_two_band_basis_mixing_audit_out" / "offset_line_two_band_basis_mixing_summary.json"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_mouth_contract_audit_out"))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
    parser.add_argument("--candidates-hz", default="75,100,150,200,300,500,800,1000,1500,2000")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    sum_frd = _load_frd(Path(args.sum_frd))
    drv_frd = _load_frd(Path(args.drv_frd))
    port_frd = _load_frd(Path(args.port_frd))
    freqs = sum_frd["frequency_hz"]

    model, _warnings = load_and_normalize(Path(args.model))
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)
    p_front = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space=args.radiation_space)
    p_mouth = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space=args.radiation_space)

    summary_two = json.loads(Path(args.two_band_summary).read_text(encoding="utf-8"))
    front_two, mouth_two = _apply_two_band_mix(freqs, p_front, p_mouth, summary_two)

    ref_front = -_complex_from_spl_phase(drv_frd["spl_db"], drv_frd["phase_deg"])
    ref_mouth = -_complex_from_spl_phase(port_frd["spl_db"], port_frd["phase_deg"])
    ref_sum = -_complex_from_spl_phase(sum_frd["spl_db"], sum_frd["phase_deg"])

    cand = [float(x.strip()) for x in args.candidates_hz.split(",") if x.strip()]
    best_cross, a_lo, a_hi = _fit_real_two_band(freqs, p_mouth, ref_mouth, cand, args.hf_min_hz)
    mouth_real = p_mouth.copy()
    lo = freqs < best_cross
    hi = ~lo
    if np.any(lo):
        mouth_real[lo] = a_lo * p_mouth[lo]
    if np.any(hi):
        mouth_real[hi] = a_hi * p_mouth[hi]
    front_real = p_front.copy()

    scenarios = {
        "raw": (p_front, p_mouth),
        "complex_two_band": (front_two, mouth_two),
        "real_amplitude_mix": (front_real, mouth_real),
    }

    ranked = []
    scenario_metrics: dict[str, dict[str, object]] = {}
    for name, (front_sim, mouth_sim) in scenarios.items():
        sum_sim = front_sim + mouth_sim
        metric = {
            "front_all": _metrics(freqs, front_sim, ref_front, args.hf_min_hz),
            "mouth_all": _metrics(freqs, mouth_sim, ref_mouth, args.hf_min_hz),
            "sum_all": _metrics(freqs, sum_sim, ref_sum, args.hf_min_hz),
        }
        scenario_metrics[name] = metric
        ranked.append({
            "scenario": name,
            "sum_hf_spl_mae_db": metric["sum_all"]["hf_spl_mae_db"],
            "sum_hf_phase_mae_deg": metric["sum_all"]["hf_phase_mae_deg"],
            "sum_hf_complex_rel_rmse": metric["sum_all"]["hf_complex_rel_rmse"],
        })
    ranked.sort(key=lambda r: (r["sum_hf_complex_rel_rmse"], r["sum_hf_phase_mae_deg"]))

    summary = {
        "two_band_summary_status": "loaded",
        "best_mouth_amplitude_crossover_hz": best_cross,
        "mouth_real_low_scalar": a_lo,
        "mouth_real_high_scalar": a_hi,
        "ranked_scenarios": ranked,
        "scenario_metrics": scenario_metrics,
        "pm_interpretation": {
            "purpose": "test whether mouth-path amplitude semantics explain the remaining mismatch while preserving raw phase",
            "decision_rules": {
                "real_amplitude_mix_best": "remaining mismatch is mainly mouth amplitude/observable semantics; raw phase is already closer than complex basis mixing",
                "raw_best": "no helpful mouth-only amplitude contract was found; focus on mouth observable definition, not scalar amplitude remapping",
                "complex_two_band_best": "a full complex contribution-basis mismatch still dominates",
            },
        },
    }
    (outdir / "offset_line_mouth_contract_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    for path_name, ref in (("front", ref_front), ("mouth", ref_mouth), ("sum", ref_sum)):
        spl_curves = {}
        phase_curves = {}
        for name, (front_sim, mouth_sim) in scenarios.items():
            sig = front_sim if path_name == "front" else mouth_sim if path_name == "mouth" else (front_sim + mouth_sim)
            spl_curves[name] = _spl_db(sig) - _spl_db(ref)
            phase_curves[name] = _phase_wrap_deg(_phase_deg(sig) - _phase_deg(ref))
        _plot(freqs, spl_curves, "SPL residual (dB)", f"Offset-line mouth-contract audit: {path_name} SPL residual", outdir / f"offset_line_mouth_contract_{path_name}_spl_residual.png")
        _plot(freqs, phase_curves, "Phase residual (deg)", f"Offset-line mouth-contract audit: {path_name} phase residual", outdir / f"offset_line_mouth_contract_{path_name}_phase_residual.png")

    print(json.dumps({"summary_json": str(outdir / "offset_line_mouth_contract_audit_summary.json"), "ranked_scenarios": ranked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
