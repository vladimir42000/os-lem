from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.solve import solve_frequency_point


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "direct_plus_split_merge_rear_path_demo", "radiation_space": "2pi"},
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
                "node_b": "split",
                "length": "22 cm",
                "area_start": "85 cm2",
                "area_end": "90 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "leg_main",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "40 cm",
                "area_start": "90 cm2",
                "area_end": "105 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "leg_aux",
                "type": "waveguide_1d",
                "node_a": "split",
                "node_b": "merge",
                "length": "28 cm",
                "area_start": "55 cm2",
                "area_end": "65 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "shared_exit",
                "type": "waveguide_1d",
                "node_a": "merge",
                "node_b": "rear_mouth",
                "length": "34 cm",
                "area_start": "105 cm2",
                "area_end": "108 cm2",
                "profile": "conical",
                "segments": 5,
            },
            {
                "id": "rear_mouth_rad",
                "type": "radiator",
                "node": "rear_mouth",
                "model": "flanged_piston",
                "area": "108 cm2",
            },
        ],
        "observations": [],
    }


def test_solve_frequency_point_supports_direct_plus_split_merge_rear_path_skeleton() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 150.0)

    assert len(system.direct_plus_split_merge_rear_path_skeletons) == 1
    assert solved.node_order == ("front", "rear", "split", "merge", "rear_mouth")
    assert solved.pressures.shape == (5,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    stem_to_split = -solved.waveguide_endpoint_flow["stem"].node_b
    main_from_split = solved.waveguide_endpoint_flow["leg_main"].node_a
    aux_from_split = solved.waveguide_endpoint_flow["leg_aux"].node_a
    main_into_merge = -solved.waveguide_endpoint_flow["leg_main"].node_b
    aux_into_merge = -solved.waveguide_endpoint_flow["leg_aux"].node_b
    exit_from_merge = solved.waveguide_endpoint_flow["shared_exit"].node_a

    np.testing.assert_allclose(
        stem_to_split,
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
    assert not np.allclose(main_from_split, aux_from_split)
