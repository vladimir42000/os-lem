from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.model import Driver, NormalizedModel, RadiatorElement, Waveguide1DElement
from os_lem.solve import solve_frequency_point


def _driver() -> Driver:
    return Driver(
        id="drv1",
        Re=6.0,
        Le=0.0,
        Bl=7.0,
        Mms=0.02,
        Cms=1.0e-3,
        Rms=1.0,
        Sd=0.013,
        node_front="front",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def _branched_horn_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="stem",
                node_a="rear",
                node_b="junction",
                length_m=0.30,
                area_start_m2=0.0090,
                area_end_m2=0.0095,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="main_branch",
                node_a="junction",
                node_b="mouth_main",
                length_m=0.45,
                area_start_m2=0.0095,
                area_end_m2=0.0110,
                profile="conical",
                segments=6,
            ),
            Waveguide1DElement(
                id="tap_branch",
                node_a="junction",
                node_b="mouth_tap",
                length_m=0.26,
                area_start_m2=0.0040,
                area_end_m2=0.0055,
                profile="conical",
                segments=4,
            ),
        ],
        radiators=[
            RadiatorElement(id="front_rad", node="front", model="flanged_piston", area_m2=0.0132),
            RadiatorElement(id="main_rad", node="mouth_main", model="flanged_piston", area_m2=0.0110),
            RadiatorElement(id="tap_rad", node="mouth_tap", model="flanged_piston", area_m2=0.0055),
        ],
        node_order=["front", "rear", "junction", "mouth_main", "mouth_tap"],
    )


def test_solve_frequency_point_supports_minimal_branched_horn_skeleton() -> None:
    model = _branched_horn_model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 120.0)

    assert len(system.branched_horn_skeletons) == 1
    assert solved.node_order == ("front", "rear", "junction", "mouth_main", "mouth_tap")
    assert solved.pressures.shape == (5,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    stem_to_junction = -solved.waveguide_endpoint_flow["stem"].node_b
    main_from_junction = solved.waveguide_endpoint_flow["main_branch"].node_a
    tap_from_junction = solved.waveguide_endpoint_flow["tap_branch"].node_a

    np.testing.assert_allclose(
        stem_to_junction,
        main_from_junction + tap_from_junction,
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(main_from_junction, tap_from_junction)
