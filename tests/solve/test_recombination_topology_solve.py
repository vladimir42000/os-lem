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


def _recombination_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="path_main",
                node_a="rear",
                node_b="merge",
                length_m=0.48,
                area_start_m2=0.0090,
                area_end_m2=0.0085,
                profile="conical",
                segments=6,
            ),
            Waveguide1DElement(
                id="path_tap",
                node_a="rear",
                node_b="merge",
                length_m=0.29,
                area_start_m2=0.0045,
                area_end_m2=0.0040,
                profile="conical",
                segments=4,
            ),
            Waveguide1DElement(
                id="shared_exit",
                node_a="merge",
                node_b="mouth",
                length_m=0.34,
                area_start_m2=0.0125,
                area_end_m2=0.0150,
                profile="conical",
                segments=5,
            ),
        ],
        radiators=[
            RadiatorElement(id="front_rad", node="front", model="flanged_piston", area_m2=0.0132),
            RadiatorElement(id="mouth_rad", node="mouth", model="flanged_piston", area_m2=0.0150),
        ],
        node_order=["front", "rear", "merge", "mouth"],
    )


def test_solve_frequency_point_supports_recombination_topology_with_shared_exit() -> None:
    model = _recombination_model()
    system = assemble_system(model)

    solved = solve_frequency_point(model, system, 120.0)

    assert len(system.recombination_topologies) == 1
    assert solved.node_order == ("front", "rear", "merge", "mouth")
    assert solved.pressures.shape == (4,)
    assert np.all(np.isfinite(solved.pressures.real))
    assert np.all(np.isfinite(solved.pressures.imag))

    main_to_merge = -solved.waveguide_endpoint_flow["path_main"].node_b
    tap_to_merge = -solved.waveguide_endpoint_flow["path_tap"].node_b
    exit_from_merge = solved.waveguide_endpoint_flow["shared_exit"].node_a

    np.testing.assert_allclose(
        main_to_merge + tap_to_merge,
        exit_from_merge,
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(main_to_merge, tap_to_merge)
