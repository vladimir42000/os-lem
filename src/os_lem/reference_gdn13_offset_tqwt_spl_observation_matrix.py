"""GDN13 offset-driver TQWT SPL observation-convention diagnostic matrix.

This module is intentionally bounded to the already-landed GDN13 HornResp
mapping trial.  It diagnoses which currently exposed os-lem SPL observation, if
any, best explains the HornResp SPL column.  It does not repair SPL behavior,
change radiation semantics, import HornResp models generally, or broaden the
optimizer-facing contract.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from os_lem.api import run_simulation
from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    build_gdn13_offset_tqwt_model_dict,
    load_hornresp_gdn13_response_table,
    parse_hornresp_definition_sections,
)

LOW_FREQUENCY_LIMIT_HZ = 600.0

# Diagnostic-only scalar offsets.  These are applied to already-computed SPL
# arrays to test convention hypotheses; solver/radiation behavior is not changed.
SCALAR_DIAGNOSTIC_OFFSETS_DB: tuple[tuple[str, float], ...] = (
    ("plus_3p0103_db_2pi_4pi_style_scalar_check", 3.010299956639812),
    ("minus_3p0103_db_2pi_4pi_style_scalar_check", -3.010299956639812),
    ("plus_6p0206_db_reference_distance_style_scalar_check", 6.020599913279624),
    ("minus_6p0206_db_reference_distance_style_scalar_check", -6.020599913279624),
)


def _metric_summary(delta_db: np.ndarray) -> dict[str, float]:
    return {
        "mean_abs": float(np.mean(np.abs(delta_db))),
        "rms": float(np.sqrt(np.mean(delta_db * delta_db))),
        "max_abs": float(np.max(np.abs(delta_db))),
    }


def _comparison_summary(
    *,
    candidate_spl_db: np.ndarray,
    hornresp_spl_db: np.ndarray,
    low_mask: np.ndarray,
) -> dict[str, Any]:
    raw_delta = candidate_spl_db - hornresp_spl_db
    low_raw_delta = raw_delta[low_mask]
    best_fit_offset_db = -float(np.mean(low_raw_delta))
    adjusted_delta = (candidate_spl_db + best_fit_offset_db) - hornresp_spl_db

    scalar_checks: dict[str, Any] = {}
    for name, offset_db in SCALAR_DIAGNOSTIC_OFFSETS_DB:
        scalar_delta = (candidate_spl_db + offset_db) - hornresp_spl_db
        scalar_checks[name] = {
            "applied_offset_db": float(offset_db),
            "full": _metric_summary(scalar_delta),
            "low_frequency_le_600_hz": _metric_summary(scalar_delta[low_mask]),
        }

    return {
        "raw": {
            "full": _metric_summary(raw_delta),
            "low_frequency_le_600_hz": _metric_summary(low_raw_delta),
        },
        "constant_offset_adjusted": {
            "best_fit_offset_db_added_to_oslem_candidate_over_lf_le_600_hz": float(best_fit_offset_db),
            "full": _metric_summary(adjusted_delta),
            "low_frequency_le_600_hz": _metric_summary(adjusted_delta[low_mask]),
        },
        "diagnostic_scalar_checks": scalar_checks,
    }


def _candidate_role(candidate_id: str) -> str:
    lowered = candidate_id.lower()
    if "mouth" in lowered:
        return "mouth SPL observable"
    if "front" in lowered or "driver" in lowered or "direct" in lowered:
        return "front/direct/driver SPL observable"
    if "total" in lowered or "sum" in lowered or "combined" in lowered:
        return "total/combined SPL observable"
    return "named SPL observable returned by os-lem"


def _append_front_spl_diagnostic_observation(model_dict: Mapping[str, Any]) -> dict[str, Any]:
    """Return a diagnostic copy with a driver-front SPL observation if possible."""

    model = deepcopy(model_dict)
    observations = list(model.get("observations", []))
    existing_ids = {str(obs.get("id")) for obs in observations if isinstance(obs, Mapping)}
    element_ids = {str(elem.get("id")) for elem in model.get("elements", []) if isinstance(elem, Mapping)}

    if "driver_front_radiation_diagnostic" in element_ids and "spl_driver_front_diagnostic" not in existing_ids:
        observations.append(
            {
                "id": "spl_driver_front_diagnostic",
                "type": "spl",
                "target": "driver_front_radiation_diagnostic",
                "distance": "1 m",
                "radiation_space": "2pi",
            }
        )
    model["observations"] = observations
    return model


def _extract_spl_candidates(result: Any, frequency_hz: np.ndarray) -> dict[str, np.ndarray]:
    """Extract all finite one-dimensional SPL-like fields currently exposed."""

    candidates: dict[str, np.ndarray] = {}
    series = getattr(result, "series", {})
    if not isinstance(series, Mapping):
        return candidates

    for key, values in series.items():
        key_text = str(key)
        if "spl" not in key_text.lower():
            continue
        array = np.asarray(values, dtype=float)
        if array.shape != frequency_hz.shape:
            continue
        if not np.all(np.isfinite(array)):
            continue
        candidates[key_text] = array

    return dict(sorted(candidates.items()))


def _best_scalar_check(candidate_matrices: Mapping[str, Mapping[str, Any]]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for candidate_id, matrix in candidate_matrices.items():
        for transform_name, transform in matrix["diagnostic_scalar_checks"].items():
            metric = float(transform["low_frequency_le_600_hz"]["mean_abs"])
            record = {
                "candidate_id": candidate_id,
                "transform": transform_name,
                "applied_offset_db": float(transform["applied_offset_db"]),
                "low_frequency_mean_abs_db": metric,
                "full_mean_abs_db": float(transform["full"]["mean_abs"]),
            }
            if best is None or metric < best["low_frequency_mean_abs_db"]:
                best = record
    return best


def _classify_mismatch(candidate_matrices: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Classify the SPL mismatch from computed matrix metrics only."""

    raw_ranked = sorted(
        (
            {
                "candidate_id": candidate_id,
                "low_frequency_mean_abs_db": float(matrix["raw"]["low_frequency_le_600_hz"]["mean_abs"]),
                "full_mean_abs_db": float(matrix["raw"]["full"]["mean_abs"]),
            }
            for candidate_id, matrix in candidate_matrices.items()
        ),
        key=lambda row: row["low_frequency_mean_abs_db"],
    )
    adjusted_ranked = sorted(
        (
            {
                "candidate_id": candidate_id,
                "best_fit_offset_db": float(
                    matrix["constant_offset_adjusted"][
                        "best_fit_offset_db_added_to_oslem_candidate_over_lf_le_600_hz"
                    ]
                ),
                "low_frequency_mean_abs_db": float(
                    matrix["constant_offset_adjusted"]["low_frequency_le_600_hz"]["mean_abs"]
                ),
                "full_mean_abs_db": float(matrix["constant_offset_adjusted"]["full"]["mean_abs"]),
            }
            for candidate_id, matrix in candidate_matrices.items()
        ),
        key=lambda row: row["low_frequency_mean_abs_db"],
    )

    if not raw_ranked or not adjusted_ranked:
        return {
            "classification": "still_unresolved",
            "classification_label": "still unresolved",
            "basis": "no usable SPL observable was exposed by current os-lem result fields",
            "best_raw_candidate": None,
            "best_offset_adjusted_candidate": None,
            "best_scalar_check": None,
        }

    best_raw = raw_ranked[0]
    best_adjusted = adjusted_ranked[0]
    best_scalar = _best_scalar_check(candidate_matrices)
    mouth_raw = next((row for row in raw_ranked if row["candidate_id"] == "spl_mouth"), None)
    improvement_vs_mouth = None
    if mouth_raw is not None:
        improvement_vs_mouth = mouth_raw["low_frequency_mean_abs_db"] - best_raw["low_frequency_mean_abs_db"]

    classification = "still_unresolved"
    label = "still unresolved"
    basis = (
        "no available SPL candidate or scalar diagnostic transform reduces both low-frequency and full-band "
        "residuals enough to identify a convincing HornResp SPL observation convention"
    )

    if improvement_vs_mouth is not None and improvement_vs_mouth > 3.0 and "front" in best_raw["candidate_id"].lower():
        classification = "likely_wrong_spl_output_channel"
        label = "likely wrong SPL output channel"
        basis = "a front/direct/driver SPL observable is materially closer than the mouth SPL observable"
    elif improvement_vs_mouth is not None and improvement_vs_mouth > 3.0 and (
        "total" in best_raw["candidate_id"].lower() or "sum" in best_raw["candidate_id"].lower()
    ):
        classification = "likely_missing_driver_direct_contribution"
        label = "likely missing driver/direct contribution"
        basis = "a total/combined SPL observable is materially closer than the mouth SPL observable"
    elif best_scalar is not None and best_scalar["low_frequency_mean_abs_db"] <= 6.0 and best_scalar["full_mean_abs_db"] <= 12.0:
        classification = "likely_radiation_reference_distance_convention_issue"
        label = "likely radiation/reference-distance convention issue"
        basis = "a bounded 2pi/reference-distance scalar diagnostic transform materially reduces the residual"
    elif best_adjusted["low_frequency_mean_abs_db"] <= 4.0 and best_adjusted["full_mean_abs_db"] <= 10.0:
        classification = "mostly_constant_level_scaling"
        label = "mostly constant level scaling"
        basis = "the best low-frequency mean-offset adjustment leaves a small low-frequency and full-band residual"
    elif best_adjusted["low_frequency_mean_abs_db"] <= 6.0 and best_adjusted["full_mean_abs_db"] > 10.0:
        classification = "likely_coherent_summation_phase_convention_issue"
        label = "likely coherent summation / phase convention issue"
        basis = (
            "low-frequency mean-offset residual improves, but full-band residual remains large; current result "
            "fields do not expose complex pressure/phase candidates for direct confirmation"
        )

    return {
        "classification": classification,
        "classification_label": label,
        "basis": basis,
        "best_raw_candidate": best_raw,
        "best_offset_adjusted_candidate": best_adjusted,
        "best_scalar_check": best_scalar,
        "raw_candidate_ranking_by_low_frequency_mae": raw_ranked,
        "offset_adjusted_candidate_ranking_by_low_frequency_mae": adjusted_ranked,
    }


