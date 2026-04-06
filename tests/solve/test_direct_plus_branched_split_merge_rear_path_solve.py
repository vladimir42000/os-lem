from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.solve import solve_frequency_point


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "direct_plus_branched_split_merge_rear_path_demo", "radiation_space": "2pi"},
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
            "node_rear": "rear",
        },
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "flanged_piston",
                "area": "132 cm2",
            },
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "junction",
                "length": "20 cm",
                "area_start": "82 cm2",
                "area_end": "88 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "direct_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_direct",
                "length": "34 cm",
                "area_start": "88 cm2",
                "area_end": "96 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "split_feed",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "split",
                "length": "18 cm",
                "area_start": "44 cm2",
                "area_end": "50 cm2",
                "profile": "conical",
                "segments": 3,
            },
            {
                "id": "merge_main",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "26 cm",
                "area_start": "50 cm2",
                "area_end": "58 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "merge_aux",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "31 cm",
                "area_start": "42 cm2",
                "area_end": "47 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "shared_exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "rear_mouth_merged",
                "length": "22 cm",
                "area_start": "58 cm2",
                "area_end": "62 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_direct_rad",
                "type": "radiator",
                "node": "rear_mouth_direct",
                "model": "flanged_piston",
                "area": "96 cm2",
            },
            {
                "id": "rear_merged_rad",
                "type": "radiator",
                "node": "rear_mouth_merged",
                "model": "flanged_piston",
                "area": "62 cm2",
            },
        ],
        "observations": [],
    }


def test_solve_frequency_point_supports_direct_plus_branched_split_merge_rear_path_skeleton() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 160.0)

    assert len(system.direct_plus_branched_split_merge_rear_path_skeletons) == 1
    assert solved.node_order == (
        "front",
        "rear",
        "junction",
        "rear_mouth_direct",
        "split",
        "merge",
        "rear_mouth_merged",
    )
    assert solved.pressures.shape == (7,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    stem_to_junction = -solved.waveguide_endpoint_flow["stem"].node_b
    direct_from_junction = solved.waveguide_endpoint_flow["direct_leg"].node_a
    feed_from_junction = solved.waveguide_endpoint_flow["split_feed"].node_a
    feed_to_split = -solved.waveguide_endpoint_flow["split_feed"].node_b
    main_from_split = solved.waveguide_endpoint_flow["merge_main"].node_a
    aux_from_split = solved.waveguide_endpoint_flow["merge_aux"].node_a
    main_into_merge = -solved.waveguide_endpoint_flow["merge_main"].node_b
    aux_into_merge = -solved.waveguide_endpoint_flow["merge_aux"].node_b
    exit_from_merge = solved.waveguide_endpoint_flow["shared_exit"].node_a

    np.testing.assert_allclose(
        stem_to_junction,
        direct_from_junction + feed_from_junction,
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        feed_to_split,
        main_from_split + aux_from_split,
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        exit_from_merge,
        main_into_merge + aux_into_merge,
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(direct_from_junction, feed_from_junction)
