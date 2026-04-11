from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class BandScore:
    label: str
    f_min_hz: float
    f_max_hz: float
    mae_db: float
    max_abs_delta_db: float
    finite_points: int


@dataclass(frozen=True)
class ConventionVariantScore:
    label: str
    mouth_model: str
    mouth_contract: str
    hornresp_mouth_mae_db: float
    hornresp_total_mae_db: float
    hornresp_front_mae_db: float
    akabak_total_mae_db: float | None
    high_band_mouth_mae_db: float


@dataclass(frozen=True)
class ConventionSensitivityAssessment:
    category: str
    interpretation: str
    best_variant_label: str
    baseline_mouth_mae_db: float
    best_variant_mouth_mae_db: float
    best_variant_total_mae_db: float
    mouth_improvement_db: float
    total_penalty_db: float


BANDS: tuple[tuple[str, float, float], ...] = (
    ("low", 0.0, 200.0),
    ("mid", 200.0, 2000.0),
    ("high", 2000.0, 20000.0),
)

MATERIAL_MOUTH_IMPROVEMENT_DB = 3.0
ALLOWED_TOTAL_PENALTY_DB = 1.0


def _as_float_array(values: Iterable[float]) -> np.ndarray:
    return np.asarray(list(values), dtype=float)


def mean_absolute_error_db(reference_db: Iterable[float], candidate_db: Iterable[float]) -> tuple[float, int]:
    reference = _as_float_array(reference_db)
    candidate = _as_float_array(candidate_db)
    mask = np.isfinite(reference) & np.isfinite(candidate)
    if not np.any(mask):
        return float("inf"), 0
    delta = np.abs(reference[mask] - candidate[mask])
    return float(np.mean(delta)), int(np.count_nonzero(mask))


def band_scores(
    frequencies_hz: Iterable[float],
    reference_db: Iterable[float],
    candidate_db: Iterable[float],
    *,
    label_prefix: str,
    bands: Sequence[tuple[str, float, float]] = BANDS,
) -> list[BandScore]:
    frequencies = _as_float_array(frequencies_hz)
    reference = _as_float_array(reference_db)
    candidate = _as_float_array(candidate_db)
    scores: list[BandScore] = []
    finite = np.isfinite(frequencies) & np.isfinite(reference) & np.isfinite(candidate)
    for band_label, f_min_hz, f_max_hz in bands:
        mask = finite & (frequencies >= f_min_hz) & (frequencies < f_max_hz)
        if not np.any(mask):
            scores.append(
                BandScore(
                    label=f"{label_prefix}:{band_label}",
                    f_min_hz=f_min_hz,
                    f_max_hz=f_max_hz,
                    mae_db=float("inf"),
                    max_abs_delta_db=float("inf"),
                    finite_points=0,
                )
            )
            continue
        delta = np.abs(reference[mask] - candidate[mask])
        scores.append(
            BandScore(
                label=f"{label_prefix}:{band_label}",
                f_min_hz=f_min_hz,
                f_max_hz=f_max_hz,
                mae_db=float(np.mean(delta)),
                max_abs_delta_db=float(np.max(delta)),
                finite_points=int(np.count_nonzero(mask)),
            )
        )
    return scores


def rank_variant_scores(scores: Sequence[ConventionVariantScore]) -> list[ConventionVariantScore]:
    return sorted(
        scores,
        key=lambda item: (
            item.hornresp_mouth_mae_db,
            item.hornresp_total_mae_db,
            item.high_band_mouth_mae_db,
            item.label,
        ),
    )


def assess_convention_sensitivity(
    baseline_mouth_mae_db: float,
    baseline_total_mae_db: float,
    ranked_scores: Sequence[ConventionVariantScore],
) -> ConventionSensitivityAssessment:
    if not ranked_scores:
        return ConventionSensitivityAssessment(
            category="no-variants",
            interpretation="no supported mouth observation/convention variants were evaluated",
            best_variant_label="",
            baseline_mouth_mae_db=baseline_mouth_mae_db,
            best_variant_mouth_mae_db=float("inf"),
            best_variant_total_mae_db=float("inf"),
            mouth_improvement_db=float("-inf"),
            total_penalty_db=float("inf"),
        )

    best = ranked_scores[0]
    mouth_improvement_db = float(baseline_mouth_mae_db - best.hornresp_mouth_mae_db)
    total_penalty_db = float(best.hornresp_total_mae_db - baseline_total_mae_db)

    if mouth_improvement_db >= MATERIAL_MOUTH_IMPROVEMENT_DB and total_penalty_db <= ALLOWED_TOTAL_PENALTY_DB:
        interpretation = (
            "the remaining mouth-side residual changes materially inside the currently supported mouth "
            "observation/radiator convention space without collapsing total-SPL agreement; strongest "
            f"variant: {best.label}"
        )
        category = "material-supported-convention-sensitivity"
    else:
        interpretation = (
            "the remaining mouth-side residual survives the currently supported mouth observation/radiator "
            "convention sweep; best supported variant does not materially overturn the frozen benchmark "
            f"reading (strongest variant: {best.label})"
        )
        category = "survives-supported-convention-sweep"

    return ConventionSensitivityAssessment(
        category=category,
        interpretation=interpretation,
        best_variant_label=best.label,
        baseline_mouth_mae_db=baseline_mouth_mae_db,
        best_variant_mouth_mae_db=best.hornresp_mouth_mae_db,
        best_variant_total_mae_db=best.hornresp_total_mae_db,
        mouth_improvement_db=mouth_improvement_db,
        total_penalty_db=total_penalty_db,
    )
