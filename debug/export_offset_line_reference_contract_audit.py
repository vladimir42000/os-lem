from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


C0 = 343.0
P_REF = 20.0e-6


@dataclass(frozen=True)
class Convention:
    name: str
    front_from: str  # drv or port
    mouth_from: str  # drv or port
    front_sign: int
    mouth_sign: int


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


def _phase_wrap_deg(diff: np.ndarray) -> np.ndarray:
    return ((diff + 180.0) % 360.0) - 180.0


def _phase_deg(series: np.ndarray) -> np.ndarray:
    return np.angle(series, deg=True)


def _spl_db(series: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(series), 1.0e-30) / P_REF)


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


def _complex_rel_rmse(sim: np.ndarray, ref: np.ndarray) -> float:
    mask = np.isfinite(sim) & np.isfinite(ref)
    if not np.any(mask):
        return float("nan")
    num = np.sqrt(np.mean(np.abs(sim[mask] - ref[mask]) ** 2))
    den = np.sqrt(np.mean(np.abs(ref[mask]) ** 2))
    if den <= 0.0:
        return float("nan")
    return float(num / den)


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

    freq = np.asarray(cols["Freq (hertz)"], dtype=float)
    spl_db = np.asarray(cols["SPL (dB)"], dtype=float)
    phase_deg = np.asarray(cols["WPhase (deg)"], dtype=float)
    _validate_frequency_axis(freq)
    mag_pa = P_REF * np.power(10.0, spl_db / 20.0)
    complex_pa = mag_pa * np.exp(1j * np.deg2rad(phase_deg))
    return {
        "frequency_hz": freq,
        "spl_db": spl_db,
        "phase_deg": phase_deg,
        "complex_pa": complex_pa,
    }


def _normalize_series_phase_reference(series: np.ndarray, freqs_hz: np.ndarray, distance_m: float) -> np.ndarray:
    kd = 2.0 * np.pi * freqs_hz * distance_m / C0
    return series * np.exp(1j * kd)


def _fit_complex_scalar(sim: np.ndarray, ref: np.ndarray, mask: np.ndarray) -> complex:
    sel = mask & np.isfinite(sim) & np.isfinite(ref)
    if not np.any(sel):
        return complex(float("nan"), float("nan"))
    x = sim[sel]
    y = ref[sel]
    denom = np.vdot(x, x)
    if abs(denom) <= 0.0:
        return complex(float("nan"), float("nan"))
    return np.vdot(x, y) / denom


def _scalar_summary(alpha: complex) -> dict[str, float]:
    return {
        "real": float(np.real(alpha)),
        "imag": float(np.imag(alpha)),
        "magnitude": float(np.abs(alpha)),
        "magnitude_db": float(20.0 * np.log10(max(abs(alpha), 1.0e-30))),
        "phase_deg": float(np.angle(alpha, deg=True)),
    }


def _conventions() -> dict[str, Convention]:
    items = [
        Convention("direct", "drv", "port", +1, +1),
        Convention("direct_drv_flip", "drv", "port", -1, +1),
        Convention("direct_port_flip", "drv", "port", +1, -1),
        Convention("direct_both_flip", "drv", "port", -1, -1),
        Convention("swapped", "port", "drv", +1, +1),
        Convention("swapped_drv_flip", "port", "drv", -1, +1),
        Convention("swapped_port_flip", "port", "drv", +1, -1),
        Convention("swapped_both_flip", "port", "drv", -1, -1),
    ]
    return {c.name: c for c in items}


