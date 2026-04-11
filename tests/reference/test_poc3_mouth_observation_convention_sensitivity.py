from __future__ import annotations

from os_lem.reference_poc3_mouth_observation_convention import (
    ConventionVariantScore,
    assess_convention_sensitivity,
    band_scores,
    rank_variant_scores,
)


def test_rank_variant_scores_prefers_lower_mouth_then_total_then_high_band() -> None:
    ranked = rank_variant_scores(
        [
            ConventionVariantScore(
                label="b",
                mouth_model="flanged_piston",
                mouth_contract="raw",
                hornresp_mouth_mae_db=10.0,
                hornresp_total_mae_db=5.5,
                hornresp_front_mae_db=2.0,
                akabak_total_mae_db=1.0,
                high_band_mouth_mae_db=40.0,
            ),
            ConventionVariantScore(
                label="a",
                mouth_model="flanged_piston",
                mouth_contract="mouth_directivity_only",
                hornresp_mouth_mae_db=10.0,
                hornresp_total_mae_db=5.0,
                hornresp_front_mae_db=2.0,
                akabak_total_mae_db=1.0,
                high_band_mouth_mae_db=50.0,
            ),
        ]
    )

    assert [item.label for item in ranked] == ["a", "b"]


def test_assess_convention_sensitivity_marks_material_when_mouth_improves_without_total_collapse() -> None:
    ranked = rank_variant_scores(
        [
            ConventionVariantScore(
                label="best",
                mouth_model="flanged_piston",
                mouth_contract="mouth_directivity_only",
                hornresp_mouth_mae_db=10.0,
                hornresp_total_mae_db=5.2,
                hornresp_front_mae_db=2.0,
                akabak_total_mae_db=1.0,
                high_band_mouth_mae_db=25.0,
            )
        ]
    )

    assessment = assess_convention_sensitivity(
        baseline_mouth_mae_db=14.6,
        baseline_total_mae_db=4.9,
        ranked_scores=ranked,
    )

    assert assessment.category == "material-supported-convention-sensitivity"
    assert assessment.best_variant_label == "best"


def test_assess_convention_sensitivity_keeps_survival_reading_when_total_penalty_is_too_large() -> None:
    ranked = rank_variant_scores(
        [
            ConventionVariantScore(
                label="best",
                mouth_model="flanged_piston",
                mouth_contract="mouth_directivity_only",
                hornresp_mouth_mae_db=10.0,
                hornresp_total_mae_db=7.5,
                hornresp_front_mae_db=2.0,
                akabak_total_mae_db=1.0,
                high_band_mouth_mae_db=25.0,
            )
        ]
    )

    assessment = assess_convention_sensitivity(
        baseline_mouth_mae_db=14.6,
        baseline_total_mae_db=4.9,
        ranked_scores=ranked,
    )

    assert assessment.category == "survives-supported-convention-sweep"


def test_band_scores_report_expected_ranges_and_counts() -> None:
    scores = band_scores(
        frequencies_hz=[50.0, 500.0, 5000.0],
        reference_db=[1.0, 2.0, 3.0],
        candidate_db=[2.0, 1.0, 5.0],
        label_prefix="demo",
    )

    assert [score.label for score in scores] == ["demo:low", "demo:mid", "demo:high"]
    assert [score.finite_points for score in scores] == [1, 1, 1]
    assert scores[0].mae_db == 1.0
    assert scores[2].max_abs_delta_db == 2.0
