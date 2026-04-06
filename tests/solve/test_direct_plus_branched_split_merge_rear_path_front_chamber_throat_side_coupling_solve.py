from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.solve import solve_frequency_point


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_demo", "radiation_space": "2pi"},
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
            {"id": "front_rad", "type": "radiator", "node": "front", "model": "flanged_piston", "area": "132 cm2"},
            {"id": "front_chamber", "type": "volume", "node": "front", "value": "0.55 l"},
            {"id": "stem", "type": "waveguide_1d", "node_a": "rear", "node_b": "junction", "length": "20 cm", "area_start": "82 cm2", "area_end": "88 cm2", "profile": "conical", "segments": 4},
            {"id": "direct_leg", "type": "waveguide_1d", "node_a": "junction", "node_b": "rear_mouth_direct", "length": "34 cm", "area_start": "88 cm2", "area_end": "96 cm2", "profile": "conical", "segments": 5},
            {"id": "throat_feed_up", "type": "waveguide_1d", "node_a": "junction", "node_b": "throat_side", "length": "14 cm", "area_start": "46 cm2", "area_end": "52 cm2", "profile": "conical", "segments": 3},
            {"id": "throat_feed_down", "type": "waveguide_1d", "node_a": "throat_side", "node_b": "split", "length": "12 cm", "area_start": "52 cm2", "area_end": "50 cm2", "profile": "conical", "segments": 3},
            {"id": "front_coupling", "type": "waveguide_1d", "node_a": "front", "node_b": "throat_side", "length": "6 cm", "area_start": "18 cm2", "area_end": "20 cm2", "profile": "conical", "segments": 2},
            {"id": "merge_main", "type": "waveguide_1d", "node_a": "split", "node_b": "merge", "length": "26 cm", "area_start": "50 cm2", "area_end": "58 cm2", "profile": "conical", "segments": 4},
            {"id": "merge_aux", "type": "waveguide_1d", "node_a": "split", "node_b": "merge", "length": "31 cm", "area_start": "42 cm2", "area_end": "47 cm2", "profile": "conical", "segments": 4},
            {"id": "shared_exit", "type": "waveguide_1d", "node_a": "merge", "node_b": "rear_mouth_merged", "length": "22 cm", "area_start": "58 cm2", "area_end": "62 cm2", "profile": "conical", "segments": 4},
            {"id": "rear_direct_rad", "type": "radiator", "node": "rear_mouth_direct", "model": "flanged_piston", "area": "96 cm2"},
            {"id": "rear_merged_rad", "type": "radiator", "node": "rear_mouth_merged", "model": "flanged_piston", "area": "62 cm2"},
        ],
        "observations": [],
    }


def test_solve_frequency_point_supports_direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_skeleton() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 170.0)

    assert len(system.direct_plus_branched_split_merge_rear_path_front_chamber_throat_side_coupling_skeletons) == 1
    assert solved.node_order == (
        "front",
        "rear",
        "junction",
        "rear_mouth_direct",
        "throat_side",
        "split",
        "merge",
        "rear_mouth_merged",
    )
    assert solved.pressures.shape == (8,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    stem_to_junction = -solved.waveguide_endpoint_flow["stem"].node_b
    direct_from_junction = solved.waveguide_endpoint_flow["direct_leg"].node_a
    throat_up_from_junction = solved.waveguide_endpoint_flow["throat_feed_up"].node_a
    throat_up_into_side = -solved.waveguide_endpoint_flow["throat_feed_up"].node_b
    front_into_side = -solved.waveguide_endpoint_flow["front_coupling"].node_b
    throat_down_from_side = solved.waveguide_endpoint_flow["throat_feed_down"].node_a
    throat_down_into_split = -solved.waveguide_endpoint_flow["throat_feed_down"].node_b
    main_from_split = solved.waveguide_endpoint_flow["merge_main"].node_a
    aux_from_split = solved.waveguide_endpoint_flow["merge_aux"].node_a
    main_into_merge = -solved.waveguide_endpoint_flow["merge_main"].node_b
    aux_into_merge = -solved.waveguide_endpoint_flow["merge_aux"].node_b
    exit_from_merge = solved.waveguide_endpoint_flow["shared_exit"].node_a

    np.testing.assert_allclose(stem_to_junction, direct_from_junction + throat_up_from_junction, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(throat_down_from_side, throat_up_into_side + front_into_side, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(throat_down_into_split, main_from_split + aux_from_split, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(exit_from_merge, main_into_merge + aux_into_merge, rtol=1e-10, atol=1e-12)

    front_index = solved.node_order.index("front")
    throat_side_index = solved.node_order.index("throat_side")
    assert not np.isclose(solved.pressures[front_index], solved.pressures[throat_side_index])
    assert not np.allclose(main_from_split, aux_from_split)
