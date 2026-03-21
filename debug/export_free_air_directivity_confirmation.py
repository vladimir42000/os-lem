from __future__ import annotations

import argparse
import csv
import json
import math
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


def _phase_wrap_deg(diff: np.ndarray) -> np.ndarray:
    return ((diff + 180.0) % 360.0) - 180.0


def _normalize_phase_reference(phase_deg: np.ndarray, freqs_hz: np.ndarray, distance_m: float, c0: float = 343.0) -> np.ndarray:
    k_d_deg = 360.0 * freqs_hz * distance_m / c0
    return _phase_wrap_deg(phase_deg + k_d_deg)


def _metrics(sim: np.ndarray, ref: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(sim) & np.isfinite(ref)
    if not np.any(mask):
        return {"count": 0, "mae": float("nan"), "rmse": float("nan"), "max_abs_error": float("nan")}
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
        return {"count": 0, "mae": float("nan"), "rmse": float("nan"), "max_abs_error": float("nan")}
    diff = _phase_wrap_deg(sim_deg[mask] - ref_deg[mask])
    return {
        "count": int(mask.sum()),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff * diff))),
        "max_abs_error": float(np.max(np.abs(diff))),
    }


def _residual_db(sim_db: np.ndarray, ref_db: np.ndarray) -> np.ndarray:
    return ref_db - sim_db


def _phase_residual_deg(sim_deg: np.ndarray, ref_deg: np.ndarray) -> np.ndarray:
    return _phase_wrap_deg(ref_deg - sim_deg)


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

    parser = argparse.ArgumentParser(
        description="Free-air front-radiator directivity confirmation audit in the debug layer only."
    )
    parser.add_argument("--model", default=str(repo_root / "examples" / "free_air" / "model.yaml"))
    parser.add_argument("--akabak-pressure", default=str(Path("/home/vdemian/dos/spkr/AFOTEX2.TXT")))
    parser.add_argument("--driver-radiator-id", default="rad_front")
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--phase-reference-distance-m", type=float, default=1.0)
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
    parser.add_argument(
        "--directivity-factor-mode",
        choices=["signed", "magnitude_only"],
        default="signed",
        help="signed keeps Bessel sign changes in complex pressure; magnitude_only removes phase flips.",
    )
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "free_air_directivity_confirmation_out"))
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ref = _load_txt_amp_phase(Path(args.akabak_pressure))
    freqs = ref["frequency_hz"]
    ref_spl = _safedb(ref["amp"])
    ref_phase = ref["phase_deg"]

    model, warnings = load_and_normalize(Path(args.model))
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)
    p_front_raw = radiator_observation_pressure(
        sweep,
        system,
        args.driver_radiator_id,
        1.0,
        radiation_space=args.radiation_space,
    )

    radiator_area = {r.id: float(r.area_m2) for r in model.radiators}
    front_area = radiator_area[args.driver_radiator_id]
    directivity = _onaxis_directivity_signed(freqs, front_area)
    if args.directivity_factor_mode == "magnitude_only":
        directivity = np.abs(directivity)

    toggles = {
        "none": False,
        "front_only": True,
    }

    ranked: list[dict[str, object]] = []
    csv_rows: list[dict[str, object]] = []
    spl_residual_plot: dict[str, np.ndarray] = {}
    phase_residual_plot: dict[str, np.ndarray] = {}
    hf_mask = freqs >= float(args.hf_min_hz)

    for label, use_directivity in toggles.items():
        series = p_front_raw * (directivity if use_directivity else 1.0)
        sim_spl = _safedb(series)
        sim_phase = _normalize_phase_reference(
            np.angle(series, deg=True),
            freqs,
            args.phase_reference_distance_m,
        )

        spl_residual = _residual_db(sim_spl, ref_spl)
        phase_residual = _phase_residual_deg(sim_phase, ref_phase)
        spl_residual_plot[label] = spl_residual
        phase_residual_plot[label] = phase_residual

        row = {
            "toggle": label,
            "front_directivity_enabled": bool(use_directivity),
            "hf_spl_mae_db": _metrics(sim_spl[hf_mask], ref_spl[hf_mask])["mae"],
            "hf_phase_mae_deg": _phase_metrics(sim_phase[hf_mask], ref_phase[hf_mask])["mae"],
            "all_spl_mae_db": _metrics(sim_spl, ref_spl)["mae"],
            "all_phase_mae_deg": _phase_metrics(sim_phase, ref_phase)["mae"],
        }
        ranked.append(row)
        csv_rows.append(row)

    ranked.sort(key=lambda row: float(row["hf_spl_mae_db"]))

    csv_path = outdir / "free_air_directivity_confirmation_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    summary = {
        "model": str(args.model),
        "akabak_pressure": str(args.akabak_pressure),
        "warnings": list(warnings or []),
        "radiation_space": args.radiation_space,
        "phase_reference_distance_m": float(args.phase_reference_distance_m),
        "hf_min_hz": float(args.hf_min_hz),
        "directivity_factor_mode": args.directivity_factor_mode,
        "driver_radiator": {
            "id": args.driver_radiator_id,
            "area_m2": front_area,
            "f_ka1_hz_from_area": _f_ka1(front_area),
        },
        "best_toggle_by_hf_spl_mae": ranked[0]["toggle"],
        "ranked_toggles": ranked,
        "pm_interpretation": {
            "purpose": "confirm whether front-radiator directivity helps free-air too, before any kernel patch",
            "decision_rule": {
                "front_only_improves_hf_spl_materially": "front-radiator directivity becomes a stronger general solver candidate",
                "front_only_hurts_or_does_not_help": "keep directivity in debug only and do not move it into the kernel yet",
                "phase_improves_or_stays_comparable": "solver-candidate confidence increases",
                "phase_degrades_strongly": "treat the result as comparison-layer evidence only, not kernel-ready",
            },
        },
    }
    summary["spl_residual_png"] = _maybe_plot(
        outdir / "free_air_directivity_spl_residual.png",
        freqs,
        spl_residual_plot,
        "Free-air front-radiator SPL residual vs directivity toggle",
        "Residual (dB)",
    )
    summary["phase_residual_png"] = _maybe_plot(
        outdir / "free_air_directivity_phase_residual.png",
        freqs,
        phase_residual_plot,
        "Free-air front-radiator phase residual vs directivity toggle",
        "Residual (deg)",
    )

    json_path = outdir / "free_air_directivity_confirmation_summary.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"summary_json": str(json_path), "ranked_toggles": ranked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
