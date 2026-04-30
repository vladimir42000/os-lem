"""OPT-consumable low-frequency parity gate for the GDN13 offset TQWT case.

This module exports exactly one bounded kernel-owned contract for the accepted
GDN13 offset-driver TQWT low-frequency HornResp comparison basis.  It reuses the
case-level mapping/alignment report and exposes the accepted parity meaning as a
machine-consumable dictionary.

Scope guard:
- one GDN13 offset TQWT case only
- low-frequency gate only, <= 600 Hz
- SPL basis is HornResp SPL column vs os-lem spl_total_diagnostic
- impedance basis is HornResp Ze column vs os-lem electrical impedance magnitude
- no full-band SPL parity claim
- no mouth-only SPL parity claim
- no optimizer implementation or solver/topology behavior change
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    LOW_FREQUENCY_LIMIT_HZ,
    PRIMARY_SPL_OBSERVABLE_ID,
    SECONDARY_MOUTH_SPL_OBSERVABLE_ID,
    evaluate_gdn13_offset_tqwt_mapping_trial,
    load_hornresp_gdn13_response_table,
)


CASE_ID = "gdn13_offset_tqwt"
KERNEL_COMMIT_BASIS = "64f8dbb"
SPL_REFERENCE = "HornResp SPL column from tests/reference_data/hornresp_gdn13_offset_tqwt/gdn13tl.txt"
IMPEDANCE_REFERENCE = "HornResp Ze column from tests/reference_data/hornresp_gdn13_offset_tqwt/gdn13tl.txt"
IMPEDANCE_OBSERVABLE = "abs(zin_complex_ohm) electrical impedance magnitude Ze"

# Bounded low-frequency smoke-grade thresholds tied to the accepted 64f8dbb
# reading. They intentionally do not create or imply any full-band SPL gate.
SPL_MAE_THRESHOLD_DB = 1.0
SPL_RMS_THRESHOLD_DB = 1.5
ZE_MAE_THRESHOLD_OHM = 1.0
ZE_RMS_THRESHOLD_OHM = 1.5


def _repo_root_from_module() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_fixture_dir() -> Path:
    return _repo_root_from_module() / "tests" / "reference_data" / "hornresp_gdn13_offset_tqwt"


def _default_definition_path() -> Path:
    return _default_fixture_dir() / "gdn13tHRl.txt"


def _default_response_path() -> Path:
    return _default_fixture_dir() / "gdn13tl.txt"


def _band_dict(frequency_hz: np.ndarray) -> dict[str, Any]:
    low_mask = frequency_hz <= LOW_FREQUENCY_LIMIT_HZ
    low_frequency = frequency_hz[low_mask]
    return {
        "scope": "low_frequency_only",
        "predicate": "frequency_hz <= 600.0",
        "min_hz": float(low_frequency[0]),
        "max_hz": float(low_frequency[-1]),
        "count": int(low_frequency.size),
    }


def get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt(
    *,
    hornresp_definition_path: str | Path | None = None,
    hornresp_response_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return the accepted GDN13 LF parity gate as a machine-consumable dict.

    Optional fixture paths exist only to let tests or a controlled caller point
    at the accepted fixture location explicitly.  The contract semantics remain
    fixed to this one GDN13 offset-driver TQWT case and to the accepted
    spl_total_diagnostic low-frequency observation basis.
    """

    definition_path = Path(hornresp_definition_path) if hornresp_definition_path is not None else _default_definition_path()
    response_path = Path(hornresp_response_path) if hornresp_response_path is not None else _default_response_path()

    report = evaluate_gdn13_offset_tqwt_mapping_trial(
        hornresp_definition_path=definition_path,
        hornresp_response_path=response_path,
        profile="parabolic",
    )
    hornresp = load_hornresp_gdn13_response_table(response_path)
    frequency_hz = np.asarray(hornresp["frequency_hz"], dtype=float)

    primary_spl = report["primary_spl_comparison"]
    impedance = report["impedance_comparison"]
    mouth_spl = report["secondary_spl_diagnostics"][SECONDARY_MOUTH_SPL_OBSERVABLE_ID]

    spl_low = primary_spl["low_frequency_le_600_hz"]
    ze_low = impedance["low_frequency_le_600_hz"]

    spl_observable_is_accepted = report.get("primary_spl_observable") == PRIMARY_SPL_OBSERVABLE_ID
    mouth_only_claim = False
    full_band_spl_claim = False

    spl_parity_passed = bool(
        spl_observable_is_accepted
        and spl_low["mean_abs"] <= SPL_MAE_THRESHOLD_DB
        and spl_low["rms"] <= SPL_RMS_THRESHOLD_DB
    )
    impedance_parity_passed = bool(
        ze_low["mean_abs"] <= ZE_MAE_THRESHOLD_OHM
        and ze_low["rms"] <= ZE_RMS_THRESHOLD_OHM
    )
    optimizer_gate_status = "passed" if (
        spl_parity_passed
        and impedance_parity_passed
        and not full_band_spl_claim
        and not mouth_only_claim
    ) else "failed"

    if optimizer_gate_status == "passed":
        gate_reason = (
            "passed: low-frequency SPL uses HornResp SPL vs os-lem spl_total_diagnostic; "
            "low-frequency impedance uses HornResp Ze vs os-lem electrical impedance magnitude; "
            "full-band SPL parity and mouth-only SPL parity are explicit non-claims"
        )
    else:
        failed_parts: list[str] = []
        if not spl_observable_is_accepted:
            failed_parts.append("SPL observable is not the accepted spl_total_diagnostic")
        if not spl_parity_passed:
            failed_parts.append("low-frequency SPL gate did not pass bounded thresholds")
        if not impedance_parity_passed:
            failed_parts.append("low-frequency impedance gate did not pass bounded thresholds")
        gate_reason = "failed: " + "; ".join(failed_parts)

    return {
        "case_id": CASE_ID,
        "kernel_commit_basis": KERNEL_COMMIT_BASIS,
        "contract_name": "EXPORT/gdn13-offset-tqwt-low-frequency-parity-gate-for-opt",
        "callable_path": "os_lem.gdn13_offset_tqwt_opt_parity_gate.get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt",
        "spl_reference": SPL_REFERENCE,
        "spl_observable": PRIMARY_SPL_OBSERVABLE_ID,
        "spl_band_hz": _band_dict(frequency_hz),
        "spl_parity_passed": spl_parity_passed,
        "spl_mae_db": float(spl_low["mean_abs"]),
        "spl_rms_db": float(spl_low["rms"]),
        "spl_max_abs_db": float(spl_low["max_abs"]),
        "spl_mae_threshold_db": SPL_MAE_THRESHOLD_DB,
        "spl_rms_threshold_db": SPL_RMS_THRESHOLD_DB,
        "impedance_reference": IMPEDANCE_REFERENCE,
        "impedance_observable": IMPEDANCE_OBSERVABLE,
        "impedance_band_hz": _band_dict(frequency_hz),
        "impedance_parity_passed": impedance_parity_passed,
        "ze_mae_ohm": float(ze_low["mean_abs"]),
        "ze_rms_ohm": float(ze_low["rms"]),
        "ze_max_abs_ohm": float(ze_low["max_abs"]),
        "ze_mae_threshold_ohm": ZE_MAE_THRESHOLD_OHM,
        "ze_rms_threshold_ohm": ZE_RMS_THRESHOLD_OHM,
        "frequency_hz": [float(v) for v in frequency_hz.tolist()],
        "optimizer_gate_status": optimizer_gate_status,
        "optimizer_gate_reason": gate_reason,
        "full_band_spl_claim": full_band_spl_claim,
        "mouth_only_spl_claim": mouth_only_claim,
        "mouth_only_rejected_observable": SECONDARY_MOUTH_SPL_OBSERVABLE_ID,
        "mouth_only_low_frequency_mae_db": float(mouth_spl["low_frequency_le_600_hz"]["mean_abs"]),
        "full_band_spl_metrics_visible": True,
        "full_band_spl_metrics": {
            "mae_db": float(primary_spl["full"]["mean_abs"]),
            "rms_db": float(primary_spl["full"]["rms"]),
            "max_abs_db": float(primary_spl["full"]["max_abs"]),
        },
        "limitations": [
            "low-frequency GDN13 offset TQWT parity gate only",
            "does not establish full-band SPL parity",
            "does not establish general HornResp parity",
            "does not establish full Akabak/HornResp replacement",
            "does not authorize optimizer physical claims outside this low-frequency gate",
            "does not implement optimizer repair or rerun",
            "does not alter solver or topology semantics",
            "does not open resonator work",
            "does not reopen Studio or public-promotion work",
            "mouth-only SPL is rejected as the comparison target for this case",
        ],
        "source_report_task": report.get("task"),
        "source_alignment_scope": report.get("alignment_scope"),
        "source_mapping_interpretation": report.get("mapping_trial_interpretation"),
    }


# Alias with explicit export wording for consumers that prefer the task name.
def export_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt(
    *,
    hornresp_definition_path: str | Path | None = None,
    hornresp_response_path: str | Path | None = None,
) -> dict[str, Any]:
    return get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt(
        hornresp_definition_path=hornresp_definition_path,
        hornresp_response_path=hornresp_response_path,
    )
