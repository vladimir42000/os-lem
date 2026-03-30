from __future__ import annotations

from pathlib import Path

from os_lem.reference_front_chamber_throat_side import write_front_chamber_throat_side_compare_outputs

if __name__ == "__main__":
    reference_dir = Path("tests/reference_data/akabak_rear_chamber_tapped")
    outdir = Path("debug/front_chamber_throat_side_compare_out")
    comparison = write_front_chamber_throat_side_compare_outputs(reference_dir, outdir)
    print(f"wrote {outdir}")
    for key, value in comparison.metrics.items():
        print(f"{key}: {value}")
