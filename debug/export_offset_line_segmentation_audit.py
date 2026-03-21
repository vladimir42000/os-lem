from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import yaml


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


def _normalize_phase_reference(phase_deg: np.ndarray, freqs_hz: np.ndarray, distance_m: float) -> np.ndarray:
    k_d_deg = 360.0 * freqs_hz * distance_m / 343.0
    return _phase_wrap_deg(phase_deg + k_d_deg)


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
    diff = _phase_diff_deg(sim_deg[mask], ref_deg[mask])
    return {
        "count": int(mask.sum()),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff * diff))),
        "max_abs_error": float(np.max(np.abs(diff))),
    }


def _subset(freqs_hz: np.ndarray, fmin_hz: float | None, fmax_hz: float | None) -> np.ndarray:
    mask = np.ones_like(freqs_hz, dtype=bool)
    if fmin_hz is not None:
        mask &= freqs_hz >= fmin_hz
    if fmax_hz is not None:
        mask &= freqs_hz <= fmax_hz
    return mask


def _find_waveguide_elements(model_dict: dict[str, Any]) -> list[dict[str, Any]]:
    elements = model_dict.get("elements")
    if not isinstance(elements, list):
        raise ValueError("model must contain an elements list")
    waveguides = [e for e in elements if isinstance(e, dict) and e.get("type") == "waveguide_1d"]
    if not waveguides:
        raise ValueError("model does not contain any waveguide_1d elements")
    return waveguides


def _scaled_segment_variants(model_dict: dict[str, Any], scales: list[float]) -> list[dict[str, Any]]:
    base_waveguides = _find_waveguide_elements(model_dict)
    variants: list[dict[str, Any]] = []
    for scale in scales:
        if scale <= 0.0:
            raise ValueError("segment scales must be > 0")
        current = deepcopy(model_dict)
        segments_by_waveguide: dict[str, int] = {}
        for element in _find_waveguide_elements(current):
            base = next(wg for wg in base_waveguides if wg.get("id") == element.get("id"))
            base_segments = int(base.get("segments", 8))
            scaled = max(1, int(round(base_segments * scale)))
            element["segments"] = scaled
            segments_by_waveguide[str(element["id"])] = scaled
        label = "_".join(f"{wg_id}{segments:02d}" for wg_id, segments in segments_by_waveguide.items())
        variants.append(
            {
                "scale": float(scale),
                "label": label,
                "segments_by_waveguide": segments_by_waveguide,
                "model_dict": current,
            }
        )
    return variants


def _source_series(name: str, front: np.ndarray, mouth: np.ndarray) -> np.ndarray:
    if name == "front":
        return front
    if name == "mouth":
        return mouth
    raise ValueError(name)


