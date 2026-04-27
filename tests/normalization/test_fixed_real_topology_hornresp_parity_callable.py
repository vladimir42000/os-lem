from __future__ import annotations

import json
from pathlib import Path

from os_lem.fixed_real_topology_hornresp_parity import (
    DEFAULT_HORNRESP_BASELINE_PARITY_FIXTURE,
    evaluate_fixed_real_topology_hornresp_baseline_parity,
)
from os_lem.fixed_real_topology_normalization_adapter import example_authored_offset_line_tqwt_input


def test_fixed_real_topology_hornresp_parity_callable_returns_opt_consumable_fields() -> None:
    result = evaluate_fixed_real_topology_hornresp_baseline_parity()

    assert set(result) == {
        "baseline_parity_gate_status",
        "spl_parity_passed",
        "impedance_parity_passed",
        "spl_metric",
        "spl_threshold",
        "impedance_metric",
        "impedance_threshold",
        "frequency_hz",
        "parity_gate_reason",
        "spl_parity_reason",
        "impedance_parity_reason",
    }
    assert result["baseline_parity_gate_status"] in {"passed", "failed"}
    assert isinstance(result["spl_parity_passed"], bool)
    assert isinstance(result["impedance_parity_passed"], bool)
    assert isinstance(result["spl_metric"], float)
    assert isinstance(result["spl_threshold"], float)
    assert isinstance(result["impedance_metric"], float)
    assert isinstance(result["impedance_threshold"], float)
    assert isinstance(result["parity_gate_reason"], str)
    assert isinstance(result["spl_parity_reason"], str)
    assert isinstance(result["impedance_parity_reason"], str)
    assert result["frequency_hz"] == [30.0, 40.0, 60.0, 80.0, 120.0, 160.0]


def test_fixed_real_topology_hornresp_parity_callable_uses_honest_bounded_thresholds() -> None:
    result = evaluate_fixed_real_topology_hornresp_baseline_parity()

    assert result["spl_threshold"] == 12.0
    assert result["impedance_threshold"] == 25.0
    assert result["spl_threshold"] < 240.0
    assert result["impedance_threshold"] < 100000.0


def test_fixed_real_topology_hornresp_parity_callable_blocks_current_spl_mismatch() -> None:
    result = evaluate_fixed_real_topology_hornresp_baseline_parity()

    assert result["baseline_parity_gate_status"] == "failed"
    assert result["spl_parity_passed"] is False
    assert result["spl_metric"] > result["spl_threshold"]
    assert "failed" in result["parity_gate_reason"]
    assert "SPL" in result["spl_parity_reason"]


def test_fixed_real_topology_hornresp_parity_callable_keeps_impedance_gate_explicit() -> None:
    result = evaluate_fixed_real_topology_hornresp_baseline_parity()

    assert result["impedance_parity_passed"] is True
    assert result["impedance_metric"] <= result["impedance_threshold"]
    assert "Impedance" in result["impedance_parity_reason"]


def test_fixed_real_topology_hornresp_parity_callable_accepts_bounded_authored_input() -> None:
    authored = example_authored_offset_line_tqwt_input()
    result = evaluate_fixed_real_topology_hornresp_baseline_parity(authored)

    assert result["baseline_parity_gate_status"] == "failed"
    assert result["spl_parity_passed"] is False
    assert isinstance(result["parity_gate_reason"], str)


def test_fixed_real_topology_hornresp_parity_callable_reports_failed_gate(tmp_path: Path) -> None:
    with Path(DEFAULT_HORNRESP_BASELINE_PARITY_FIXTURE).open("r", encoding="utf-8") as handle:
        fixture = json.load(handle)

    fixture["spl_total_db"] = [1.0e9 for _ in fixture["frequency_hz"]]
    fixture["impedance_mag_ohm"] = [1.0e9 for _ in fixture["frequency_hz"]]
    fixture["smoke_grade_thresholds"] = {
        "max_abs_spl_db": 0.001,
        "max_abs_impedance_mag_ohm": 0.001,
    }
    failing_fixture = tmp_path / "failing_hornresp_fixture.json"
    failing_fixture.write_text(json.dumps(fixture), encoding="utf-8")

    result = evaluate_fixed_real_topology_hornresp_baseline_parity(
        hornresp_fixture_path=failing_fixture
    )

    assert result["baseline_parity_gate_status"] == "failed"
    assert result["spl_parity_passed"] is False
    assert result["impedance_parity_passed"] is False
    assert "failed" in result["parity_gate_reason"]
    assert "failed" in result["spl_parity_reason"]
    assert "failed" in result["impedance_parity_reason"]
