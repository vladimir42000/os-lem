from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np


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


def _normalize_hornresp_header(name: str) -> str:
    name = name.strip()
    mapping = {
        "Freq (hertz)": "frequency_hz",
        "Ze (ohms)": "zin_mag_ohm",
        "Xd (mm)": "x_mm",
        "SPL (dB)": "spl_total_db",
    }
    return mapping.get(name, name)


def _load_reference_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"Reference file is empty: {path}")

    required = {"frequency_hz"}
    available = set(reader.fieldnames or [])
    if not required.issubset(available):
        raise ValueError(f"Reference CSV must contain at least: {sorted(required)}")

    out: dict[str, list[float]] = {name: [] for name in available}
    for row in rows:
        for name in available:
            raw = (row.get(name) or "").strip()
            if raw == "":
                out[name].append(float("nan"))
            else:
                out[name].append(float(raw))

    arrays = {name: np.asarray(values, dtype=float) for name, values in out.items()}
    _validate_frequency_axis(arrays["frequency_hz"])
    return arrays


def _load_reference_hornresp_txt(path: Path) -> dict[str, np.ndarray]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    header_idx = None
    header = None
    for i, line in enumerate(lines):
        if "Freq (hertz)" in line and "Ze (ohms)" in line:
            header_idx = i
            header = [c.strip() for c in re.split(r"\t+", line.strip()) if c.strip()]
            break

    if header_idx is None or header is None:
        raise ValueError(
            f"Could not find Hornresp result table header in {path}. "
            "Expected a line containing at least 'Freq (hertz)' and 'Ze (ohms)'."
        )

    norm_header = [_normalize_hornresp_header(h) for h in header]
    columns: dict[str, list[float]] = {h: [] for h in norm_header}

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
        for key, val in zip(norm_header, vals):
            columns[key].append(val)

    if not columns.get("frequency_hz"):
        raise ValueError(f"No numeric Hornresp rows found in {path}")

    arrays = {name: np.asarray(values, dtype=float) for name, values in columns.items()}
    _validate_frequency_axis(arrays["frequency_hz"])
    return arrays


