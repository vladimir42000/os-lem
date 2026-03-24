from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "debug" / "export_offset_line_compare_harness.py"


def test_offset_line_compare_harness_writes_summary_and_csv(tmp_path: Path) -> None:
    outdir = tmp_path / "compare_harness_out"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--outdir",
        str(outdir),
    ]
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)

    csv_path = outdir / "offset_line_compare_harness.csv"
    json_path = outdir / "offset_line_compare_harness_summary.json"
    assert csv_path.exists()
    assert json_path.exists()

    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["candidate_contract"] == "mouth_directivity_only"
    assert summary["points"] > 100
    assert summary["radiation_space"] == "2pi"
    assert summary["warnings"] == []

    for key in ["front_raw", "mouth_raw", "mouth_candidate", "sum_raw", "sum_candidate"]:
        assert key in summary["series"]
        assert summary["series"][key]["spl_db"]["count"] == summary["points"]
        assert summary["series"][key]["phase_deg"]["count"] == summary["points"]
