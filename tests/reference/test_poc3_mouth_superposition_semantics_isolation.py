from __future__ import annotations

import numpy as np

from os_lem.reference_poc3_mouth_superposition_semantics import (
    amplitude_sum_db,
    build_partition_semantic_candidates,
    classify_mouth_residual,
    implied_residual_amplitude_db,
    implied_residual_power_db,
    power_sum_db,
    score_candidates,
)


def test_power_sum_db_matches_manual_reference() -> None:
    lhs = np.array([60.0, 70.0])
    rhs = np.array([60.0, 64.0])

    result = power_sum_db(lhs, rhs)
    expected = 10.0 * np.log10(np.power(10.0, lhs / 10.0) + np.power(10.0, rhs / 10.0))

    assert np.allclose(result, expected)


def test_amplitude_sum_db_matches_manual_reference() -> None:
    lhs = np.array([40.0, 50.0])
    rhs = np.array([34.0, 38.0])

    result = amplitude_sum_db(lhs, rhs)
    expected = 20.0 * np.log10(np.power(10.0, lhs / 20.0) + np.power(10.0, rhs / 20.0))

    assert np.allclose(result, expected)


def test_implied_residual_power_db_inverts_power_sum() -> None:
    front = np.array([70.0, 74.0, 78.0])
    mouth = np.array([60.0, 61.0, 62.0])
    total = power_sum_db(front, mouth)

    recovered = implied_residual_power_db(total, front)

    assert np.allclose(recovered, mouth)


def test_implied_residual_amplitude_db_inverts_amplitude_sum_when_valid() -> None:
    front = np.array([65.0, 67.0, 69.0])
    mouth = np.array([54.0, 55.0, 56.0])
    total = amplitude_sum_db(front, mouth)

    recovered = implied_residual_amplitude_db(total, front)

    assert np.allclose(recovered, mouth)


def test_synthetic_ranking_prefers_power_residual_partition_case() -> None:
    front = np.array([80.0, 80.0, 80.0, 80.0])
    mouth_true = np.array([60.0, 61.0, 62.0, 63.0])
    total = power_sum_db(front, mouth_true)

    # Direct reported mouth is biased high; implied power residual should recover the true curve.
    oslem_reported_mouth = mouth_true + 6.0
    hornresp_reference_mouth = mouth_true

    candidates = build_partition_semantic_candidates(
        total_db=total,
        front_db=front,
        mouth_db=oslem_reported_mouth,
    )
    ranked = score_candidates(
        reference_db=hornresp_reference_mouth,
        candidates={
            "direct_mouth": candidates["direct_mouth"],
            "implied_mouth_power": candidates["implied_mouth_power_from_total_minus_front"],
            "implied_mouth_amplitude": candidates["implied_mouth_amplitude_from_total_minus_front"],
        },
    )

    assert ranked[0].label == "implied_mouth_power"
    assert ranked[0].mae_db < 0.01
    direct_score = next(score for score in ranked if score.label == "direct_mouth")
    assert direct_score.mae_db > ranked[0].mae_db


def test_classification_stays_model_equivalence_when_total_is_good() -> None:
    result = classify_mouth_residual(
        baseline_mouth_mae_db=14.513826,
        best_alternative_mae_db=10.0,
        total_mae_db=4.896901,
        best_alternative_label="implied_mouth_power",
    )

    assert result.category == "model-equivalence"
    assert "implied_mouth_power" in result.interpretation
