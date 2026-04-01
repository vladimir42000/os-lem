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
        node_front="front",
        node_rear="rear",
        source_voltage_rms=2.83,
    )


def _model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        volumes=[
            VolumeElement(id="rear_chamber", node="rear", value_m3=0.010),
            VolumeElement(id="throat_chamber", node="throat", value_m3=0.0016),
        ],
        waveguides=[
            Waveguide1DElement(id="rear_port", node_a="rear", node_b="inject", length_m=0.11, area_start_m2=0.0042, area_end_m2=0.0045, profile="conical", segments=2),
            Waveguide1DElement(id="throat_entry", node_a="inject", node_b="throat", length_m=0.08, area_start_m2=0.0045, area_end_m2=0.0048, profile="conical", segments=2),
            Waveguide1DElement(id="blind_upstream", node_a="throat", node_b="throat_side", length_m=0.04, area_start_m2=0.0048, area_end_m2=0.0041, profile="conical", segments=2),
            Waveguide1DElement(id="blind_downstream", node_a="throat_side", node_b="blind", length_m=0.05, area_start_m2=0.0041, area_end_m2=0.0039, profile="conical", segments=2),
            Waveguide1DElement(id="rear_leg", node_a="throat", node_b="mouth", length_m=0.61, area_start_m2=0.0048, area_end_m2=0.0105, profile="conical", segments=7),
        ],
        radiators=[
            RadiatorElement(id="front_rad", node="front", model="flanged_piston", area_m2=0.0130),
            RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0105),
        ],
        node_order=["rear", "inject", "throat", "throat_side", "blind", "front", "mouth"],
    )


def test_solve_frequency_point_supports_back_loaded_horn_skeleton() -> None:
    model = _model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 160.0)

    assert len(system.back_loaded_horn_skeletons) == 1
    assert solved.node_order == ("rear", "inject", "throat", "throat_side", "blind", "front", "mouth")
    assert solved.pressures.shape == (7,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    rear_port_into_inject = -solved.waveguide_endpoint_flow["rear_port"].node_b
    throat_entry_from_inject = solved.waveguide_endpoint_flow["throat_entry"].node_a
    blind_up_into_side = -solved.waveguide_endpoint_flow["blind_upstream"].node_b
    blind_down_from_side = solved.waveguide_endpoint_flow["blind_downstream"].node_a
    blind_closed_end = solved.waveguide_endpoint_flow["blind_downstream"].node_b

    np.testing.assert_allclose(rear_port_into_inject, throat_entry_from_inject, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(blind_down_from_side, blind_up_into_side, rtol=1e-10, atol=1e-12)
    assert abs(blind_closed_end) < 1.0e-10

    front_index = solved.node_order.index("front")
    mouth_index = solved.node_order.index("mouth")
    throat_index = solved.node_order.index("throat")
    assert np.isfinite(solved.pressures[front_index])
    assert np.isfinite(solved.pressures[mouth_index])
    assert not np.isclose(solved.pressures[front_index], solved.pressures[mouth_index])
    assert not np.isclose(solved.pressures[mouth_index], solved.pressures[throat_index])
