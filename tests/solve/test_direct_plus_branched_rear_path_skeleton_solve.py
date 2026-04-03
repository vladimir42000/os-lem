from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import normalize_model
from os_lem.solve import solve_frequency_point


def _model_dict() -> dict[str, object]:
    return {
        "meta": {"name": "direct_plus_branched_rear_path_demo", "radiation_space": "2pi"},
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
                "length": "30 cm",
                "area_start": "90 cm2",
                "area_end": "95 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_main_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_main",
                "length": "45 cm",
                "area_start": "95 cm2",
                "area_end": "110 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "rear_aux_leg",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "rear_mouth_aux",
                "length": "26 cm",
                "area_start": "40 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "rear_main_rad",
                "type": "radiator",
                "node": "rear_mouth_main",
                "model": "flanged_piston",
                "area": "110 cm2",
            },
            {
                "id": "rear_aux_rad",
                "type": "radiator",
                "node": "rear_mouth_aux",
                "model": "flanged_piston",
                "area": "55 cm2",
            },
        ],
        "observations": [],
    }


def test_solve_frequency_point_supports_direct_plus_branched_rear_path_skeleton() -> None:
    model, warnings = normalize_model(_model_dict())
    assert warnings == []
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 120.0)

    assert len(system.direct_plus_branched_rear_path_skeletons) == 1
    assert set(solved.node_order) == {"front", "rear", "junction", "rear_mouth_main", "rear_mouth_aux"}
    assert solved.pressures.shape == (5,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    stem_to_junction = -solved.waveguide_endpoint_flow["stem"].node_b
    main_from_junction = solved.waveguide_endpoint_flow["rear_main_leg"].node_a
    aux_from_junction = solved.waveguide_endpoint_flow["rear_aux_leg"].node_a

    np.testing.assert_allclose(
        stem_to_junction,
        main_from_junction + aux_from_junction,
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(main_from_junction, aux_from_junction)
