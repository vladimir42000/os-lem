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
        node_front="tap",
        node_rear="rear",
        source_voltage_rms=2.83,
    )



def _offset_tap_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="stem",
                node_a="rear",
                node_b="split",
                length_m=0.23,
                area_start_m2=0.0080,
                area_end_m2=0.0088,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="main_leg",
                node_a="split",
                node_b="merge",
                length_m=0.46,
                area_start_m2=0.0088,
                area_end_m2=0.0102,
                profile="conical",
                segments=6,
            ),
            Waveguide1DElement(
                id="tap_upstream",
                node_a="split",
                node_b="tap",
                length_m=0.18,
                area_start_m2=0.0052,
                area_end_m2=0.0055,
                profile="conical",
                segments=3,
            ),
            Waveguide1DElement(
                id="tap_downstream",
                node_a="tap",
                node_b="merge",
                length_m=0.16,
                area_start_m2=0.0055,
                area_end_m2=0.0062,
                profile="conical",
                segments=3,
            ),
            Waveguide1DElement(
                id="exit",
                node_a="merge",
                node_b="mouth",
                length_m=0.32,
                area_start_m2=0.0102,
                area_end_m2=0.0105,
                profile="conical",
                segments=5,
            ),
        ],
        radiators=[
            RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0105),
        ],
        node_order=["rear", "split", "tap", "merge", "mouth"],
    )



def test_solve_frequency_point_supports_offset_tap_topology() -> None:
    model = _offset_tap_model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 160.0)

    assert len(system.offset_tap_topologies) == 1
    assert solved.node_order == ("rear", "split", "tap", "merge", "mouth")
    assert solved.pressures.shape == (5,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    stem_to_split = -solved.waveguide_endpoint_flow["stem"].node_b
    main_from_split = solved.waveguide_endpoint_flow["main_leg"].node_a
    tap_up_from_split = solved.waveguide_endpoint_flow["tap_upstream"].node_a
    main_into_merge = -solved.waveguide_endpoint_flow["main_leg"].node_b
    tap_down_into_merge = -solved.waveguide_endpoint_flow["tap_downstream"].node_b
    exit_from_merge = solved.waveguide_endpoint_flow["exit"].node_a

    np.testing.assert_allclose(
        stem_to_split,
        main_from_split + tap_up_from_split,
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        exit_from_merge,
        main_into_merge + tap_down_into_merge,
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(main_from_split, tap_up_from_split)

    tap_index = solved.node_order.index("tap")
    merge_index = solved.node_order.index("merge")
    assert not np.isclose(solved.pressures[tap_index], solved.pressures[merge_index])
