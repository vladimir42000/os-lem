from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

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


def _normalize_hornresp_header(name: str) -> str:
    name = name.strip()
    mapping = {
        "Freq (hertz)": "frequency_hz",
        "Ze (ohms)": "zin_mag_ohm",
        "Xd (mm)": "x_mm",
        "SPL (dB)": "spl_total_db",
    }
    return mapping.get(name, name)


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

    from os_lem.api import run_simulation

    parser = argparse.ArgumentParser(description="Compare os-lem offset-line outputs against Hornresp reference data.")
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
        default=str(repo_root / "debug" / "offset_line_compare_out"),
        help="Output directory for comparison artifacts",
    )
    args = parser.parse_args()

    model_path = Path(args.model)
    reference_path = Path(args.reference)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    model_dict = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    ref = _load_reference(reference_path)
    freqs = ref["frequency_hz"]

    result = run_simulation(model_dict, freqs)

    comparisons: dict[str, dict[str, np.ndarray]] = {}

    if "zin_mag_ohm" in ref and result.zin_mag_ohm is not None:
        comparisons["zin_mag_ohm"] = {
            "sim": np.asarray(result.zin_mag_ohm, dtype=float),
            "ref": ref["zin_mag_ohm"],
        }

    if "x_mm" in ref and result.cone_excursion_mm is not None:
        x_rms = np.asarray(result.cone_excursion_mm, dtype=float)
        x_peak = x_rms * np.sqrt(2.0)
        comparisons["x_peak_mm"] = {
            "sim": x_peak,
            "ref": ref["x_mm"],
            "sim_rms": x_rms,
        }

    if "spl_total_db" in ref and "spl_total" in result.series:
        comparisons["spl_total_db"] = {
            "sim": np.asarray(result.series["spl_total"], dtype=float),
            "ref": ref["spl_total_db"],
        }

    if "spl_mouth_db" in ref and "spl_mouth" in result.series:
        comparisons["spl_mouth_db"] = {
            "sim": np.asarray(result.series["spl_mouth"], dtype=float),
            "ref": ref["spl_mouth_db"],
        }

    if not comparisons:
        raise ValueError(
            "Reference file does not contain any supported comparison columns.\n"
            "Supported optional columns are: zin_mag_ohm, x_mm, spl_total_db, spl_mouth_db"
        )

    comparison_csv = outdir / "offset_line_compare.csv"
    summary_json = outdir / "offset_line_summary.json"

    fieldnames = ["frequency_hz"]
    for name, payload in comparisons.items():
        if name == "x_peak_mm":
            fieldnames.extend(
                [
                    "oslem_x_rms_mm",
                    "oslem_x_peak_mm",
                    "hornresp_x_peak_mm",
                    "delta_x_peak_mm",
                ]
            )
        else:
            fieldnames.extend([f"oslem_{name}", f"hornresp_{name}", f"delta_{name}"])

    rows: list[dict[str, Any]] = []
    for i, f_hz in enumerate(freqs):
        row: dict[str, Any] = {"frequency_hz": float(f_hz)}
        for name, payload in comparisons.items():
            sim = payload["sim"]
            ref_col = payload["ref"]
            sim_v = float(sim[i]) if np.isfinite(sim[i]) else math.nan
            ref_v = float(ref_col[i]) if np.isfinite(ref_col[i]) else math.nan
            delta = sim_v - ref_v if math.isfinite(sim_v) and math.isfinite(ref_v) else math.nan

            if name == "x_peak_mm":
                x_rms = payload["sim_rms"]
                rms_v = float(x_rms[i]) if np.isfinite(x_rms[i]) else math.nan
                row["oslem_x_rms_mm"] = rms_v
                row["oslem_x_peak_mm"] = sim_v
                row["hornresp_x_peak_mm"] = ref_v
                row["delta_x_peak_mm"] = delta
            else:
                row[f"oslem_{name}"] = sim_v
                row[f"hornresp_{name}"] = ref_v
                row[f"delta_{name}"] = delta

        rows.append(row)

    with comparison_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary: dict[str, Any] = {
        "model": str(model_path),
        "reference": str(reference_path),
        "points": int(freqs.size),
        "comparisons": {},
        "warnings": list(result.warnings or []),
    }

    for name, payload in comparisons.items():
        summary["comparisons"][name] = _metrics(payload["sim"], payload["ref"])

    if "spl_total_db" in comparisons:
        bands = [(10.0, 200.0), (200.0, 1000.0), (1000.0, 5000.0), (5000.0, 20000.1)]
        summary["spl_total_db_bands"] = _band_metrics(
            freqs,
            comparisons["spl_total_db"]["sim"],
            comparisons["spl_total_db"]["ref"],
            bands,
        )

    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Comparison artifacts written:")
    print(f"  CSV:  {comparison_csv}")
    print(f"  JSON: {summary_json}")
    print("")
    print("Available comparison metrics:")
    for name, metrics in summary["comparisons"].items():
        print(f"  {name}: {metrics}")
    if "spl_total_db_bands" in summary:
        print("")
        print("Band-limited SPL metrics:")
        for band, metrics in summary["spl_total_db_bands"].items():
            print(f"  {band}: {metrics}")
    if summary["warnings"]:
        print("")
        print("os-lem warnings:")
        for warning in summary["warnings"]:
            print(f"  - {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