def _apply_hypothesis(name: str, p_front: np.ndarray, p_mouth: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    mapping = {
        "direct": {"drv_source": "front", "mouth_source": "mouth", "drv_sign": +1, "mouth_sign": +1},
        "direct_drv_flip": {"drv_source": "front", "mouth_source": "mouth", "drv_sign": -1, "mouth_sign": +1},
        "direct_mouth_flip": {"drv_source": "front", "mouth_source": "mouth", "drv_sign": +1, "mouth_sign": -1},
        "direct_both_flip": {"drv_source": "front", "mouth_source": "mouth", "drv_sign": -1, "mouth_sign": -1},
        "swapped": {"drv_source": "mouth", "mouth_source": "front", "drv_sign": +1, "mouth_sign": +1},
        "swapped_drv_flip": {"drv_source": "mouth", "mouth_source": "front", "drv_sign": -1, "mouth_sign": +1},
        "swapped_mouth_flip": {"drv_source": "mouth", "mouth_source": "front", "drv_sign": +1, "mouth_sign": -1},
        "swapped_both_flip": {"drv_source": "mouth", "mouth_source": "front", "drv_sign": -1, "mouth_sign": -1},
    }
    spec = mapping.get(name)
    if spec is None:
        raise ValueError(f"unsupported hypothesis {name!r}")
    p_driver = spec["drv_sign"] * _source_series(str(spec["drv_source"]), p_front, p_mouth)
    p_mouth_contrib = spec["mouth_sign"] * _source_series(str(spec["mouth_source"]), p_front, p_mouth)
    return p_driver, p_mouth_contrib, spec


def _find_radiator_ids(model: Any) -> tuple[str, str]:
    front_ids = [r.id for r in model.radiators if r.node == model.driver.node_front]
    if len(front_ids) != 1:
        raise ValueError(f"expected exactly one front radiator on node {model.driver.node_front!r}, got {front_ids!r}")
    front_id = front_ids[0]
    other_ids = [r.id for r in model.radiators if r.id != front_id]
    if len(other_ids) != 1:
        raise ValueError(f"expected exactly one non-front radiator, got {other_ids!r}")
    return front_id, other_ids[0]


def _plot_residuals(freqs_hz: np.ndarray, series: dict[str, np.ndarray], title: str, ylabel: str, path: Path) -> None:
    plt.figure(figsize=(11, 6))
    for label, values in series.items():
        plt.semilogx(freqs_hz, values, label=label)
    plt.title(title)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel(ylabel)
    plt.grid(True, which="both", alpha=0.35)
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

    from os_lem.api import run_simulation
    from os_lem.constants import P_REF
    from os_lem.parser import normalize_model
    from os_lem.solve import radiator_observation_pressure

    parser = argparse.ArgumentParser(description="Audit offset-line HF residual sensitivity to waveguide segmentation only.")
    parser.add_argument("--model", default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"))
    parser.add_argument("--sum-frd", default=str(repo_root / "debug" / "hornresp_offset_line_sum.frd"))
    parser.add_argument("--drv-frd", default=str(repo_root / "debug" / "hornresp_offset_line_drv.frd"))
    parser.add_argument("--mouth-frd", default=str(repo_root / "debug" / "hornresp_offset_line_port.frd"))
    parser.add_argument("--outdir", default=str(repo_root / "debug" / "offset_line_segmentation_audit_out"))
    parser.add_argument("--radiation-space", default="2pi")
    parser.add_argument("--phase-reference-distance-m", type=float, default=1.0)
    parser.add_argument("--hypothesis", default="direct_both_flip")
    parser.add_argument("--segment-scales", default="0.25,0.5,1,2,4")
    parser.add_argument("--hf-min-hz", type=float, default=1000.0)
    args = parser.parse_args()

    model_path = Path(args.model)
    model_dict = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    scales = [float(x.strip()) for x in str(args.segment_scales).split(",") if x.strip()]

    sum_frd = _load_frd(Path(args.sum_frd))
    drv_frd = _load_frd(Path(args.drv_frd))
    mouth_frd = _load_frd(Path(args.mouth_frd))
    freqs_hz = sum_frd["frequency_hz"]
    for name, frd in {"drv": drv_frd, "mouth": mouth_frd}.items():
        if frd["frequency_hz"].shape != freqs_hz.shape or not np.allclose(frd["frequency_hz"], freqs_hz, rtol=0, atol=1e-9):
            raise ValueError(f"{name} FRD frequency axis does not match sum FRD")

    hf_mask = _subset(freqs_hz, args.hf_min_hz, None)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows_csv = outdir / "offset_line_segmentation_audit.csv"
    summary_json = outdir / "offset_line_segmentation_audit_summary.json"

    driver_residuals: dict[str, np.ndarray] = {}
    mouth_residuals: dict[str, np.ndarray] = {}
    sum_residuals: dict[str, np.ndarray] = {}
    variants_summary: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []

    for variant in _scaled_segment_variants(model_dict, scales):
        result = run_simulation(variant["model_dict"], freqs_hz)
        front_id, mouth_id = _find_radiator_ids(result.model)
        p_front = radiator_observation_pressure(result.sweep, result.system, front_id, 1.0, radiation_space=args.radiation_space)
        p_mouth = radiator_observation_pressure(result.sweep, result.system, mouth_id, 1.0, radiation_space=args.radiation_space)
        p_total_raw = p_front + p_mouth

        p_driver_cmp, p_mouth_cmp, hyp_spec = _apply_hypothesis(args.hypothesis, p_front, p_mouth)
        p_sum_cmp = p_driver_cmp + p_mouth_cmp

        spl_driver_cmp = 20.0 * np.log10(np.maximum(np.abs(p_driver_cmp), 1e-30) / P_REF)
        spl_mouth_cmp = 20.0 * np.log10(np.maximum(np.abs(p_mouth_cmp), 1e-30) / P_REF)
        spl_sum_cmp = 20.0 * np.log10(np.maximum(np.abs(p_sum_cmp), 1e-30) / P_REF)

        phase_driver_cmp = _normalize_phase_reference(np.angle(p_driver_cmp, deg=True), freqs_hz, args.phase_reference_distance_m)
        phase_mouth_cmp = _normalize_phase_reference(np.angle(p_mouth_cmp, deg=True), freqs_hz, args.phase_reference_distance_m)
        phase_sum_cmp = _normalize_phase_reference(np.angle(p_sum_cmp, deg=True), freqs_hz, args.phase_reference_distance_m)

        raw_total_spl_from_pressure = 20.0 * np.log10(np.maximum(np.abs(p_total_raw), 1e-30) / P_REF)
        if "spl_total" not in result.series:
            raise ValueError("model must contain spl_total observation for reconstruction audit")
        spl_total_obs = np.asarray(result.series["spl_total"], dtype=float)
        identity_spl_delta_db = raw_total_spl_from_pressure - spl_total_obs

        driver_residual = drv_frd["spl_db"] - spl_driver_cmp
        mouth_residual = mouth_frd["spl_db"] - spl_mouth_cmp
        sum_residual = sum_frd["spl_db"] - spl_sum_cmp
        driver_phase_residual = _phase_diff_deg(drv_frd["phase_deg"], phase_driver_cmp)
        mouth_phase_residual = _phase_diff_deg(mouth_frd["phase_deg"], phase_mouth_cmp)
        sum_phase_residual = _phase_diff_deg(sum_frd["phase_deg"], phase_sum_cmp)

        driver_residuals[variant["label"]] = driver_residual
        mouth_residuals[variant["label"]] = mouth_residual
        sum_residuals[variant["label"]] = sum_residual
        variant_rows.append(
            {
                "label": variant["label"],
                "scale": float(variant["scale"]),
                "segments_by_waveguide": variant["segments_by_waveguide"],
                "driver_residual": driver_residual,
                "mouth_residual": mouth_residual,
                "sum_residual": sum_residual,
                "driver_phase_residual": driver_phase_residual,
                "mouth_phase_residual": mouth_phase_residual,
                "sum_phase_residual": sum_phase_residual,
            }
        )

        variants_summary.append(
            {
                "label": variant["label"],
                "scale": float(variant["scale"]),
                "segments_by_waveguide": variant["segments_by_waveguide"],
                "front_radiator_id": front_id,
                "mouth_radiator_id": mouth_id,
                "warnings": list(result.warnings),
                "hypothesis": {
                    "name": args.hypothesis,
                    **hyp_spec,
                },
                "identity_check": {
                    "spl_total_series_max_abs_delta_db": float(np.max(np.abs(identity_spl_delta_db))),
                    "spl_total_series_rmse_db": float(np.sqrt(np.mean(identity_spl_delta_db * identity_spl_delta_db))),
                },
                "driver_hf_spl_db": _metrics(spl_driver_cmp[hf_mask], drv_frd["spl_db"][hf_mask]),
                "mouth_hf_spl_db": _metrics(spl_mouth_cmp[hf_mask], mouth_frd["spl_db"][hf_mask]),
                "sum_hf_spl_db": _metrics(spl_sum_cmp[hf_mask], sum_frd["spl_db"][hf_mask]),
                "driver_hf_phase_norm_deg": _phase_metrics(phase_driver_cmp[hf_mask], drv_frd["phase_deg"][hf_mask]),
                "mouth_hf_phase_norm_deg": _phase_metrics(phase_mouth_cmp[hf_mask], mouth_frd["phase_deg"][hf_mask]),
                "sum_hf_phase_norm_deg": _phase_metrics(phase_sum_cmp[hf_mask], sum_frd["phase_deg"][hf_mask]),
                "sum_all_spl_db": _metrics(spl_sum_cmp, sum_frd["spl_db"]),
            }
        )

    fieldnames = [
        "variant",
        "scale",
        "segments_by_waveguide_json",
        "frequency_hz",
        "driver_spl_residual_db",
        "mouth_spl_residual_db",
        "sum_spl_residual_db",
        "driver_phase_norm_residual_deg",
        "mouth_phase_norm_residual_deg",
        "sum_phase_norm_residual_deg",
    ]
    with rows_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in variant_rows:
            label = row["label"]
            segments_json = json.dumps(row["segments_by_waveguide"], sort_keys=True)
            for i, f_hz in enumerate(freqs_hz):
                writer.writerow(
                    {
                        "variant": label,
                        "scale": float(row["scale"]),
                        "segments_by_waveguide_json": segments_json,
                        "frequency_hz": float(f_hz),
                        "driver_spl_residual_db": float(row["driver_residual"][i]),
                        "mouth_spl_residual_db": float(row["mouth_residual"][i]),
                        "sum_spl_residual_db": float(row["sum_residual"][i]),
                        "driver_phase_norm_residual_deg": float(row["driver_phase_residual"][i]),
                        "mouth_phase_norm_residual_deg": float(row["mouth_phase_residual"][i]),
                        "sum_phase_norm_residual_deg": float(row["sum_phase_residual"][i]),
                    }
                )

    variants_summary.sort(key=lambda row: (row["sum_hf_spl_db"]["mae"], row["sum_hf_phase_norm_deg"]["mae"]))

    driver_plot = outdir / "offset_line_segmentation_driver_hf_residual.png"
    mouth_plot = outdir / "offset_line_segmentation_mouth_hf_residual.png"
    sum_plot = outdir / "offset_line_segmentation_sum_hf_residual.png"
    _plot_residuals(freqs_hz[hf_mask], {k: v[hf_mask] for k, v in driver_residuals.items()}, "Offset-line driver HF residual vs segmentation", "Residual (dB)", driver_plot)
    _plot_residuals(freqs_hz[hf_mask], {k: v[hf_mask] for k, v in mouth_residuals.items()}, "Offset-line mouth HF residual vs segmentation", "Residual (dB)", mouth_plot)
    _plot_residuals(freqs_hz[hf_mask], {k: v[hf_mask] for k, v in sum_residuals.items()}, "Offset-line total HF residual vs segmentation", "Residual (dB)", sum_plot)

    summary = {
        "model": str(model_path),
        "sum_frd": str(args.sum_frd),
        "drv_frd": str(args.drv_frd),
        "mouth_frd": str(args.mouth_frd),
        "radiation_space": args.radiation_space,
        "phase_reference_distance_m": float(args.phase_reference_distance_m),
        "hypothesis": args.hypothesis,
        "hf_min_hz": float(args.hf_min_hz),
        "segment_scales": scales,
        "variants_ranked": variants_summary,
        "plots": {
            "driver": str(driver_plot),
            "mouth": str(mouth_plot),
            "sum": str(sum_plot),
        },
        "pm_interpretation": {
            "purpose": "test whether offset-line HF mismatch changes materially when only waveguide segmentation changes",
            "decision_rule": {
                "clear_refinement_trend": "HF mismatch likely contains a discretization-sensitive component; inspect waveguide assembly / phase accumulation before new observation physics",
                "little_or_no_refinement_trend": "HF mismatch is less likely to be caused mainly by segmentation density; inspect comparison semantics or observation physics next",
                "driver_stable_but_mouth_sum_move": "focus next on line-output / mouth composition rather than front radiator observation",
            },
        },
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps({
        "summary_json": str(summary_json),
        "ranked_variants": [
            {
                "label": row["label"],
                "segments_by_waveguide": row["segments_by_waveguide"],
                "sum_hf_spl_mae_db": row["sum_hf_spl_db"]["mae"],
                "mouth_hf_spl_mae_db": row["mouth_hf_spl_db"]["mae"],
                "driver_hf_spl_mae_db": row["driver_hf_spl_db"]["mae"],
                "sum_hf_phase_mae_deg": row["sum_hf_phase_norm_deg"]["mae"],
                "identity_max_abs_delta_db": row["identity_check"]["spl_total_series_max_abs_delta_db"],
            }
            for row in variants_summary
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
