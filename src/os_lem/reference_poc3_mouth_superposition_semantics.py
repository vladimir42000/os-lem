from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import numpy as np


DEFAULT_FLOOR_DB = -300.0


@dataclass(frozen=True)
class CandidateScore:
    label: str
    mae_db: float
    finite_points: int
    notes: str = ""


@dataclass(frozen=True)
class ResidualClassification:
    category: str
    interpretation: str


def _as_array(values: Iterable[float]) -> np.ndarray:
    return np.asarray(list(values), dtype=float)


def db_to_power(values_db: Iterable[float]) -> np.ndarray:
    values = _as_array(values_db)
    return np.power(10.0, values / 10.0)


def power_to_db(values_power: Iterable[float], floor_db: float = DEFAULT_FLOOR_DB) -> np.ndarray:
    values = _as_array(values_power)
    floor_power = 10.0 ** (floor_db / 10.0)
    clipped = np.clip(values, floor_power, None)
    result = 10.0 * np.log10(clipped)
    return np.where(np.isfinite(values), result, np.nan)


def db_to_amplitude(values_db: Iterable[float]) -> np.ndarray:
    values = _as_array(values_db)
    return np.power(10.0, values / 20.0)


def amplitude_to_db(values_amplitude: Iterable[float], floor_db: float = DEFAULT_FLOOR_DB) -> np.ndarray:
    values = _as_array(values_amplitude)
    floor_amplitude = 10.0 ** (floor_db / 20.0)
    clipped = np.clip(values, floor_amplitude, None)
    result = 20.0 * np.log10(clipped)
    return np.where(np.isfinite(values), result, np.nan)


def power_sum_db(lhs_db: Iterable[float], rhs_db: Iterable[float], floor_db: float = DEFAULT_FLOOR_DB) -> np.ndarray:
    lhs_power = db_to_power(lhs_db)
    rhs_power = db_to_power(rhs_db)
    return power_to_db(lhs_power + rhs_power, floor_db=floor_db)


def amplitude_sum_db(lhs_db: Iterable[float], rhs_db: Iterable[float], floor_db: float = DEFAULT_FLOOR_DB) -> np.ndarray:
    lhs_amplitude = db_to_amplitude(lhs_db)
    rhs_amplitude = db_to_amplitude(rhs_db)
    return amplitude_to_db(lhs_amplitude + rhs_amplitude, floor_db=floor_db)


def implied_residual_power_db(
    total_db: Iterable[float],
    known_branch_db: Iterable[float],
    floor_db: float = DEFAULT_FLOOR_DB,
) -> np.ndarray:
    residual_power = db_to_power(total_db) - db_to_power(known_branch_db)
    residual_power = np.where(residual_power > 0.0, residual_power, np.nan)
    return power_to_db(residual_power, floor_db=floor_db)


def implied_residual_amplitude_db(
    total_db: Iterable[float],
    known_branch_db: Iterable[float],
    floor_db: float = DEFAULT_FLOOR_DB,
) -> np.ndarray:
    residual_amplitude = db_to_amplitude(total_db) - db_to_amplitude(known_branch_db)
    residual_amplitude = np.where(residual_amplitude > 0.0, residual_amplitude, np.nan)
    return amplitude_to_db(residual_amplitude, floor_db=floor_db)


def mean_absolute_error_db(reference_db: Iterable[float], candidate_db: Iterable[float]) -> CandidateScore:
    reference = _as_array(reference_db)
    candidate = _as_array(candidate_db)
    mask = np.isfinite(reference) & np.isfinite(candidate)
    if not np.any(mask):
        return CandidateScore(label="", mae_db=float("inf"), finite_points=0)
    mae = float(np.mean(np.abs(reference[mask] - candidate[mask])))
    return CandidateScore(label="", mae_db=mae, finite_points=int(np.count_nonzero(mask)))


def score_candidates(reference_db: Iterable[float], candidates: Dict[str, Iterable[float]]) -> List[CandidateScore]:
    reference = _as_array(reference_db)
    scores: List[CandidateScore] = []
    for label, candidate_values in candidates.items():
        scored = mean_absolute_error_db(reference, candidate_values)
        scores.append(
            CandidateScore(
                label=label,
                mae_db=scored.mae_db,
                finite_points=scored.finite_points,
            )
        )
    return sorted(scores, key=lambda item: (item.mae_db, -item.finite_points, item.label))


def classify_mouth_residual(
    baseline_mouth_mae_db: float,
    best_alternative_mae_db: float,
    total_mae_db: float,
    best_alternative_label: str,
) -> ResidualClassification:
    improvement_db = baseline_mouth_mae_db - best_alternative_mae_db

    if total_mae_db <= 6.0 and improvement_db >= 3.0:
        return ResidualClassification(
            category="model-equivalence",
            interpretation=(
                "total SPL remains benchmark-close while a phase-free alternative meaningfully "
                f"reduces the mouth residual; strongest candidate: {best_alternative_label}"
            ),
        )

    if total_mae_db <= 6.0:
        return ResidualClassification(
            category="model-equivalence",
            interpretation=(
                "total SPL remains benchmark-close and semantic alternatives do not overturn the "
                "dominant reading; residual remains mainly a partition / convention issue"
            ),
        )

    if improvement_db >= 2.0:
        return ResidualClassification(
            category="missing-physics",
            interpretation=(
                "mouth semantic alternatives help, but total mismatch is too large to treat the "
                f"residual as convention-only; strongest candidate: {best_alternative_label}"
            ),
        )

    return ResidualClassification(
        category="solver/pathology",
        interpretation=(
            "total mismatch is not benchmark-close and semantic alternatives do not materially improve "
            "the mouth residual"
        ),
    )


def build_partition_semantic_candidates(
    total_db: Iterable[float],
    front_db: Iterable[float],
    mouth_db: Iterable[float],
) -> Dict[str, np.ndarray]:
    total = _as_array(total_db)
    front = _as_array(front_db)
    mouth = _as_array(mouth_db)
    return {
        "direct_mouth": mouth,
        "implied_mouth_power_from_total_minus_front": implied_residual_power_db(total, front),
        "implied_mouth_amplitude_from_total_minus_front": implied_residual_amplitude_db(total, front),
        "reconstructed_total_power_from_front_plus_mouth": power_sum_db(front, mouth),
        "reconstructed_total_amplitude_from_front_plus_mouth": amplitude_sum_db(front, mouth),
    }
