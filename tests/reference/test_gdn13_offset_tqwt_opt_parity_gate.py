from __future__ import annotations

from os_lem.gdn13_offset_tqwt_opt_parity_gate import (
    CASE_ID,
    KERNEL_COMMIT_BASIS,
    export_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt,
    get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt,
)


def test_gdn13_offset_tqwt_opt_parity_gate_contract_fields_are_machine_consumable() -> None:
    gate = get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt()

    required_fields = {
        "case_id",
        "kernel_commit_basis",
        "spl_reference",
        "spl_observable",
        "spl_band_hz",
        "spl_parity_passed",
        "spl_mae_db",
        "spl_rms_db",
        "spl_max_abs_db",
        "impedance_reference",
        "impedance_observable",
        "impedance_band_hz",
        "impedance_parity_passed",
        "ze_mae_ohm",
        "ze_rms_ohm",
        "ze_max_abs_ohm",
        "frequency_hz",
        "optimizer_gate_status",
        "full_band_spl_claim",
        "mouth_only_spl_claim",
        "limitations",
    }
    assert required_fields.issubset(gate.keys())
    assert gate["case_id"] == CASE_ID == "gdn13_offset_tqwt"
    assert gate["kernel_commit_basis"] == KERNEL_COMMIT_BASIS == "64f8dbb"
    assert gate["callable_path"].endswith("get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt")
    assert isinstance(gate["frequency_hz"], list)
    assert len(gate["frequency_hz"]) == 533


def test_gdn13_offset_tqwt_opt_parity_gate_uses_accepted_spl_and_impedance_basis() -> None:
    gate = get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt()

    assert gate["spl_observable"] == "spl_total_diagnostic"
    assert "HornResp SPL column" in gate["spl_reference"]
    assert gate["spl_band_hz"]["scope"] == "low_frequency_only"
    assert gate["spl_band_hz"]["max_hz"] <= 600.0
    assert gate["spl_parity_passed"] is True
    assert gate["spl_mae_db"] < gate["spl_mae_threshold_db"]
    assert gate["spl_rms_db"] < gate["spl_rms_threshold_db"]
    assert 0.3 < gate["spl_mae_db"] < 0.7
    assert 0.7 < gate["spl_rms_db"] < 1.3

    assert "HornResp Ze column" in gate["impedance_reference"]
    assert "electrical impedance" in gate["impedance_observable"]
    assert gate["impedance_band_hz"]["scope"] == "low_frequency_only"
    assert gate["impedance_band_hz"]["max_hz"] <= 600.0
    assert gate["impedance_parity_passed"] is True
    assert gate["ze_mae_ohm"] < gate["ze_mae_threshold_ohm"]
    assert gate["ze_rms_ohm"] < gate["ze_rms_threshold_ohm"]
    assert 0.2 < gate["ze_mae_ohm"] < 0.7


def test_gdn13_offset_tqwt_opt_parity_gate_blocks_wrong_claim_surface() -> None:
    gate = get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt()

    assert gate["optimizer_gate_status"] == "passed"
    assert "low-frequency SPL uses HornResp SPL vs os-lem spl_total_diagnostic" in gate["optimizer_gate_reason"]
    assert gate["full_band_spl_claim"] is False
    assert gate["mouth_only_spl_claim"] is False
    assert gate["mouth_only_rejected_observable"] == "spl_mouth"
    assert gate["mouth_only_low_frequency_mae_db"] > gate["spl_mae_db"] + 5.0
    assert gate["full_band_spl_metrics_visible"] is True
    assert gate["full_band_spl_metrics"]["mae_db"] > gate["spl_mae_db"]
    assert "does not establish full-band SPL parity" in gate["limitations"]
    assert "mouth-only SPL is rejected as the comparison target for this case" in gate["limitations"]


def test_gdn13_offset_tqwt_opt_parity_gate_export_alias_matches_primary_callable() -> None:
    assert export_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt() == get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt()
