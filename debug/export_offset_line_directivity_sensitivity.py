from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy.special import j1


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


def _safedb(amp: np.ndarray, pref: float = 20e-6) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(amp), 1e-30) / pref)


def _phase_wrap_deg(diff: np.ndarray) -> np.ndarray:
    return ((diff + 180.0) % 360.0) - 180.0


def _normalize_phase_reference(phase_deg: np.ndarray, freqs_hz: np.ndarray, distance_m: float) -> np.ndarray:
    k_d_deg = 360.0 * freqs_hz * distance_m / 343.0
    return _phase_wrap_deg(phase_deg + k_d_deg)


def _residual_db(sim_db: np.ndarray, ref_db: np.ndarray) -> np.ndarray:
    return ref_db - sim_db


def _phase_residual_deg(sim_deg: np.ndarray, ref_deg: np.ndarray) -> np.ndarray:
    return _phase_wrap_deg(ref_deg - sim_deg)


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


def _phase_metrics(sim_deg: np.ndarray, ref_deg: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(sim_deg) & np.isfinite(ref_deg)
    if not np.any(mask):
        return {"count": 0}
    diff = _phase_wrap_deg(sim_deg[mask] - ref_deg[mask])
    return {
        "count": int(mask.sum()),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff * diff))),
        "max_abs_error": float(np.max(np.abs(diff))),
    }


def _piston_radius_from_area(area_m2: float) -> float:
    return math.sqrt(area_m2 / math.pi)


def _f_ka1(area_m2: float, c0: float = 343.0) -> float:
    a = _piston_radius_from_area(area_m2)
    return c0 / (2.0 * math.pi * a)


def _onaxis_directivity_signed(freq_hz: np.ndarray, area_m2: float, c0: float = 343.0) -> np.ndarray:
    radius_m = _piston_radius_from_area(area_m2)
    ka = (2.0 * math.pi * freq_hz / c0) * radius_m
    out = np.ones_like(freq_hz, dtype=float)
    mask = np.abs(ka) > 1.0e-12
    out[mask] = 2.0 * j1(ka[mask]) / ka[mask]
    return out


def _polarity_signs(mode: str) -> tuple[int, int]:
    if mode == "none":
        return (+1, +1)
    if mode == "driver_flip":
        return (-1, +1)
    if mode == "mouth_flip":
        return (+1, -1)
    if mode == "both_flip":
        return (-1, -1)
    raise ValueError(mode)


