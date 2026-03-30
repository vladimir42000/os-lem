from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.model import Driver, NormalizedModel, RadiatorElement, VolumeElement, Waveguide1DElement
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


def _blind_throat_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        volumes=[
            VolumeElement(id="rear_chamber", node="rear", value_m3=0.010),
            VolumeElement(id="throat_chamber", node="throat", value_m3=0.0016),
        ],
        waveguides=[
            Waveguide1DElement(
                id="rear_port",
                node_a="rear",
                node_b="inject",
                length_m=0.11,
                area_start_m2=0.0042,
                area_end_m2=0.0045,
                profile="conical",
                segments=2,
            ),
            Waveguide1DElement(
                id="throat_entry",
                node_a="inject",
                node_b="throat",
                length_m=0.08,
                area_start_m2=0.0045,
                area_end_m2=0.0048,
                profile="conical",
                segments=2,
            ),
            Waveguide1DElement(
                id="blind_segment",
                node_a="throat",
                node_b="blind",
                length_m=0.12,
                area_start_m2=0.0048,
                area_end_m2=0.0042,
                profile="conical",
                segments=2,
            ),
            Waveguide1DElement(
                id="stem",
                node_a="throat",
                node_b="split",
                length_m=0.19,
                area_start_m2=0.0048,
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
        node_order=["rear", "inject", "throat", "blind", "split", "tap", "merge", "mouth"],
    )


def test_solve_frequency_point_supports_blind_throat_side_segment_topology() -> None:
    model = _blind_throat_model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 160.0)

    assert len(system.blind_throat_side_segment_topologies) == 1
    assert solved.node_order == ("rear", "inject", "throat", "blind", "split", "tap", "merge", "mouth")
    assert solved.pressures.shape == (8,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    rear_port_into_inject = -solved.waveguide_endpoint_flow["rear_port"].node_b
    throat_entry_from_inject = solved.waveguide_endpoint_flow["throat_entry"].node_a
    blind_to_closed_end = solved.waveguide_endpoint_flow["blind_segment"].node_b
    stem_to_split = -solved.waveguide_endpoint_flow["stem"].node_b
    main_from_split = solved.waveguide_endpoint_flow["main_leg"].node_a
    tap_up_from_split = solved.waveguide_endpoint_flow["tap_upstream"].node_a
    main_into_merge = -solved.waveguide_endpoint_flow["main_leg"].node_b
    tap_down_into_merge = -solved.waveguide_endpoint_flow["tap_downstream"].node_b
    exit_from_merge = solved.waveguide_endpoint_flow["exit"].node_a

    np.testing.assert_allclose(rear_port_into_inject, throat_entry_from_inject, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(blind_to_closed_end, 0.0, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(stem_to_split, main_from_split + tap_up_from_split, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(exit_from_merge, main_into_merge + tap_down_into_merge, rtol=1e-10, atol=1e-12)

    blind_index = solved.node_order.index("blind")
    throat_index = solved.node_order.index("throat")
    assert not np.isclose(solved.pressures[blind_index], solved.pressures[throat_index])
