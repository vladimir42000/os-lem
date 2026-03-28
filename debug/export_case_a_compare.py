#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from os_lem.reference_case_a import write_case_a_compare_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Export os-lem vs Akabak Case A smoke comparison outputs")
    parser.add_argument("--reference-dir", type=Path, default=Path("tests/reference_data/akabak_case_a"))
    parser.add_argument("--outdir", type=Path, default=Path("debug/case_a_compare_out"))
    parser.add_argument("--exit-segments", type=int, default=1)
    args = parser.parse_args()

    comparison = write_case_a_compare_outputs(
        args.reference_dir,
        args.outdir,
        exit_segments=args.exit_segments,
    )
    print(f"wrote {args.outdir / 'case_a_compare.csv'}")
    print(f"wrote {args.outdir / 'summary.json'}")
    print(f"zmag_high_band_corr={comparison.metrics['zmag_high_band_corr']:.6f}")
    print(f"pressure_db_low_band_corr={comparison.metrics['pressure_db_low_band_corr']:.6f}")
    print(f"pressure_phase_low_band_corr={comparison.metrics['pressure_phase_low_band_corr']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
