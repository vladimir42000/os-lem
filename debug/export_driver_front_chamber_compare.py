from __future__ import annotations

from pathlib import Path

from os_lem.reference_driver_front_chamber import write_driver_front_chamber_compare_outputs

if __name__ == "__main__":
    reference_dir = Path("tests/reference_data/akabak_rear_chamber_tapped")
    outdir = Path("debug/driver_front_chamber_compare_out")
    comparison = write_driver_front_chamber_compare_outputs(reference_dir, outdir)
    print(f"wrote {outdir}")
    for key, value in comparison.metrics.items():
        print(f"{key}: {value}")
