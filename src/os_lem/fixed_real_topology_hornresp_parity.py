"""Bounded v0.8.0 fixed real-topology HornResp parity callable.

This module promotes the accepted HornResp baseline parity smoke path from
purely test-owned logic into one narrow kernel-owned callable gate.  It is
intentionally limited to the frozen fixed real-topology packet contract and the
accepted bounded HornResp fixture surface.

Non-goals:
- no broad HornResp importer
- no arbitrary topology import or mutation
- no optimizer implementation
- no continuous source-position semantics
- no multiple resonator-slot semantics
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from os_lem.api import run_simulation
from os_lem.fixed_real_topology_normalization_adapter import (
    example_authored_offset_line_tqwt_input,
    normalize_fixed_real_topology_authored_input,
)

DEFAULT_HORNRESP_BASELINE_PARITY_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "reference_data"
    / "hornresp_fixed_real_topology_baseline"
    / "HORNRESP_BASELINE_PARITY.json"
)


def _fmt_m(value: float) -> str:
    return f"{value:.6g} m"


def _fmt_m2(value: float) -> str:
    return f"{value:.6g} m2"


def fixed_real_topology_packet_to_model_dict(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Convert the fixed v0.8.0 packet into one bounded solver model_dict.

    This helper is deliberately narrow.  It supports only the accepted fixed
    offset-line / TQWT-family packet shape and the current segmented 1D kernel
    discipline.  It is not a broad topology importer.
    """

    geometry = packet["geometry"]
    source_slot = packet["source"]["slot"]
    slot_to_node = {
        "rear_slot": "rear",
        "throat_slot": "closed_end",
        "bend_slot": "bend",
    }
    source_node = slot_to_node[source_slot]

    elements: list[dict[str, Any]] = [
        {
            "id": "front_rad",
            "type": "radiator",
            "node": "front",
            "model": "infinite_baffle_piston",
            "area": "132 cm2",
        },
        {
            "id": "throat_chamber",
            "type": "waveguide_1d",
            "node_a": "closed_end",
            "node_b": "rear",
            "length": _fmt_m(geometry["throat_chamber"]["length_m"]),
            "area_start": _fmt_m2(geometry["throat_chamber"]["area_in_m2"]),
            "area_end": _fmt_m2(geometry["throat_chamber"]["area_out_m2"]),
            "profile": geometry["throat_chamber"]["profile"],
            "segments": 6,
        },
        {
            "id": "horn_seg1",
            "type": "waveguide_1d",
            "node_a": "rear",
            "node_b": "bend",
            "length": _fmt_m(geometry["horn_seg1"]["length_m"]),
            "area_start": _fmt_m2(geometry["horn_seg1"]["area_in_m2"]),
            "area_end": _fmt_m2(geometry["horn_seg1"]["area_out_m2"]),
            "profile": geometry["horn_seg1"]["profile"],
            "segments": 8,
        },
        {
            "id": "horn_seg2",
            "type": "waveguide_1d",
            "node_a": "bend",
            "node_b": "mouth",
            "length": _fmt_m(geometry["horn_seg2"]["length_m"]),
            "area_start": _fmt_m2(geometry["horn_seg2"]["area_in_m2"]),
            "area_end": _fmt_m2(geometry["horn_seg2"]["area_out_m2"]),
            "profile": geometry["horn_seg2"]["profile"],
            "segments": 8,
        },
        {
            "id": "mouth_rad",
            "type": "radiator",
            "node": "mouth",
            "model": "unflanged_piston",
            "area": _fmt_m2(geometry["horn_seg2"]["area_out_m2"]),
        },
    ]

    resonator = geometry["resonator"]
    if resonator["present"]:
        attach_node = slot_to_node[resonator["slot"]]
        payload = resonator["payload"]
        elements.append(
            {
                "id": "resonator_side_pipe",
                "type": "waveguide_1d",
                "node_a": attach_node,
                "node_b": "resonator_closed_end",
                "length": _fmt_m(payload["length_m"]),
                "area_start": _fmt_m2(payload["area_m2"]),
                "area_end": _fmt_m2(payload["area_m2"]),
                "profile": "conical",
                "segments": 4,
            }
        )

    return {
        "meta": {
            "name": "fixed_real_topology_hornresp_baseline_parity_callable",
            "radiation_space": "2pi",
        },
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "front",
            "node_rear": source_node,
        },
        "elements": elements,
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {
                "id": "spl_total",
                "type": "spl_sum",
                "radiation_space": "2pi",
                "terms": [
                    {"target": "front_rad", "distance": "1 m"},
                    {"target": "mouth_rad", "distance": "1 m"},
                ],
            },
            {
                "id": "spl_mouth",
                "type": "spl",
                "target": "mouth_rad",
                "distance": "1 m",
                "radiation_space": "2pi",
            },
        ],
    }


def _load_hornresp_fixture(fixture_path: str | Path) -> dict[str, Any]:
    path = Path(fixture_path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _as_float_array(name: str, value: Sequence[Any]) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional sequence")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite values")
    return array