def _maybe_plot(path: Path, freqs: np.ndarray, series_by_label: dict[str, np.ndarray], title: str, ylabel: str) -> str | None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig = plt.figure(figsize=(11, 5.5))
    ax = fig.add_subplot(111)
    for label, values in series_by_label.items():
        ax.semilogx(freqs, values, label=label)
    ax.set_title(title)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(ylabel)
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

    parser = argparse.ArgumentParser(description="Audit directivity sensitivity in offset-line comparison without changing solver physics.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--driver-radiator-id", default="front_rad")
    parser.add_argument("--mouth-radiator-id", default="mouth_rad")
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--phase-reference-distance-m", type=float, default=1.0)
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
    parser.add_argument(
        "--baseline-polarity",
        choices=["none", "driver_flip", "mouth_flip", "both_flip"],
        default="both_flip",
        help="Current best convention scan suggests both_flip.",
    )
    parser.add_argument(
        "--directivity-factor-mode",
        choices=["signed", "magnitude_only"],
        default="signed",
        help="signed keeps Bessel sign changes in complex pressure; magnitude_only removes phase flips.",
    )
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_directivity_sensitivity_out"))
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    drv_frd = _load_frd(Path(args.drv_frd))
    port_frd = _load_frd(Path(args.port_frd))
    sum_frd = _load_frd(Path(args.sum_frd))
    freqs = drv_frd["frequency_hz"]
    for name, frd in {"port": port_frd, "sum": sum_frd}.items():
        if frd["frequency_hz"].shape != freqs.shape or not np.allclose(frd["frequency_hz"], freqs, rtol=0, atol=1e-9):
            raise ValueError(f"{name} FRD frequency axis does not match drv FRD")

    model, warnings = load_and_normalize(Path(args.model))
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)

    p_front_raw = radiator_observation_pressure(sweep, system, args.driver_radiator_id, 1.0, radiation_space=args.radiation_space)
    p_mouth_raw = radiator_observation_pressure(sweep, system, args.mouth_radiator_id, 1.0, radiation_space=args.radiation_space)

    radiator_area = {r.id: float(r.area_m2) for r in model.radiators}
    front_area = radiator_area[args.driver_radiator_id]
    mouth_area = radiator_area[args.mouth_radiator_id]
    front_directivity = _onaxis_directivity_signed(freqs, front_area)
    mouth_directivity = _onaxis_directivity_signed(freqs, mouth_area)
    if args.directivity_factor_mode == "magnitude_only":
        front_directivity = np.abs(front_directivity)
        mouth_directivity = np.abs(mouth_directivity)

    front_sign, mouth_sign = _polarity_signs(args.baseline_polarity)
    p_front_base = front_sign * p_front_raw
    p_mouth_base = mouth_sign * p_mouth_raw

    toggles = {
        "none": (False, False),
        "front_only": (True, False),
        "mouth_only": (False, True),
        "both": (True, True),
    }

    ranked: list[dict[str, object]] = []
    csv_rows: list[dict[str, object]] = []

    drv_spl_res_plot: dict[str, np.ndarray] = {}
    mouth_spl_res_plot: dict[str, np.ndarray] = {}
    sum_spl_res_plot: dict[str, np.ndarray] = {}
    drv_phase_res_plot: dict[str, np.ndarray] = {}
    mouth_phase_res_plot: dict[str, np.ndarray] = {}
    sum_phase_res_plot: dict[str, np.ndarray] = {}

    hf_mask = freqs >= float(args.hf_min_hz)

    for label, (use_front_directivity, use_mouth_directivity) in toggles.items():
        drv_series = p_front_base * (front_directivity if use_front_directivity else 1.0)
        mouth_series = p_mouth_base * (mouth_directivity if use_mouth_directivity else 1.0)
        sum_series = drv_series + mouth_series

        drv_spl = _safedb(drv_series)
        mouth_spl = _safedb(mouth_series)
        sum_spl = _safedb(sum_series)

        drv_phase = _normalize_phase_reference(np.angle(drv_series, deg=True), freqs, args.phase_reference_distance_m)
        mouth_phase = _normalize_phase_reference(np.angle(mouth_series, deg=True), freqs, args.phase_reference_distance_m)
        sum_phase = _normalize_phase_reference(np.angle(sum_series, deg=True), freqs, args.phase_reference_distance_m)

        drv_spl_res = _residual_db(drv_spl, drv_frd["spl_db"])
        mouth_spl_res = _residual_db(mouth_spl, port_frd["spl_db"])
        sum_spl_res = _residual_db(sum_spl, sum_frd["spl_db"])

        drv_phase_res = _phase_residual_deg(drv_phase, drv_frd["phase_deg"])
        mouth_phase_res = _phase_residual_deg(mouth_phase, port_frd["phase_deg"])
        sum_phase_res = _phase_residual_deg(sum_phase, sum_frd["phase_deg"])

        drv_spl_res_plot[label] = drv_spl_res
        mouth_spl_res_plot[label] = mouth_spl_res
        sum_spl_res_plot[label] = sum_spl_res
        drv_phase_res_plot[label] = drv_phase_res
        mouth_phase_res_plot[label] = mouth_phase_res
        sum_phase_res_plot[label] = sum_phase_res

        row = {
            "toggle": label,
            "front_directivity_enabled": bool(use_front_directivity),
            "mouth_directivity_enabled": bool(use_mouth_directivity),
            "driver_hf_spl_mae_db": _metrics(drv_spl[hf_mask], drv_frd["spl_db"][hf_mask])["mae"],
            "mouth_hf_spl_mae_db": _metrics(mouth_spl[hf_mask], port_frd["spl_db"][hf_mask])["mae"],
            "sum_hf_spl_mae_db": _metrics(sum_spl[hf_mask], sum_frd["spl_db"][hf_mask])["mae"],
            "driver_hf_phase_mae_deg": _phase_metrics(drv_phase[hf_mask], drv_frd["phase_deg"][hf_mask])["mae"],
            "mouth_hf_phase_mae_deg": _phase_metrics(mouth_phase[hf_mask], port_frd["phase_deg"][hf_mask])["mae"],
            "sum_hf_phase_mae_deg": _phase_metrics(sum_phase[hf_mask], sum_frd["phase_deg"][hf_mask])["mae"],
            "driver_all_spl_mae_db": _metrics(drv_spl, drv_frd["spl_db"])["mae"],
            "mouth_all_spl_mae_db": _metrics(mouth_spl, port_frd["spl_db"])["mae"],
            "sum_all_spl_mae_db": _metrics(sum_spl, sum_frd["spl_db"])["mae"],
            "driver_all_phase_mae_deg": _phase_metrics(drv_phase, drv_frd["phase_deg"])["mae"],
            "mouth_all_phase_mae_deg": _phase_metrics(mouth_phase, port_frd["phase_deg"])["mae"],
            "sum_all_phase_mae_deg": _phase_metrics(sum_phase, sum_frd["phase_deg"])["mae"],
        }
        ranked.append(row)
        csv_rows.append(row)

    ranked.sort(key=lambda row: float(row["sum_hf_spl_mae_db"]))

    csv_path = outdir / "offset_line_directivity_sensitivity_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    summary = {
        "model": str(args.model),
        "drv_frd": str(args.drv_frd),
        "port_frd": str(args.port_frd),
        "sum_frd": str(args.sum_frd),
        "warnings": list(warnings or []),
        "radiation_space": args.radiation_space,
        "phase_reference_distance_m": float(args.phase_reference_distance_m),
        "hf_min_hz": float(args.hf_min_hz),
        "baseline_polarity": args.baseline_polarity,
        "directivity_factor_mode": args.directivity_factor_mode,
        "driver_radiator": {
            "id": args.driver_radiator_id,
            "area_m2": front_area,
            "f_ka1_hz_from_area": _f_ka1(front_area),
        },
        "mouth_radiator": {
            "id": args.mouth_radiator_id,
            "area_m2": mouth_area,
            "f_ka1_hz_from_area": _f_ka1(mouth_area),
        },
        "best_toggle_by_sum_hf_spl_mae": ranked[0]["toggle"],
        "ranked_toggles": ranked,
        "pm_interpretation": {
            "purpose": "test directivity as a debug-layer sensitivity only, before any solver or kernel change",
            "decision_rule": {
                "front_only_improves_driver_and_total": "front-radiator directivity becomes a serious candidate for a later solver patch",
                "both_improves_total_and_phase": "shared directivity could be a candidate, but only after reviewing mouth semantics carefully",
                "mouth_only_hurts_or_does_not_help": "do not assume mouth contribution should share the same directivity correction",
                "no_toggle_improves_total_materially": "do not move directivity into the kernel yet",
            },
        },
    }

    summary["driver_spl_residual_png"] = _maybe_plot(
        outdir / "offset_line_directivity_driver_spl_residual.png",
        freqs,
        drv_spl_res_plot,
        "Offset-line driver SPL residual vs directivity toggle",
        "Residual (dB)",
    )
    summary["mouth_spl_residual_png"] = _maybe_plot(
        outdir / "offset_line_directivity_mouth_spl_residual.png",
        freqs,
        mouth_spl_res_plot,
        "Offset-line mouth SPL residual vs directivity toggle",
        "Residual (dB)",
    )
    summary["sum_spl_residual_png"] = _maybe_plot(
        outdir / "offset_line_directivity_sum_spl_residual.png",
        freqs,
        sum_spl_res_plot,
        "Offset-line total SPL residual vs directivity toggle",
        "Residual (dB)",
    )
    summary["driver_phase_residual_png"] = _maybe_plot(
        outdir / "offset_line_directivity_driver_phase_residual.png",
        freqs,
        drv_phase_res_plot,
        "Offset-line driver phase residual vs directivity toggle",
        "Residual (deg)",
    )
    summary["mouth_phase_residual_png"] = _maybe_plot(
        outdir / "offset_line_directivity_mouth_phase_residual.png",
        freqs,
        mouth_phase_res_plot,
        "Offset-line mouth phase residual vs directivity toggle",
        "Residual (deg)",
    )
    summary["sum_phase_residual_png"] = _maybe_plot(
        outdir / "offset_line_directivity_sum_phase_residual.png",
        freqs,
        sum_phase_res_plot,
        "Offset-line total phase residual vs directivity toggle",
        "Residual (deg)",
    )

    json_path = outdir / "offset_line_directivity_sensitivity_summary.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps({"summary_json": str(json_path), "ranked_toggles": ranked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