def _apply_convention(convention: Convention, hr_drv: np.ndarray, hr_port: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    src = {"drv": hr_drv, "port": hr_port}
    front = convention.front_sign * src[convention.front_from]
    mouth = convention.mouth_sign * src[convention.mouth_from]
    return front, mouth, front + mouth


def _additivity_rows(hr_sum: np.ndarray, hr_drv: np.ndarray, hr_port: np.ndarray, freqs: np.ndarray, hf_min_hz: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    hf_mask = freqs >= hf_min_hz
    choices = [
        ("drv_plus_port", +1, +1),
        ("neg_drv_plus_port", -1, +1),
        ("drv_minus_port", +1, -1),
        ("neg_drv_minus_port", -1, -1),
    ]
    for name, s_drv, s_port in choices:
        recon = s_drv * hr_drv + s_port * hr_port
        row = {
            "contract": name,
            "drv_sign": s_drv,
            "port_sign": s_port,
            "all_spl_mae_db": _metrics(_spl_db(recon), _spl_db(hr_sum))["mae"],
            "all_phase_mae_deg": _phase_metrics(_phase_deg(recon), _phase_deg(hr_sum))["mae"],
            "all_complex_rel_rmse": _complex_rel_rmse(recon, hr_sum),
            "hf_spl_mae_db": _metrics(_spl_db(recon[hf_mask]), _spl_db(hr_sum[hf_mask]))["mae"],
            "hf_phase_mae_deg": _phase_metrics(_phase_deg(recon[hf_mask]), _phase_deg(hr_sum[hf_mask]))["mae"],
            "hf_complex_rel_rmse": _complex_rel_rmse(recon[hf_mask], hr_sum[hf_mask]),
        }
        rows.append(row)
    rows.sort(key=lambda r: (float(r["hf_complex_rel_rmse"]), float(r["hf_spl_mae_db"])))
    return rows


def _band_masks(freqs: np.ndarray, hf_min_hz: float) -> dict[str, np.ndarray]:
    return {
        "all": np.isfinite(freqs),
        "hf": freqs >= hf_min_hz,
    }


def _path_metrics(label: str, sim: np.ndarray, ref: np.ndarray, masks: dict[str, np.ndarray]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for band_name, mask in masks.items():
        alpha = _fit_complex_scalar(sim, ref, mask)
        fit = alpha * sim
        rows.append(
            {
                "path": label,
                "band": band_name,
                "raw_spl_mae_db": _metrics(_spl_db(sim[mask]), _spl_db(ref[mask]))["mae"],
                "raw_phase_mae_deg": _phase_metrics(_phase_deg(sim[mask]), _phase_deg(ref[mask]))["mae"],
                "raw_complex_rel_rmse": _complex_rel_rmse(sim[mask], ref[mask]),
                "fit_scalar": _scalar_summary(alpha),
                "fit_spl_mae_db": _metrics(_spl_db(fit[mask]), _spl_db(ref[mask]))["mae"],
                "fit_phase_mae_deg": _phase_metrics(_phase_deg(fit[mask]), _phase_deg(ref[mask]))["mae"],
                "fit_complex_rel_rmse": _complex_rel_rmse(fit[mask], ref[mask]),
            }
        )
    return rows


def _plot_residual(path: Path, freqs: np.ndarray, raw_residual: np.ndarray, fit_residual: np.ndarray, ylabel: str, title: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.semilogx(freqs, raw_residual, label="raw")
    plt.semilogx(freqs, fit_residual, label="after best complex scalar")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
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

    parser = argparse.ArgumentParser(description="Audit offset-line reference contract semantics against Hornresp contribution FRDs.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_reference_contract_audit_out"))
    parser.add_argument("--convention", default="direct_both_flip", choices=sorted(_conventions().keys()))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--phase-reference-distance-m", type=float, default=1.0)
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
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

    p_front = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space=args.radiation_space)
    p_mouth = radiator_observation_pressure(sweep, system, "mouth_rad", 1.0, radiation_space=args.radiation_space)
    p_sum = p_front + p_mouth

    os_front = _normalize_series_phase_reference(p_front, freqs, args.phase_reference_distance_m)
    os_mouth = _normalize_series_phase_reference(p_mouth, freqs, args.phase_reference_distance_m)
    os_sum = _normalize_series_phase_reference(p_sum, freqs, args.phase_reference_distance_m)

    hr_drv = drv_frd["complex_pa"]
    hr_port = port_frd["complex_pa"]
    hr_sum_raw = sum_frd["complex_pa"]

    additivity_rows = _additivity_rows(hr_sum_raw, hr_drv, hr_port, freqs, args.hf_min_hz)
    best_self_contract = additivity_rows[0]
    best_recon_hr = best_self_contract["drv_sign"] * hr_drv + best_self_contract["port_sign"] * hr_port

    convention = _conventions()[args.convention]
    hr_front, hr_mouth, hr_sum_conv = _apply_convention(convention, hr_drv, hr_port)
    masks = _band_masks(freqs, args.hf_min_hz)

    scalar_rows: list[dict[str, object]] = []
    scalar_rows.extend(_path_metrics("front", os_front, hr_front, masks))
    scalar_rows.extend(_path_metrics("mouth", os_mouth, hr_mouth, masks))
    scalar_rows.extend(_path_metrics("sum", os_sum, hr_sum_conv, masks))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    additivity_csv = outdir / "offset_line_reference_contract_additivity_ranked.csv"
    scalar_csv = outdir / "offset_line_reference_contract_scalar_fit.csv"
    summary_json = outdir / "offset_line_reference_contract_summary.json"

    with additivity_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(additivity_rows[0].keys()))
        writer.writeheader()
        for row in additivity_rows:
            writer.writerow(row)

    scalar_fieldnames = [
        "path",
        "band",
        "raw_spl_mae_db",
        "raw_phase_mae_deg",
        "raw_complex_rel_rmse",
        "fit_scalar_real",
        "fit_scalar_imag",
        "fit_scalar_magnitude",
        "fit_scalar_magnitude_db",
        "fit_scalar_phase_deg",
        "fit_spl_mae_db",
        "fit_phase_mae_deg",
        "fit_complex_rel_rmse",
    ]
    with scalar_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=scalar_fieldnames)
        writer.writeheader()
        for row in scalar_rows:
            fit = row["fit_scalar"]
            writer.writerow(
                {
                    "path": row["path"],
                    "band": row["band"],
                    "raw_spl_mae_db": row["raw_spl_mae_db"],
                    "raw_phase_mae_deg": row["raw_phase_mae_deg"],
                    "raw_complex_rel_rmse": row["raw_complex_rel_rmse"],
                    "fit_scalar_real": fit["real"],
                    "fit_scalar_imag": fit["imag"],
                    "fit_scalar_magnitude": fit["magnitude"],
                    "fit_scalar_magnitude_db": fit["magnitude_db"],
                    "fit_scalar_phase_deg": fit["phase_deg"],
                    "fit_spl_mae_db": row["fit_spl_mae_db"],
                    "fit_phase_mae_deg": row["fit_phase_mae_deg"],
                    "fit_complex_rel_rmse": row["fit_complex_rel_rmse"],
                }
            )

    by_path_band = {(row["path"], row["band"]): row for row in scalar_rows}
    summary = {
        "model": str(args.model),
        "sum_frd": str(args.sum_frd),
        "drv_frd": str(args.drv_frd),
        "port_frd": str(args.port_frd),
        "warnings": list(warnings or []),
        "points": int(freqs.size),
        "radiation_space": args.radiation_space,
        "phase_reference_distance_m": float(args.phase_reference_distance_m),
        "hf_min_hz": float(args.hf_min_hz),
        "comparison_convention": {
            "name": convention.name,
            "front_from": convention.front_from,
            "mouth_from": convention.mouth_from,
            "front_sign": convention.front_sign,
            "mouth_sign": convention.mouth_sign,
        },
        "hornresp_self_additivity_ranked": additivity_rows,
        "best_hornresp_self_contract": additivity_rows[0],
        "path_scalar_alignment": {
            "front_all": by_path_band[("front", "all")],
            "front_hf": by_path_band[("front", "hf")],
            "mouth_all": by_path_band[("mouth", "all")],
            "mouth_hf": by_path_band[("mouth", "hf")],
            "sum_all": by_path_band[("sum", "all")],
            "sum_hf": by_path_band[("sum", "hf")],
        },
        "pm_interpretation": {
            "purpose": "decide whether the remaining mismatch is better explained by reference-contract semantics than by solver breakage",
            "decision_rules": {
                "hornresp_self_additivity_good": "if Hornresp sum ~= driver+port under a simple sign contract, exported components behave like arithmetic components",
                "hornresp_self_additivity_poor": "if no simple sign contract reconstructs Hornresp sum well, exported contributions likely encode a semantic contract beyond raw arithmetic fields",
                "scalar_fit_large_improvement": "if a single complex scalar strongly improves a path, mismatch is closer to gain/phase reference offset than to shape disagreement",
                "scalar_fit_small_improvement": "if even best scalar fit leaves large error, path definitions are likely not the same observable",
            },
        },
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # plots
    best_name = str(best_self_contract["contract"])
    _plot_residual(
        outdir / "offset_line_reference_contract_hornresp_self_additivity_spl_residual.png",
        freqs,
        _spl_db(best_recon_hr) - _spl_db(hr_sum_raw),
        np.zeros_like(freqs),
        "Residual (dB)",
        f"Hornresp self-additivity SPL residual ({best_name})",
    )
    _plot_residual(
        outdir / "offset_line_reference_contract_hornresp_self_additivity_phase_residual.png",
        freqs,
        _phase_wrap_deg(_phase_deg(best_recon_hr) - _phase_deg(hr_sum_raw)),
        np.zeros_like(freqs),
        "Residual (deg)",
        f"Hornresp self-additivity phase residual ({best_name})",
    )

    plot_series = {
        "front": (os_front, hr_front),
        "mouth": (os_mouth, hr_mouth),
        "sum": (os_sum, hr_sum_conv),
    }
    for label, (sim, ref) in plot_series.items():
        alpha = by_path_band[(label, "all")]["fit_scalar"]
        fit = complex(alpha["real"], alpha["imag"]) * sim
        _plot_residual(
            outdir / f"offset_line_reference_contract_{label}_spl_residual.png",
            freqs,
            _spl_db(sim) - _spl_db(ref),
            _spl_db(fit) - _spl_db(ref),
            "Residual (dB)",
            f"Offset-line {label} SPL residual vs reference contract",
        )
        _plot_residual(
            outdir / f"offset_line_reference_contract_{label}_phase_residual.png",
            freqs,
            _phase_wrap_deg(_phase_deg(sim) - _phase_deg(ref)),
            _phase_wrap_deg(_phase_deg(fit) - _phase_deg(ref)),
            "Residual (deg)",
            f"Offset-line {label} phase residual vs reference contract",
        )

    payload = {
        "summary_json": str(summary_json),
        "best_hornresp_self_contract": additivity_rows[0],
        "sum_hf_raw_spl_mae_db": by_path_band[("sum", "hf")]["raw_spl_mae_db"],
        "sum_hf_fit_spl_mae_db": by_path_band[("sum", "hf")]["fit_spl_mae_db"],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
