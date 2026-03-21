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
    front_from: str
    mouth_from: str
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
        return {"count": 0, "mae": float("nan"), "rmse": float("nan"), "max_abs_error": float("nan")}
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
        return {"count": 0, "mae": float("nan"), "rmse": float("nan"), "max_abs_error": float("nan")}
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


def _fit_complex_matrix(os_front: np.ndarray, os_mouth: np.ndarray, hr_front: np.ndarray, hr_mouth: np.ndarray, mask: np.ndarray) -> np.ndarray:
    sel = mask & np.isfinite(os_front) & np.isfinite(os_mouth) & np.isfinite(hr_front) & np.isfinite(hr_mouth)
    if not np.any(sel):
        raise ValueError("No valid samples available for complex matrix fit")
    x = np.column_stack([os_front[sel], os_mouth[sel]])
    y = np.column_stack([hr_front[sel], hr_mouth[sel]])
    coeffs, *_ = np.linalg.lstsq(x, y, rcond=None)
    # coeffs shape (2 input basis, 2 outputs); convert to rows=outputs, cols=inputs
    return coeffs.T


def _apply_complex_matrix(matrix: np.ndarray, os_front: np.ndarray, os_mouth: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.vstack([os_front, os_mouth])
    y = matrix @ x
    return y[0, :], y[1, :]


def _matrix_summary(matrix: np.ndarray) -> dict[str, object]:
    entries = {}
    for r, row_name in enumerate(["front", "mouth"]):
        for c, col_name in enumerate(["front", "mouth"]):
            z = matrix[r, c]
            entries[f"{row_name}_from_{col_name}"] = {
                "real": float(np.real(z)),
                "imag": float(np.imag(z)),
                "magnitude": float(np.abs(z)),
                "magnitude_db": float(20.0 * np.log10(max(abs(z), 1.0e-30))),
                "phase_deg": float(np.angle(z, deg=True)),
            }
    s = np.linalg.svd(matrix, compute_uv=False)
    return {
        "entries": entries,
        "singular_values": [float(v) for v in s],
        "condition_number": float(s[0] / s[-1]) if s[-1] > 0.0 else float("inf"),
    }


def _band_masks(freqs: np.ndarray, hf_min_hz: float) -> dict[str, np.ndarray]:
    return {"all": np.isfinite(freqs), "hf": freqs >= hf_min_hz}


def _path_row(label: str, band: str, raw: np.ndarray, fit: np.ndarray, ref: np.ndarray) -> dict[str, object]:
    return {
        "path": label,
        "band": band,
        "raw_spl_mae_db": _metrics(_spl_db(raw), _spl_db(ref))["mae"],
        "raw_phase_mae_deg": _phase_metrics(_phase_deg(raw), _phase_deg(ref))["mae"],
        "raw_complex_rel_rmse": _complex_rel_rmse(raw, ref),
        "fit_spl_mae_db": _metrics(_spl_db(fit), _spl_db(ref))["mae"],
        "fit_phase_mae_deg": _phase_metrics(_phase_deg(fit), _phase_deg(ref))["mae"],
        "fit_complex_rel_rmse": _complex_rel_rmse(fit, ref),
    }


def _plot_residual(path: Path, freqs: np.ndarray, raw_residual: np.ndarray, fit_residual: np.ndarray, ylabel: str, title: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.semilogx(freqs, raw_residual, label="raw")
    plt.semilogx(freqs, fit_residual, label="after best 2x2 complex mix")
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

    parser = argparse.ArgumentParser(description="Audit whether Hornresp and os-lem contribution outputs differ mainly by a constant 2x2 basis mix.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--port-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_basis_mixing_audit_out"))
    parser.add_argument("--convention", default="direct_both_flip", choices=sorted(_conventions().keys()))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--phase-reference-distance-m", type=float, default=1.0)
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
    parser.add_argument("--fit-band", default="all", choices=["all", "hf"])
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

    os_front = _normalize_series_phase_reference(p_front, freqs, args.phase_reference_distance_m)
    os_mouth = _normalize_series_phase_reference(p_mouth, freqs, args.phase_reference_distance_m)
    os_sum = os_front + os_mouth

    convention = _conventions()[args.convention]
    hr_front, hr_mouth, hr_sum = _apply_convention(convention, drv_frd["complex_pa"], port_frd["complex_pa"])

    masks = _band_masks(freqs, args.hf_min_hz)
    fit_mask = masks[args.fit_band]
    matrix = _fit_complex_matrix(os_front, os_mouth, hr_front, hr_mouth, fit_mask)
    fit_front, fit_mouth = _apply_complex_matrix(matrix, os_front, os_mouth)
    fit_sum = fit_front + fit_mouth

    rows: list[dict[str, object]] = []
    for band_name, mask in masks.items():
        rows.append(_path_row("front", band_name, os_front[mask], fit_front[mask], hr_front[mask]))
        rows.append(_path_row("mouth", band_name, os_mouth[mask], fit_mouth[mask], hr_mouth[mask]))
        rows.append(_path_row("sum", band_name, os_sum[mask], fit_sum[mask], hr_sum[mask]))

    by_path_band = {(row["path"], row["band"]): row for row in rows}

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
        "fit_band": args.fit_band,
        "comparison_convention": {
            "name": convention.name,
            "front_from": convention.front_from,
            "mouth_from": convention.mouth_from,
            "front_sign": convention.front_sign,
            "mouth_sign": convention.mouth_sign,
        },
        "best_constant_basis_mix": _matrix_summary(matrix),
        "basis_mix_alignment": {
            "front_all": by_path_band[("front", "all")],
            "front_hf": by_path_band[("front", "hf")],
            "mouth_all": by_path_band[("mouth", "all")],
            "mouth_hf": by_path_band[("mouth", "hf")],
            "sum_all": by_path_band[("sum", "all")],
            "sum_hf": by_path_band[("sum", "hf")],
        },
        "pm_interpretation": {
            "purpose": "test whether Hornresp and os-lem decompose the same total field in different constant contribution bases",
            "decision_rules": {
                "strong_improvement": "if a constant 2x2 complex mix strongly reduces front/mouth/sum error, basis mismatch is a serious explanation",
                "weak_improvement": "if even best constant 2x2 mix leaves large error, mismatch is not just a constant basis transform",
                "sum_only_improves": "if sum improves but component paths remain poor, total agreement may hide component semantic mismatch",
                "cross_terms_large": "large off-diagonal coefficients suggest Hornresp and os-lem contributions are not directly aligned path-by-path",
            },
        },
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    summary_json = outdir / "offset_line_basis_mixing_summary.json"
    csv_path = outdir / "offset_line_basis_mixing_metrics.csv"
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fieldnames = [
        "path",
        "band",
        "raw_spl_mae_db",
        "raw_phase_mae_deg",
        "raw_complex_rel_rmse",
        "fit_spl_mae_db",
        "fit_phase_mae_deg",
        "fit_complex_rel_rmse",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

    _plot_residual(
        outdir / "offset_line_basis_mixing_front_spl_residual.png",
        freqs,
        _spl_db(os_front) - _spl_db(hr_front),
        _spl_db(fit_front) - _spl_db(hr_front),
        "Residual (dB)",
        "Offset-line front SPL residual vs basis mix",
    )
    _plot_residual(
        outdir / "offset_line_basis_mixing_front_phase_residual.png",
        freqs,
        _phase_wrap_deg(_phase_deg(os_front) - _phase_deg(hr_front)),
        _phase_wrap_deg(_phase_deg(fit_front) - _phase_deg(hr_front)),
        "Residual (deg)",
        "Offset-line front phase residual vs basis mix",
    )
    _plot_residual(
        outdir / "offset_line_basis_mixing_mouth_spl_residual.png",
        freqs,
        _spl_db(os_mouth) - _spl_db(hr_mouth),
        _spl_db(fit_mouth) - _spl_db(hr_mouth),
        "Residual (dB)",
        "Offset-line mouth SPL residual vs basis mix",
    )
    _plot_residual(
        outdir / "offset_line_basis_mixing_mouth_phase_residual.png",
        freqs,
        _phase_wrap_deg(_phase_deg(os_mouth) - _phase_deg(hr_mouth)),
        _phase_wrap_deg(_phase_deg(fit_mouth) - _phase_deg(hr_mouth)),
        "Residual (deg)",
        "Offset-line mouth phase residual vs basis mix",
    )
    _plot_residual(
        outdir / "offset_line_basis_mixing_sum_spl_residual.png",
        freqs,
        _spl_db(os_sum) - _spl_db(hr_sum),
        _spl_db(fit_sum) - _spl_db(hr_sum),
        "Residual (dB)",
        "Offset-line sum SPL residual vs basis mix",
    )
    _plot_residual(
        outdir / "offset_line_basis_mixing_sum_phase_residual.png",
        freqs,
        _phase_wrap_deg(_phase_deg(os_sum) - _phase_deg(hr_sum)),
        _phase_wrap_deg(_phase_deg(fit_sum) - _phase_deg(hr_sum)),
        "Residual (deg)",
        "Offset-line sum phase residual vs basis mix",
    )

    payload = {
        "summary_json": str(summary_json),
        "fit_band": args.fit_band,
        "front_hf_raw_spl_mae_db": by_path_band[("front", "hf")]["raw_spl_mae_db"],
        "front_hf_fit_spl_mae_db": by_path_band[("front", "hf")]["fit_spl_mae_db"],
        "mouth_hf_raw_spl_mae_db": by_path_band[("mouth", "hf")]["raw_spl_mae_db"],
        "mouth_hf_fit_spl_mae_db": by_path_band[("mouth", "hf")]["fit_spl_mae_db"],
        "sum_hf_raw_spl_mae_db": by_path_band[("sum", "hf")]["raw_spl_mae_db"],
        "sum_hf_fit_spl_mae_db": by_path_band[("sum", "hf")]["fit_spl_mae_db"],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