def _load_reference(path: Path) -> dict[str, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(f"Reference file not found: {path}")
    if path.suffix.lower() == ".csv":
        return _load_reference_csv(path)
    if path.suffix.lower() == ".txt":
        return _load_reference_hornresp_txt(path)
    raise ValueError(f"Unsupported reference file type: {path.suffix}")


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


def _band_metrics(freq: np.ndarray, sim: np.ndarray, ref: np.ndarray, bands: list[tuple[float, float]]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for f_lo, f_hi in bands:
        mask = (freq >= f_lo) & (freq < f_hi) & np.isfinite(sim) & np.isfinite(ref)
        key = f"{f_lo:g}-{f_hi:g}_Hz"
        if not np.any(mask):
            out[key] = {"count": 0}
            continue
        diff = sim[mask] - ref[mask]
        out[key] = {
            "count": int(mask.sum()),
            "mae": float(np.mean(np.abs(diff))),
            "rmse": float(np.sqrt(np.mean(diff * diff))),
            "max_abs_error": float(np.max(np.abs(diff))),
        }
    return out


def main() -> int:
    here = Path(__file__).resolve()
    repo_candidates = _candidate_repo_roots(here.parent)
    if not repo_candidates:
        raise SystemExit("Could not locate repo root containing src/os_lem")
    repo_root = repo_candidates[0]

    if str(repo_root / "src") not in sys.path:
        sys.path.insert(0, str(repo_root / "src"))

    from os_lem.assemble import assemble_system
    from os_lem.constants import C0, P_REF
    from os_lem.parser import load_and_normalize
    from os_lem.solve import radiator_observation_pressure, solve_frequency_sweep

    parser = argparse.ArgumentParser(description="Isolate source-spacing SPL effects for the offset-line comparison.")
    parser.add_argument(
        "--model",
        default=str(repo_root / "examples" / "offset_line_minimal" / "model.yaml"),
        help="Path to os-lem model YAML",
    )
    parser.add_argument(
        "--reference",
        default=str(repo_root / "debug" / "hornresp_offset_line_reference.txt"),
        help="Path to Hornresp reference file (.txt table export or .csv)",
    )
    parser.add_argument(
        "--outdir",
        default=str(repo_root / "debug" / "offset_line_spacing_compare_out"),
        help="Output directory for comparison artifacts",
    )
    parser.add_argument(
        "--separation-m",
        type=float,
        default=1.15,
        help="Extra driver-to-mouth path-length separation to apply to the mouth source in meters.",
    )
    parser.add_argument(
        "--radiation-space",
        default="2pi",
        help="Observation radiation_space to use when evaluating complex radiator pressures.",
    )
    args = parser.parse_args()

    model_path = Path(args.model)
    reference_path = Path(args.reference)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ref = _load_reference(reference_path)
    freqs = ref["frequency_hz"]
    if "spl_total_db" not in ref:
        raise ValueError("Reference file does not contain Hornresp SPL data (SPL (dB)).")
    ref_spl = ref["spl_total_db"]

    model, warnings = load_and_normalize(model_path)
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)

    p_driver = radiator_observation_pressure(
        sweep, system, "front_rad", 1.0, radiation_space=args.radiation_space
    )
    p_mouth = radiator_observation_pressure(
        sweep, system, "mouth_rad", 1.0, radiation_space=args.radiation_space
    )

    omega = 2.0 * np.pi * freqs
    k = omega / C0
    phase_modifier = np.exp(-1j * k * float(args.separation_m))

    p_total_colocated = p_driver + p_mouth
    p_total_delayed = p_driver + p_mouth * phase_modifier

    spl_colocated_db = 20.0 * np.log10(np.maximum(np.abs(p_total_colocated), 1e-30) / P_REF)
    spl_delayed_db = 20.0 * np.log10(np.maximum(np.abs(p_total_delayed), 1e-30) / P_REF)

    bands = [(10.0, 200.0), (200.0, 1000.0), (1000.0, 5000.0), (5000.0, 20000.1)]
    comparison_csv = outdir / "offset_line_spacing_compare.csv"
    summary_json = outdir / "offset_line_spacing_summary.json"

    with comparison_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "frequency_hz",
                "hornresp_spl_total_db",
                "oslem_spl_total_colocated_db",
                "delta_colocated_db",
                "oslem_spl_total_delayed_db",
                "delta_delayed_db",
            ],
        )
        writer.writeheader()
        for i, f_hz in enumerate(freqs):
            writer.writerow(
                {
                    "frequency_hz": float(f_hz),
                    "hornresp_spl_total_db": float(ref_spl[i]),
                    "oslem_spl_total_colocated_db": float(spl_colocated_db[i]),
                    "delta_colocated_db": float(spl_colocated_db[i] - ref_spl[i]),
                    "oslem_spl_total_delayed_db": float(spl_delayed_db[i]),
                    "delta_delayed_db": float(spl_delayed_db[i] - ref_spl[i]),
                }
            )

    summary = {
        "model": str(model_path),
        "reference": str(reference_path),
        "points": int(freqs.size),
        "separation_m": float(args.separation_m),
        "radiation_space": args.radiation_space,
        "warnings": list(warnings or []),
        "spl_total_db_colocated": _metrics(spl_colocated_db, ref_spl),
        "spl_total_db_delayed": _metrics(spl_delayed_db, ref_spl),
        "spl_total_db_colocated_bands": _band_metrics(freqs, spl_colocated_db, ref_spl, bands),
        "spl_total_db_delayed_bands": _band_metrics(freqs, spl_delayed_db, ref_spl, bands),
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Spacing comparison artifacts written:")
    print(f"  CSV:  {comparison_csv}")
    print(f"  JSON: {summary_json}")
    print("")
    print("Overall SPL metrics:")
    print(f"  colocated: {summary['spl_total_db_colocated']}")
    print(f"  delayed:   {summary['spl_total_db_delayed']}")
    print("")
    print("Band-limited SPL metrics (colocated):")
    for band, metrics in summary["spl_total_db_colocated_bands"].items():
        print(f"  {band}: {metrics}")
    print("")
    print("Band-limited SPL metrics (delayed):")
    for band, metrics in summary["spl_total_db_delayed_bands"].items():
        print(f"  {band}: {metrics}")
    if warnings:
        print("")
        print("Model warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
