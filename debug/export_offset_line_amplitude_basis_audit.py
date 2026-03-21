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


def _fit_real_amplitude_mix(src_front: np.ndarray, src_mouth: np.ndarray, ref_front: np.ndarray, ref_mouth: np.ndarray) -> np.ndarray:
    X = np.column_stack([np.abs(src_front), np.abs(src_mouth)])
    y_front = np.abs(ref_front)
    y_mouth = np.abs(ref_mouth)
    a_front, *_ = np.linalg.lstsq(X, y_front, rcond=None)
    a_mouth, *_ = np.linalg.lstsq(X, y_mouth, rcond=None)
    return np.vstack([a_front, a_mouth])


def _apply_real_amplitude_mix(src_front: np.ndarray, src_mouth: np.ndarray, A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    src_mag = np.vstack([np.abs(src_front), np.abs(src_mouth)])
    out_mag = A @ src_mag
    out_front_mag = np.maximum(out_mag[0], 1e-30)
    out_mouth_mag = np.maximum(out_mag[1], 1e-30)
    out_front = out_front_mag * np.exp(1j * np.angle(src_front))
    out_mouth = out_mouth_mag * np.exp(1j * np.angle(src_mouth))
    return out_front, out_mouth


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


def _residual_curves(sim: np.ndarray, ref: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    spl = _spl_db(sim) - _spl_db(ref)
    phase = _phase_wrap_deg(_phase_deg(sim) - _phase_deg(ref))
    return spl, phase


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

    parser = argparse.ArgumentParser(description="Audit whether amplitude-basis mixing can improve SPL while preserving raw phase.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--two-band-summary", default=str(repo_root / "debug" / "offset_line_two_band_basis_mixing_audit_out" / "offset_line_two_band_basis_mixing_summary.json"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_amplitude_basis_audit_out"))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
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

    two_band_path = Path(args.two_band_summary)
    if two_band_path.exists():
        two_band_summary = json.loads(two_band_path.read_text(encoding="utf-8"))
        mixed_front, mixed_mouth = _apply_two_band_mix(freqs, p_front, p_mouth, two_band_summary)
        two_band_note = "loaded"
    else:
        mixed_front, mixed_mouth = p_front.copy(), p_mouth.copy()
        two_band_note = f"missing summary at {two_band_path}"


    ref_front = -_complex_from_spl_phase(drv_frd["spl_db"], drv_frd["phase_deg"])
    ref_mouth = -_complex_from_spl_phase(port_frd["spl_db"], port_frd["phase_deg"])
    ref_sum = -_complex_from_spl_phase(sum_frd["spl_db"], sum_frd["phase_deg"])

    A = _fit_real_amplitude_mix(p_front, p_mouth, ref_front, ref_mouth)
    amp_front, amp_mouth = _apply_real_amplitude_mix(p_front, p_mouth, A)

    scenarios = {
        "raw": (p_front, p_mouth),
        "complex_two_band": (mixed_front, mixed_mouth),
        "real_amplitude_mix": (amp_front, amp_mouth),
    }

    ranked = []
    scenario_metrics: dict[str, dict[str, object]] = {}
    scenario_series: dict[str, dict[str, np.ndarray]] = {}
    for name, (front_sim, mouth_sim) in scenarios.items():
        sum_sim = front_sim + mouth_sim
        metrics = {
            "front_all": _metrics(freqs, front_sim, ref_front, args.hf_min_hz),
            "mouth_all": _metrics(freqs, mouth_sim, ref_mouth, args.hf_min_hz),
            "sum_all": _metrics(freqs, sum_sim, ref_sum, args.hf_min_hz),
        }
        scenario_metrics[name] = metrics
        scenario_series[name] = {"front": front_sim, "mouth": mouth_sim, "sum": sum_sim}
        ranked.append(
            {
                "scenario": name,
                "sum_hf_spl_mae_db": metrics["sum_all"]["hf_spl_mae_db"],
                "sum_hf_phase_mae_deg": metrics["sum_all"]["hf_phase_mae_deg"],
                "sum_hf_complex_rel_rmse": metrics["sum_all"]["hf_complex_rel_rmse"],
            }
        )

    ranked.sort(key=lambda r: (r["sum_hf_complex_rel_rmse"], r["sum_hf_phase_mae_deg"], r["sum_hf_spl_mae_db"]))

    front_spl_curves = {}
    front_phase_curves = {}
    mouth_spl_curves = {}
    mouth_phase_curves = {}
    sum_spl_curves = {}
    sum_phase_curves = {}
    for name, series in scenario_series.items():
        fs, fp = _residual_curves(series["front"], ref_front)
        ms, mp = _residual_curves(series["mouth"], ref_mouth)
        ss, sp = _residual_curves(series["sum"], ref_sum)
        front_spl_curves[name] = fs
        front_phase_curves[name] = fp
        mouth_spl_curves[name] = ms
        mouth_phase_curves[name] = mp
        sum_spl_curves[name] = ss
        sum_phase_curves[name] = sp

    _plot(freqs, front_spl_curves, "SPL residual (dB)", "Offset-line amplitude basis audit: front SPL residual", outdir / "offset_line_amplitude_basis_front_spl_residual.png")
    _plot(freqs, front_phase_curves, "Phase residual (deg)", "Offset-line amplitude basis audit: front phase residual", outdir / "offset_line_amplitude_basis_front_phase_residual.png")
    _plot(freqs, mouth_spl_curves, "SPL residual (dB)", "Offset-line amplitude basis audit: mouth SPL residual", outdir / "offset_line_amplitude_basis_mouth_spl_residual.png")
    _plot(freqs, mouth_phase_curves, "Phase residual (deg)", "Offset-line amplitude basis audit: mouth phase residual", outdir / "offset_line_amplitude_basis_mouth_phase_residual.png")
    _plot(freqs, sum_spl_curves, "SPL residual (dB)", "Offset-line amplitude basis audit: sum SPL residual", outdir / "offset_line_amplitude_basis_sum_spl_residual.png")
    _plot(freqs, sum_phase_curves, "Phase residual (deg)", "Offset-line amplitude basis audit: sum phase residual", outdir / "offset_line_amplitude_basis_sum_phase_residual.png")

    summary = {
        "two_band_summary_status": two_band_note,
        "fit_matrix_real": {
            "front_from_front": float(A[0, 0]),
            "front_from_mouth": float(A[0, 1]),
            "mouth_from_front": float(A[1, 0]),
            "mouth_from_mouth": float(A[1, 1]),
        },
        "ranked_scenarios": ranked,
        "scenario_metrics": scenario_metrics,
        "pm_interpretation": {
            "purpose": "test whether component amplitude-basis mismatch explains SPL differences while preserving raw source phases",
            "decision_rules": {
                "real_amplitude_mix_best": "remaining mismatch is mostly amplitude-basis semantics; raw phase reference is already closer to the reference than complex basis mixing",
                "raw_best": "basis remapping is not helpful under a phase-preserving contract; focus on raw mouth observable semantics",
                "complex_two_band_best": "a full complex contribution basis mismatch still dominates over phase-preserving amplitude remapping",
            },
        },
    }
    summary_path = outdir / "offset_line_amplitude_basis_audit_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"summary_json": str(summary_path), "ranked_scenarios": ranked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
