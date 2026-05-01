from __future__ import annotations

import inspect

import numpy as np

import os_lem.gdn13_offset_tqwt_opt_model_packet as packet_module
from os_lem.api import run_simulation
from os_lem.gdn13_offset_tqwt_opt_model_packet import (
    export_gdn13_offset_tqwt_normalized_model_packet_for_opt,
    get_gdn13_offset_tqwt_normalized_model_packet_for_opt,
)
from os_lem.gdn13_offset_tqwt_opt_parity_gate import (
    get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt,
)
from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    build_gdn13_offset_tqwt_model_dict,
)


def test_gdn13_offset_tqwt_opt_model_packet_imports_and_passes_when_gate_passes() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    gate = get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt()

    assert gate["optimizer_gate_status"] == "passed"
    assert packet["packet_status"] == "passed"
    assert packet["case_id"] == "gdn13_offset_tqwt"
    assert packet["kernel_commit_basis"] == gate["kernel_commit_basis"]
    assert packet["export_commit_requirement"] == "d2e429c"
    assert packet["baseline_parity_gate_status"] == "passed"
    assert packet["spl_parity_passed"] is True
    assert packet["impedance_parity_passed"] is True


def test_gdn13_offset_tqwt_opt_model_packet_exposes_required_machine_fields() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()

    required = {
        "packet_status",
        "case_id",
        "kernel_commit_basis",
        "export_commit_requirement",
        "model_dict",
        "frequencies_hz",
        "solver_callable",
        "parity_callable",
        "spl_observable",
        "spl_reference",
        "impedance_observable",
        "impedance_reference",
        "parity_band",
        "baseline_parity_gate_status",
        "spl_parity_passed",
        "impedance_parity_passed",
        "spl_metric",
        "spl_threshold",
        "impedance_metric",
        "impedance_threshold",
        "full_band_spl_claim",
        "mouth_only_spl_claim",
        "normalization_owner",
        "model_construction_owner",
    }
    assert required.issubset(packet.keys())
    assert packet["model_dict"] is not None
    assert isinstance(packet["frequencies_hz"], list)
    assert len(packet["frequencies_hz"]) == 533
    assert packet["solver_callable"] == "os_lem.api.run_simulation"
    assert packet["parity_callable"].endswith("get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt")


def test_gdn13_offset_tqwt_opt_model_packet_runs_without_opt_side_normalization() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    frequency_hz = np.asarray(packet["frequencies_hz"][:16], dtype=float)

    result = run_simulation(packet["model_dict"], frequency_hz)

    assert result.zin_complex_ohm is not None
    assert np.asarray(result.zin_complex_ohm).shape == frequency_hz.shape
    assert packet["spl_observable"] in result.series
    assert np.asarray(result.series[packet["spl_observable"]]).shape == frequency_hz.shape
    assert np.all(np.isfinite(np.abs(result.zin_complex_ohm)))
    assert np.all(np.isfinite(result.series[packet["spl_observable"]]))


def test_gdn13_offset_tqwt_opt_model_packet_uses_accepted_spl_and_nonclaims() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()

    assert packet["spl_observable"] == "spl_total_diagnostic"
    assert "HornResp SPL column" in packet["spl_reference"]
    assert packet["impedance_observable"].startswith("abs(zin_complex_ohm)") or "electrical impedance" in packet["impedance_observable"]
    assert "HornResp Ze column" in packet["impedance_reference"]
    assert packet["parity_band"] == "frequency_hz <= 600.0"
    assert packet["full_band_spl_claim"] is False
    assert packet["mouth_only_spl_claim"] is False
    assert packet["mouth_only_rejected_observable"] == "spl_mouth"


def test_gdn13_offset_tqwt_opt_model_packet_reports_oslem_ownership_and_matches_builder() -> None:
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    expected = build_gdn13_offset_tqwt_model_dict(profile="parabolic")

    assert packet["normalization_owner"] == "os-lem"
    assert packet["model_construction_owner"] == "os-lem"
    assert packet["model_construction_source"].endswith("build_gdn13_offset_tqwt_model_dict(profile='parabolic')")
    assert packet["model_dict"] == expected


def test_gdn13_offset_tqwt_opt_model_packet_returns_defensive_model_dict_copy() -> None:
    packet_a = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    packet_b = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()

    packet_a["model_dict"]["meta"]["name"] = "mutated_by_consumer"

    assert packet_b["model_dict"]["meta"]["name"] == "gdn13_offset_tqwt_hornresp_mapping_trial"
    assert build_gdn13_offset_tqwt_model_dict(profile="parabolic")["meta"]["name"] == "gdn13_offset_tqwt_hornresp_mapping_trial"


def test_gdn13_offset_tqwt_opt_model_packet_alias_matches_primary_callable() -> None:
    assert export_gdn13_offset_tqwt_normalized_model_packet_for_opt() == get_gdn13_offset_tqwt_normalized_model_packet_for_opt()


def test_gdn13_offset_tqwt_opt_model_packet_does_not_add_fallback_or_resonator_semantics() -> None:
    source = inspect.getsource(packet_module)

    assert "fallback_normalization" not in source
    assert "resonator_slot" not in source
    assert "side_resonator" not in source
    packet = get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
    assert all("resonator" not in str(key).lower() for key in packet["model_dict"].keys())
    assert "no resonator semantics are included in this packet" in packet["limitations"]
