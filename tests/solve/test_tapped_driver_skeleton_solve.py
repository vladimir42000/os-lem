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
        node_front="merge",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def _tapped_driver_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="stem",
                node_a="rear",
                node_b="split",
                length_m=0.22,
                area_start_m2=0.0085,
                area_end_m2=0.0090,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="leg_main",
                node_a="split",
                node_b="merge",
                length_m=0.40,
                area_start_m2=0.0090,
                area_end_m2=0.0105,
                profile="conical",
                segments=5,
            ),
            Waveguide1DElement(
                id="leg_tap",
                node_a="split",
                node_b="merge",
                length_m=0.28,
                area_start_m2=0.0055,
                area_end_m2=0.0065,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="exit",
                node_a="merge",
                node_b="mouth",
                length_m=0.34,
                area_start_m2=0.0105,
                area_end_m2=0.0108,
                profile="conical",
                segments=5,
            ),
        ],
        radiators=[
            RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0108),
        ],
        node_order=["rear", "split", "merge", "mouth"],
    )


def test_solve_frequency_point_supports_tapped_driver_skeleton() -> None:
    model = _tapped_driver_model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 150.0)

    assert len(system.tapped_driver_skeletons) == 1
    assert solved.node_order == ("rear", "split", "merge", "mouth")
    assert solved.pressures.shape == (4,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    stem_to_split = -solved.waveguide_endpoint_flow["stem"].node_b
    main_from_split = solved.waveguide_endpoint_flow["leg_main"].node_a
    tap_from_split = solved.waveguide_endpoint_flow["leg_tap"].node_a
    main_into_merge = -solved.waveguide_endpoint_flow["leg_main"].node_b
    tap_into_merge = -solved.waveguide_endpoint_flow["leg_tap"].node_b
    exit_from_merge = solved.waveguide_endpoint_flow["exit"].node_a
    front_injection = model.driver.Sd * solved.cone_velocity

    np.testing.assert_allclose(stem_to_split, main_from_split + tap_from_split, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(
        exit_from_merge,
        main_into_merge + tap_into_merge + front_injection,
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(main_from_split, tap_from_split)
    assert abs(front_injection) > 0.0
