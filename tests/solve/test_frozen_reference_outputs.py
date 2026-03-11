from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.model import (
    Driver,
    DuctElement,
    NormalizedModel,
    RadiatorElement,
    VolumeElement,
)
from os_lem.solve import (
    radiator_observation_pressure,
    radiator_spl,
    solve_frequency_sweep,
)


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


def _minimal_vented_like_model() -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        volumes=[
            VolumeElement(id="rear_vol", node="rear", value_m3=0.02),
        ],
        ducts=[
            DuctElement(id="port_duct", node_a="front", node_b="port", length_m=0.10, area_m2=0.01),
        ],
        radiators=[
            RadiatorElement(id="port_rad", node="port", model="flanged_piston", area_m2=0.01),
        ],
        node_order=["front", "rear", "port"],
    )


def test_frozen_reference_sweep_outputs_for_minimal_vented_like_model() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [20.0, 100.0, 200.0])

    expected_input_impedance = np.array(
        [
            2.7045260162128115 + 12.295234228165421j,
            5.633265229375788 + 4.416896723436643j,
            5.930331098894373 + 2.266141030625777j,
        ],
        dtype=np.complex128,
    )
    expected_cone_velocity = np.array(
        [
            0.3628918004428195 + 0.1881837568830556j,
            0.1376193547958033 + 0.2090861554573528j,
            0.0473680488063779 + 0.1363879609434765j,
        ],
        dtype=np.complex128,
    )
    expected_cone_displacement = np.array(
        [
            0.0014975187558771 - 0.002887801192399619j,
            0.0003327709517312 - 0.00021902800580869428j,
            0.0001085340908119 - 0.000037694295560765954j,
        ],
        dtype=np.complex128,
    )

    np.testing.assert_allclose(sweep.input_impedance, expected_input_impedance, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(sweep.cone_velocity, expected_cone_velocity, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(sweep.cone_displacement, expected_cone_displacement, rtol=1e-9, atol=1e-12)


def test_frozen_reference_radiator_outputs_for_minimal_vented_like_model() -> None:
    model = _minimal_vented_like_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [20.0, 100.0, 200.0])

    expected_observation_pressure = np.array(
        [
            -0.0143336078471013 + 0.1271708441527861j,
            0.2923108504394869 + 0.2609176023835914j,
            0.2968826103079641 - 0.3408331361423595j,
        ],
        dtype=np.complex128,
    )
    expected_spl = np.array(
        [
            76.12197585120684,
            85.84115235034902,
            87.08222215953217,
        ],
        dtype=np.float64,
    )

    p_obs = radiator_observation_pressure(sweep, system, "port_rad", 1.0)
    spl = radiator_spl(sweep, system, "port_rad", 1.0)

    np.testing.assert_allclose(p_obs, expected_observation_pressure, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(spl, expected_spl, rtol=1e-9, atol=1e-12)
