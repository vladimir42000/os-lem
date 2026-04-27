from __future__ import annotations

from os_lem.fixed_real_topology_hornresp_parity import (
    DEFAULT_HORNRESP_BASELINE_PARITY_FIXTURE,
    evaluate_fixed_real_topology_hornresp_baseline_parity,
)


def test_fixed_real_topology_adapter_solver_hornresp_baseline_parity_smoke() -> None:
    result = evaluate_fixed_real_topology_hornresp_baseline_parity()

    assert DEFAULT_HORNRESP_BASELINE_PARITY_FIXTURE.name == "HORNRESP_BASELINE_PARITY.json"
    assert result["baseline_parity_gate_status"] == "failed"
    assert result["spl_parity_passed"] is False
    assert result["spl_metric"] > result["spl_threshold"]
    assert result["impedance_parity_passed"] is True
    assert result["impedance_metric"] <= result["impedance_threshold"]
    assert result["frequency_hz"] == [30.0, 40.0, 60.0, 80.0, 120.0, 160.0]
    assert "failed" in result["parity_gate_reason"]