def evaluate_gdn13_offset_tqwt_spl_observation_convention_matrix(
    *,
    hornresp_definition_path: str | Path,
    hornresp_response_path: str | Path,
    profile: str = "parabolic",
) -> dict[str, Any]:
    """Evaluate a bounded SPL observation-convention diagnostic matrix."""

    definition_sections = parse_hornresp_definition_sections(hornresp_definition_path)
    traditional = definition_sections.get("traditional_driver", {})
    absorbent = definition_sections.get("absorbent", {})
    if float(traditional.get("Le", -1.0)) != 1.0:
        raise ValueError("expected latest GDN13 fixture with traditional Le = 1.00 mH")
    if float(absorbent.get("Tal1", -1.0)) != 0.0 or float(absorbent.get("Tal2", -1.0)) != 0.0:
        raise ValueError("expected latest GDN13 fixture with Tal1 = Tal2 = 0")

    hornresp = load_hornresp_gdn13_response_table(hornresp_response_path)
    frequency_hz = np.asarray(hornresp["frequency_hz"], dtype=float)
    hornresp_spl_db = np.asarray(hornresp["spl_db"], dtype=float)
    low_mask = frequency_hz <= LOW_FREQUENCY_LIMIT_HZ
    if int(np.count_nonzero(low_mask)) < 10:
        raise RuntimeError("too few low-frequency rows for SPL observation diagnostics")

    base_model = build_gdn13_offset_tqwt_model_dict(profile=profile)
    diagnostic_model = _append_front_spl_diagnostic_observation(base_model)
    result = run_simulation(diagnostic_model, frequency_hz)

    if np.asarray(result.frequencies_hz, dtype=float).shape != frequency_hz.shape:
        raise RuntimeError("os-lem frequency vector shape does not match HornResp table")

    candidates = _extract_spl_candidates(result, frequency_hz)
    if not candidates:
        raise RuntimeError("no usable SPL observations were exposed by os-lem for the GDN13 diagnostic matrix")

    candidate_matrices: dict[str, Any] = {}
    for candidate_id, candidate_spl in candidates.items():
        candidate_matrices[candidate_id] = {
            "candidate_id": candidate_id,
            "candidate_role": _candidate_role(candidate_id),
            **_comparison_summary(
                candidate_spl_db=candidate_spl,
                hornresp_spl_db=hornresp_spl_db,
                low_mask=low_mask,
            ),
        }

    classification = _classify_mismatch(candidate_matrices)

    return {
        "task": "test/v0.8.0-gdn13-offset-tqwt-spl-observation-convention-matrix",
        "base_mapping_trial": "test/v0.8.0-gdn13-offset-tqwt-hornresp-mapping-trial",
        "diagnostic_scope": "SPL observation-convention matrix only; no SPL repair",
        "fixture_files": {
            "hornresp_definition": str(Path(hornresp_definition_path)),
            "hornresp_response": str(Path(hornresp_response_path)),
        },
        "hornresp_authority_column": "SPL column from gdn13tl.txt",
        "frequency_count": int(frequency_hz.size),
        "frequency_span_hz": [float(frequency_hz[0]), float(frequency_hz[-1])],
        "low_frequency_limit_hz": float(LOW_FREQUENCY_LIMIT_HZ),
        "low_frequency_count": int(np.count_nonzero(low_mask)),
        "model_construction_path": "build_gdn13_offset_tqwt_model_dict(profile='parabolic') plus one diagnostic front SPL observation",
        "solver_call_path": "os_lem.api.run_simulation(diagnostic_model_dict, frequency_hz)",
        "inspected_spl_observables": list(candidate_matrices.keys()),
        "candidate_count": len(candidate_matrices),
        "candidate_matrix": candidate_matrices,
        "diagnostic_transforms_applied": {
            "raw_comparison": "candidate SPL minus HornResp SPL",
            "constant_offset_adjusted": "best-fit mean level offset over low-frequency rows <= 600 Hz",
            "scalar_checks": [
                {"name": name, "offset_db_added_to_oslem_candidate": float(offset)}
                for name, offset in SCALAR_DIAGNOSTIC_OFFSETS_DB
            ],
        },
        "phase_or_coherent_summation_diagnostic": {
            "available_from_current_result_fields": False,
            "interpretation": (
                "current run_simulation result fields for this model expose scalar SPL arrays in result.series; "
                "they do not expose complex pressure/phase arrays needed to build new coherent phase/sign variants "
                "without changing solver behavior"
            ),
            "existing_named_combined_observables_are_listed_as_candidates": any(
                "total" in candidate_id.lower() or "sum" in candidate_id.lower()
                for candidate_id in candidate_matrices
            ),
        },
        "best_candidate_summary": classification,
        "classification": classification["classification"],
        "classification_label": classification["classification_label"],
        "classification_basis": classification["basis"],
        "no_spl_repair_made": True,
        "non_claims": [
            "this does not establish SPL parity",
            "this does not establish full HornResp/Akabak replacement",
            "this does not implement a general HornResp importer",
            "this does not authorize optimizer physical claims",
            "this does not alter topology or solver semantics",
            "this does not open resonator work",
        ],
        "scope_guards": [
            "diagnostic matrix only",
            "no SPL repair",
            "no solver-core behavior change",
            "no topology change",
            "no general HornResp importer",
            "no optimizer implementation",
            "no Studio work",
        ],
    }
