from __future__ import annotations

from pathlib import Path

from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    build_gdn13_offset_tqwt_model_dict,
    evaluate_gdn13_offset_tqwt_mapping_trial,
    gdn13_hornresp_driver_derived_parameters,
    load_hornresp_gdn13_response_table,
    parse_hornresp_definition_sections,
)


_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "reference_data" / "hornresp_gdn13_offset_tqwt"
_DEFINITION = _FIXTURE_DIR / "gdn13tHRl.txt"
_RESPONSE = _FIXTURE_DIR / "gdn13tl.txt"


def test_gdn13_supplied_hornresp_files_are_latest_expected_inputs() -> None:
    assert _DEFINITION.exists()
    assert _RESPONSE.exists()

    sections = parse_hornresp_definition_sections(_DEFINITION)
    assert sections["traditional_driver"]["Le"] == 1.00
    assert sections["traditional_driver"]["Re"] == 6.50
    assert sections["traditional_driver"]["Sd"] == 82.00
    assert sections["absorbent"]["Tal1"] == 0.0
    assert sections["absorbent"]["Tal2"] == 0.0

    table = load_hornresp_gdn13_response_table(_RESPONSE)
    assert table["frequency_hz"].shape == table["spl_db"].shape == table["ze_ohm"].shape
    assert table["frequency_hz"].size == 533
    assert table["frequency_hz"][0] == 10.0
    assert table["frequency_hz"][-1] == 20000.0


def test_gdn13_offset_tqwt_model_dict_is_explicit_and_bounded() -> None:
    model_dict = build_gdn13_offset_tqwt_model_dict(profile="parabolic")
    element_ids = {element["id"] for element in model_dict["elements"]}

    assert model_dict["meta"]["mapping_trial_only"] is True
    assert model_dict["driver"]["node_rear"] == "tap_s2"
    assert model_dict["driver"]["node_front"] == "driver_front"
    assert {"rear_closed_stub_s1_to_s2", "forward_open_line_s2_to_s3", "mouth_s3_radiation"}.issubset(element_ids)

    rear_stub = next(element for element in model_dict["elements"] if element["id"] == "rear_closed_stub_s1_to_s2")
    forward_line = next(element for element in model_dict["elements"] if element["id"] == "forward_open_line_s2_to_s3")
    assert rear_stub["node_a"] == "closed_end_s1"
    assert rear_stub["node_b"] == "tap_s2"
    assert forward_line["node_a"] == "tap_s2"
    assert forward_line["node_b"] == "mouth_s3"
    assert rear_stub["profile"] == "parabolic"
    assert forward_line["profile"] == "parabolic"


def test_gdn13_driver_hornresp_inputs_are_mapped_to_existing_ts_classic_surface() -> None:
    driver = gdn13_hornresp_driver_derived_parameters()

    assert driver.re_ohm == 6.50
    assert driver.le_mh == 1.00
    assert driver.sd_cm2 == 82.00
    assert driver.bl_tm == 6.16
    assert driver.cms_m_per_n == 1.01e-3
    assert driver.rms_mechanical == 0.49
    assert driver.mmd_g == 8.50
    assert 40.0 < driver.fs_hz < 70.0
    assert 0.1 < driver.qes < 2.0
    assert 1.0 < driver.qms < 20.0
    assert 1.0 < driver.vas_l < 50.0


def test_gdn13_offset_tqwt_hornresp_mapping_trial_runs_and_reports_metrics() -> None:
    report = evaluate_gdn13_offset_tqwt_mapping_trial(
        hornresp_definition_path=_DEFINITION,
        hornresp_response_path=_RESPONSE,
        profile="parabolic",
    )

    assert report["task"] == "test/v0.8.0-gdn13-offset-tqwt-hornresp-mapping-trial"
    assert report["compared_columns"] == ["Freq (hertz)", "SPL (dB)", "Ze (ohms)"]
    assert report["frequency_count"] == 533
    assert report["low_frequency_count_le_600_hz"] > 100
    assert report["model_dict_construction_path"].endswith("build_gdn13_offset_tqwt_model_dict(profile='parabolic')")
    assert report["solver_call_path"] == "os_lem.api.run_simulation(model_dict, frequency_hz)"
    assert (
        report["mapping_trial_interpretation"]
        == "Impedance/topology mapping is promising, but SPL observation/radiation/output convention remains unresolved."
    )
    assert report["spl_parity_non_claim"] == "not SPL parity success; SPL mismatch remains explicitly reported"
    assert "not SPL parity success" in report["non_claims"]

    impedance = report["impedance_comparison"]
    spl = report["spl_comparison"]

    assert impedance["full"]["max_abs"] >= 0.0
    assert impedance["low_frequency_le_600_hz"]["mean_abs"] >= 0.0
    assert impedance["hornresp_low_frequency_peak"]["frequency_hz"] > 0.0
    assert impedance["oslem_low_frequency_peak"]["frequency_hz"] > 0.0

    assert spl["full"]["max_abs"] >= 0.0
    assert spl["low_frequency_le_600_hz"]["mean_abs"] >= 0.0
    assert spl["low_frequency_zero_mean_shape"]["mean_abs"] >= 0.0
    assert spl["low_frequency_le_600_hz"]["mean_abs"] > 5.0

    assert report["mismatch_interpretation"] in {
        "topology_or_driver_electrical_mapping_mismatch_likely",
        "spl_observation_or_radiation_output_convention_unresolved",
        "spl_observation_or_normalization_mismatch_likely",
        "mixed_spl_and_possible_observation_mismatch",
        "bounded_mapping_trial_no_large_first_order_mismatch_detected",
        "undetermined_nonpositive_peak_frequency",
    }
    assert "no general HornResp importer" in report["scope_guards"]
    assert "no optimizer implementation" in report["scope_guards"]