def evaluate_fixed_real_topology_hornresp_baseline_parity(
    authored_input: Mapping[str, Any] | None = None,
    *,
    hornresp_fixture_path: str | Path | None = None,
) -> dict[str, Any]:
    """Evaluate the bounded fixed-real-topology HornResp parity gate.

    The callable follows the accepted path:
    authored input -> fixed normalization packet -> model_dict ->
    os_lem.api.run_simulation(...) -> HornResp fixture comparison.

    It returns a simple dictionary so downstream consumers such as OPT can use
    the result without importing test modules or reconstructing parity logic.
    """

    if authored_input is None:
        authored_input = example_authored_offset_line_tqwt_input()
    fixture_path = Path(hornresp_fixture_path or DEFAULT_HORNRESP_BASELINE_PARITY_FIXTURE)
    hornresp = _load_hornresp_fixture(fixture_path)

    frequencies_hz = _as_float_array("frequency_hz", hornresp["frequency_hz"])
    hornresp_spl_total_db = _as_float_array("spl_total_db", hornresp["spl_total_db"])
    hornresp_impedance_mag_ohm = _as_float_array(
        "impedance_mag_ohm", hornresp["impedance_mag_ohm"]
    )

    thresholds = hornresp["smoke_grade_thresholds"]
    spl_threshold = float(thresholds["max_abs_spl_db"])
    impedance_threshold = float(thresholds["max_abs_impedance_mag_ohm"])

    packet = normalize_fixed_real_topology_authored_input(authored_input)
    model_dict = fixed_real_topology_packet_to_model_dict(packet)
    result = run_simulation(model_dict, frequencies_hz)

    solver_spl_total_db = np.asarray(result.series["spl_total"], dtype=float)
    if result.zin_complex_ohm is None:
        raise RuntimeError("solver did not provide zin_complex_ohm for parity evaluation")
    solver_impedance_mag_ohm = np.abs(np.asarray(result.zin_complex_ohm, dtype=complex))

    if result.frequencies_hz.shape != frequencies_hz.shape:
        raise RuntimeError("solver frequency output shape does not match HornResp fixture grid")
    if solver_spl_total_db.shape != frequencies_hz.shape:
        raise RuntimeError("solver SPL output shape does not match HornResp fixture grid")
    if solver_impedance_mag_ohm.shape != frequencies_hz.shape:
        raise RuntimeError("solver impedance output shape does not match HornResp fixture grid")

    if hornresp_spl_total_db.shape != frequencies_hz.shape:
        raise RuntimeError("HornResp SPL fixture shape does not match frequency grid")
    if hornresp_impedance_mag_ohm.shape != frequencies_hz.shape:
        raise RuntimeError("HornResp impedance fixture shape does not match frequency grid")

    if not np.all(np.isfinite(solver_spl_total_db)):
        raise RuntimeError("solver SPL output contains non-finite values")
    if not np.all(np.isfinite(solver_impedance_mag_ohm)):
        raise RuntimeError("solver impedance output contains non-finite values")

    spl_metric = float(np.max(np.abs(solver_spl_total_db - hornresp_spl_total_db)))
    impedance_metric = float(np.max(np.abs(solver_impedance_mag_ohm - hornresp_impedance_mag_ohm)))

    spl_parity_passed = spl_metric <= spl_threshold
    impedance_parity_passed = impedance_metric <= impedance_threshold
    gate_passed = spl_parity_passed and impedance_parity_passed

    if spl_parity_passed:
        spl_parity_reason = (
            f"SPL smoke-grade parity passed: max_abs_delta_db={spl_metric:.6g} "
            f"<= threshold_db={spl_threshold:.6g}."
        )
    else:
        spl_parity_reason = (
            f"SPL smoke-grade parity failed: max_abs_delta_db={spl_metric:.6g} "
            f"> threshold_db={spl_threshold:.6g}."
        )

    if impedance_parity_passed:
        impedance_parity_reason = (
            f"Impedance smoke-grade parity passed: max_abs_delta_ohm={impedance_metric:.6g} "
            f"<= threshold_ohm={impedance_threshold:.6g}."
        )
    else:
        impedance_parity_reason = (
            f"Impedance smoke-grade parity failed: max_abs_delta_ohm={impedance_metric:.6g} "
            f"> threshold_ohm={impedance_threshold:.6g}."
        )

    if gate_passed:
        parity_gate_reason = (
            "HornResp baseline parity gate passed under bounded smoke-grade thresholds."
        )
    else:
        parity_gate_reason = (
            "HornResp baseline parity gate failed under bounded smoke-grade thresholds; "
            "the callable blocks downstream OPT physical claims until parity is repaired."
        )

    return {
        "baseline_parity_gate_status": "passed" if gate_passed else "failed",
        "spl_parity_passed": spl_parity_passed,
        "impedance_parity_passed": impedance_parity_passed,
        "spl_metric": spl_metric,
        "spl_threshold": spl_threshold,
        "impedance_metric": impedance_metric,
        "impedance_threshold": impedance_threshold,
        "frequency_hz": [float(v) for v in frequencies_hz],
        "parity_gate_reason": parity_gate_reason,
        "spl_parity_reason": spl_parity_reason,
        "impedance_parity_reason": impedance_parity_reason,
    }
