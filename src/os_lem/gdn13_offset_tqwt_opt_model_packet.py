"""OPT-consumable normalized model packet for the GDN13 offset TQWT case.

This module exposes exactly one os-lem-owned export surface for the accepted
GDN13 offset-driver TQWT baseline model construction. It is intentionally a
narrow interface artifact: OPT can consume the returned solver-facing model_dict
and parity metadata without rebuilding normalization, model construction,
source/radiation convention, or SPL interpretation locally.

Scope guard:
- one GDN13 offset TQWT baseline only
- accepted low-frequency parity gate must pass before packet_status is passed
- SPL observable is spl_total_diagnostic
- mouth-only SPL and full-band SPL parity are explicit non-claims
- no optimizer implementation, fallback normalization, resonator semantics, or
  solver/topology behavior change
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from os_lem.gdn13_offset_tqwt_opt_parity_gate import (
    get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt,
)
from os_lem.reference_gdn13_offset_tqwt_mapping_trial import (
    build_gdn13_offset_tqwt_model_dict,
)


CASE_ID = "gdn13_offset_tqwt"
EXPORT_COMMIT_REQUIREMENT = "d2e429c"
CALLABLE_PATH = "os_lem.gdn13_offset_tqwt_opt_model_packet.get_gdn13_offset_tqwt_normalized_model_packet_for_opt"
PARITY_CALLABLE_PATH = "os_lem.gdn13_offset_tqwt_opt_parity_gate.get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt"
MODEL_BUILDER_PATH = "os_lem.reference_gdn13_offset_tqwt_mapping_trial.build_gdn13_offset_tqwt_model_dict(profile='parabolic')"
SOLVER_CALLABLE_PATH = "os_lem.api.run_simulation"


def _gate_metric(gate: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in gate:
            return gate[name]
    return None


def _blocked_packet(*, gate: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "packet_status": "blocked",
        "case_id": CASE_ID,
        "kernel_commit_basis": gate.get("kernel_commit_basis", "64f8dbb"),
        "export_commit_requirement": EXPORT_COMMIT_REQUIREMENT,
        "model_dict": None,
        "frequencies_hz": list(gate.get("frequency_hz", [])),
        "solver_callable": SOLVER_CALLABLE_PATH,
        "parity_callable": PARITY_CALLABLE_PATH,
        "model_builder_path": MODEL_BUILDER_PATH,
        "spl_observable": gate.get("spl_observable"),
        "spl_reference": gate.get("spl_reference"),
        "impedance_observable": gate.get("impedance_observable"),
        "impedance_reference": gate.get("impedance_reference"),
        "parity_band": gate.get("spl_band_hz", {}).get("predicate", "frequency_hz <= 600.0"),
        "baseline_parity_gate_status": gate.get("optimizer_gate_status", "failed"),
        "spl_parity_passed": bool(gate.get("spl_parity_passed", False)),
        "impedance_parity_passed": bool(gate.get("impedance_parity_passed", False)),
        "spl_metric": _gate_metric(gate, "spl_mae_db", "spl_metric"),
        "spl_mae_db": _gate_metric(gate, "spl_mae_db", "spl_metric"),
        "spl_threshold": _gate_metric(gate, "spl_mae_threshold_db", "spl_threshold"),
        "impedance_metric": _gate_metric(gate, "ze_mae_ohm", "impedance_metric"),
        "ze_mae_ohm": _gate_metric(gate, "ze_mae_ohm", "impedance_metric"),
        "impedance_threshold": _gate_metric(gate, "ze_mae_threshold_ohm", "impedance_threshold"),
        "full_band_spl_claim": False,
        "mouth_only_spl_claim": False,
        "normalization_owner": "os-lem",
        "model_construction_owner": "os-lem",
        "packet_block_reason": reason,
        "gate_reason": gate.get("optimizer_gate_reason", reason),
        "limitations": list(gate.get("limitations", [])),
    }


def get_gdn13_offset_tqwt_normalized_model_packet_for_opt() -> dict[str, Any]:
    """Return the accepted GDN13 solver-facing model packet for OPT."""

    try:
        gate = get_gdn13_offset_tqwt_low_frequency_parity_gate_for_opt()
    except Exception as exc:  # pragma: no cover - defensive interface behavior
        return _blocked_packet(
            gate={
                "kernel_commit_basis": "64f8dbb",
                "optimizer_gate_status": "failed",
                "spl_parity_passed": False,
                "impedance_parity_passed": False,
                "spl_observable": "spl_total_diagnostic",
                "spl_reference": "HornResp SPL column",
                "impedance_observable": "abs(zin_complex_ohm)",
                "impedance_reference": "HornResp Ze column",
                "frequency_hz": [],
            },
            reason=f"accepted low-frequency parity gate unavailable: {exc}",
        )

    parity_passed = (
        gate.get("optimizer_gate_status") == "passed"
        and gate.get("spl_parity_passed") is True
        and gate.get("impedance_parity_passed") is True
        and gate.get("spl_observable") == "spl_total_diagnostic"
        and gate.get("full_band_spl_claim") is False
        and gate.get("mouth_only_spl_claim") is False
    )
    if not parity_passed:
        return _blocked_packet(
            gate=gate,
            reason="accepted low-frequency parity gate did not pass with the required SPL/impedance/non-claim surface",
        )

    model_dict = build_gdn13_offset_tqwt_model_dict(profile="parabolic")
    frequencies_hz = list(gate.get("frequency_hz", []))
    if not frequencies_hz:
        return _blocked_packet(
            gate=gate,
            reason="accepted low-frequency parity gate did not expose a frequency grid",
        )

    return {
        "packet_status": "passed",
        "case_id": CASE_ID,
        "kernel_commit_basis": gate.get("kernel_commit_basis", "64f8dbb"),
        "export_commit_requirement": EXPORT_COMMIT_REQUIREMENT,
        "callable_path": CALLABLE_PATH,
        "model_dict": deepcopy(model_dict),
        "frequencies_hz": [float(v) for v in frequencies_hz],
        "solver_callable": SOLVER_CALLABLE_PATH,
        "parity_callable": PARITY_CALLABLE_PATH,
        "model_builder_path": MODEL_BUILDER_PATH,
        "spl_observable": "spl_total_diagnostic",
        "spl_reference": gate.get("spl_reference", "HornResp SPL column"),
        "impedance_observable": gate.get("impedance_observable", "abs(zin_complex_ohm)"),
        "impedance_reference": gate.get("impedance_reference", "HornResp Ze column"),
        "parity_band": gate.get("spl_band_hz", {}).get("predicate", "frequency_hz <= 600.0"),
        "spl_band_hz": deepcopy(gate.get("spl_band_hz")),
        "impedance_band_hz": deepcopy(gate.get("impedance_band_hz")),
        "baseline_parity_gate_status": gate.get("optimizer_gate_status"),
        "baseline_parity_gate_reason": gate.get("optimizer_gate_reason"),
        "spl_parity_passed": bool(gate.get("spl_parity_passed")),
        "impedance_parity_passed": bool(gate.get("impedance_parity_passed")),
        "spl_metric": gate.get("spl_mae_db"),
        "spl_mae_db": gate.get("spl_mae_db"),
        "spl_rms_db": gate.get("spl_rms_db"),
        "spl_max_abs_db": gate.get("spl_max_abs_db"),
        "spl_threshold": gate.get("spl_mae_threshold_db"),
        "spl_rms_threshold_db": gate.get("spl_rms_threshold_db"),
        "impedance_metric": gate.get("ze_mae_ohm"),
        "ze_mae_ohm": gate.get("ze_mae_ohm"),
        "ze_rms_ohm": gate.get("ze_rms_ohm"),
        "ze_max_abs_ohm": gate.get("ze_max_abs_ohm"),
        "impedance_threshold": gate.get("ze_mae_threshold_ohm"),
        "ze_rms_threshold_ohm": gate.get("ze_rms_threshold_ohm"),
        "full_band_spl_claim": False,
        "mouth_only_spl_claim": False,
        "mouth_only_rejected_observable": gate.get("mouth_only_rejected_observable", "spl_mouth"),
        "normalization_owner": "os-lem",
        "model_construction_owner": "os-lem",
        "normalization_source": "accepted os-lem GDN13 builder and low-frequency parity gate",
        "model_construction_source": MODEL_BUILDER_PATH,
        "limitations": list(gate.get("limitations", [])) + [
            "model packet is for the accepted GDN13 offset TQWT baseline only",
            "OPT must not reinterpret SPL, source/radiation convention, or model construction locally",
            "no resonator semantics are included in this packet",
        ],
    }


def export_gdn13_offset_tqwt_normalized_model_packet_for_opt() -> dict[str, Any]:
    """Alias with explicit export wording for OPT-facing consumers."""

    return get_gdn13_offset_tqwt_normalized_model_packet_for_opt()
