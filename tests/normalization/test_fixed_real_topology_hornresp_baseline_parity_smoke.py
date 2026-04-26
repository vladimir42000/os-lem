from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from os_lem.api import run_simulation
from os_lem.fixed_real_topology_normalization_adapter import (
    example_authored_offset_line_tqwt_input,
    normalize_fixed_real_topology_authored_input,
)

_REFERENCE = Path(__file__).resolve().parents[1] / "reference_data" / "hornresp_fixed_real_topology_baseline" / "HORNRESP_BASELINE_PARITY.json"


def _fmt_m(value: float) -> str:
    return f"{value:.6g} m"


def _fmt_m2(value: float) -> str:
    return f"{value:.6g} m2"


def _packet_to_model_dict(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Bounded packet -> model_dict helper for this HornResp parity smoke only.

    This deliberately mirrors the already-landed baseline-reproduction smoke
    construction without opening broad importer or topology semantics.
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
            "name": "fixed_real_topology_hornresp_baseline_parity_smoke",
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


def _load_hornresp_authority() -> dict[str, Any]:
    with _REFERENCE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_fixed_real_topology_adapter_solver_hornresp_baseline_parity_smoke() -> None:
    hornresp = _load_hornresp_authority()
    frequencies_hz = np.asarray(hornresp["frequency_hz"], dtype=float)
    hornresp_spl_total_db = np.asarray(hornresp["spl_total_db"], dtype=float)
    smoke_max_abs_spl_db = float(hornresp["smoke_grade_thresholds"]["max_abs_spl_db"])

    authored = example_authored_offset_line_tqwt_input()
    packet = normalize_fixed_real_topology_authored_input(authored)
    model_dict = _packet_to_model_dict(packet)

    result_a = run_simulation(model_dict, frequencies_hz)
    result_b = run_simulation(model_dict, frequencies_hz)

    solver_spl_a = np.asarray(result_a.series["spl_total"], dtype=float)
    solver_spl_b = np.asarray(result_b.series["spl_total"], dtype=float)

    assert hornresp["authority"]["name"] == "HornResp bounded fixed-real-topology baseline parity smoke fixture v1"
    assert result_a.frequencies_hz.shape == frequencies_hz.shape
    assert solver_spl_a.shape == frequencies_hz.shape
    assert hornresp_spl_total_db.shape == frequencies_hz.shape

    assert np.all(np.isfinite(result_a.frequencies_hz))
    assert np.all(np.isfinite(solver_spl_a))
    assert np.all(np.isfinite(hornresp_spl_total_db))
    assert not np.allclose(solver_spl_a, 0.0, atol=1.0e-9)

    np.testing.assert_allclose(result_a.frequencies_hz, frequencies_hz, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(solver_spl_a, solver_spl_b, rtol=1.0e-12, atol=1.0e-12)

    max_abs_spl_db = float(np.max(np.abs(solver_spl_a - hornresp_spl_total_db)))
    assert max_abs_spl_db <= smoke_max_abs_spl_db
