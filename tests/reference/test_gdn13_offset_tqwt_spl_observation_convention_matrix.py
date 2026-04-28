from __future__ import annotations

from pathlib import Path

from os_lem.reference_gdn13_offset_tqwt_spl_observation_matrix import (
    evaluate_gdn13_offset_tqwt_spl_observation_convention_matrix,
)


_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "reference_data" / "hornresp_gdn13_offset_tqwt"
_DEFINITION = _FIXTURE_DIR / "gdn13tHRl.txt"
_RESPONSE = _FIXTURE_DIR / "gdn13tl.txt"


_ALLOWED_CLASSIFICATIONS = {
    "mostly_constant_level_scaling",
    "likely_wrong_spl_output_channel",
    "likely_missing_driver_direct_contribution",
    "likely_coherent_summation_phase_convention_issue",
    "likely_radiation_reference_distance_convention_issue",
    "still_unresolved",
}


def test_gdn13_spl_observation_convention_matrix_is_bounded_and_diagnostic() -> None:
    report = evaluate_gdn13_offset_tqwt_spl_observation_convention_matrix(
        hornresp_definition_path=_DEFINITION,
        hornresp_response_path=_RESPONSE,
        profile="parabolic",
    )

    assert report["task"] == "test/v0.8.0-gdn13-offset-tqwt-spl-observation-convention-matrix"
    assert report["diagnostic_scope"] == "SPL observation-convention matrix only; no SPL repair"
    assert report["no_spl_repair_made"] is True
    assert report["hornresp_authority_column"] == "SPL column from gdn13tl.txt"
    assert report["frequency_count"] == 533
    assert report["low_frequency_limit_hz"] == 600.0
    assert report["low_frequency_count"] > 100

    inspected = report["inspected_spl_observables"]
    assert inspected == sorted(inspected)
    assert "spl_mouth" in inspected
    assert report["candidate_count"] == len(inspected)

    matrix = report["candidate_matrix"]
    assert set(matrix) == set(inspected)
    for candidate_id, candidate in matrix.items():
        assert candidate["candidate_id"] == candidate_id
        assert candidate["candidate_role"]
        for comparison_key in ("raw", "constant_offset_adjusted"):
            comparison = candidate[comparison_key]
            assert comparison["full"]["mean_abs"] >= 0.0
            assert comparison["full"]["rms"] >= 0.0
            assert comparison["full"]["max_abs"] >= 0.0
            assert comparison["low_frequency_le_600_hz"]["mean_abs"] >= 0.0
            assert comparison["low_frequency_le_600_hz"]["rms"] >= 0.0
            assert comparison["low_frequency_le_600_hz"]["max_abs"] >= 0.0
        assert "best_fit_offset_db_added_to_oslem_candidate_over_lf_le_600_hz" in candidate[
            "constant_offset_adjusted"
        ]
        assert len(candidate["diagnostic_scalar_checks"]) >= 4

    phase_diag = report["phase_or_coherent_summation_diagnostic"]
    assert phase_diag["available_from_current_result_fields"] is False
    assert "do not expose complex pressure/phase arrays" in phase_diag["interpretation"]

    best = report["best_candidate_summary"]
    assert report["classification"] in _ALLOWED_CLASSIFICATIONS
    assert report["classification_label"]
    assert report["classification_basis"] == best["basis"]
    assert best["best_raw_candidate"]["candidate_id"] in inspected
    assert best["best_offset_adjusted_candidate"]["candidate_id"] in inspected

    assert "this does not establish SPL parity" in report["non_claims"]
    assert "this does not alter topology or solver semantics" in report["non_claims"]
    assert "no SPL repair" in report["scope_guards"]
    assert "no general HornResp importer" in report["scope_guards"]


def test_gdn13_spl_observation_convention_matrix_is_deterministic() -> None:
    first = evaluate_gdn13_offset_tqwt_spl_observation_convention_matrix(
        hornresp_definition_path=_DEFINITION,
        hornresp_response_path=_RESPONSE,
        profile="parabolic",
    )
    second = evaluate_gdn13_offset_tqwt_spl_observation_convention_matrix(
        hornresp_definition_path=_DEFINITION,
        hornresp_response_path=_RESPONSE,
        profile="parabolic",
    )

    assert first["inspected_spl_observables"] == second["inspected_spl_observables"]
    assert first["classification"] == second["classification"]
    assert first["candidate_matrix"] == second["candidate_matrix"]
