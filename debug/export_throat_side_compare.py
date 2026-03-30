#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from os_lem.reference_throat_side import write_throat_side_compare_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Export os-lem vs Akabak throat-side smoke comparison outputs")
    parser.add_argument("--reference-dir", type=Path, default=Path("tests/reference_data/akabak_rear_chamber_tapped"))
    parser.add_argument("--outdir", type=Path, default=Path("debug/throat_side_compare_out"))
    args = parser.parse_args()

    comparison = write_throat_side_compare_outputs(args.reference_dir, args.outdir)
    print(f"wrote {args.outdir / 'throat_side_compare.csv'}")
    print(f"wrote {args.outdir / 'throat_side_observables.csv'}")
    print(f"wrote {args.outdir / 'summary.json'}")
    print(f"zmag_overall_corr={comparison.metrics['zmag_overall_corr']:.6f}")
    print(f"pressure_db_overall_corr={comparison.metrics['pressure_db_overall_corr']:.6f}")
    print(f"pressure_phase_overall_mae_deg={comparison.metrics['pressure_phase_overall_mae_deg']:.6f}")
    print("No frontend contract change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
