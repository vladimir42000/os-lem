from __future__ import annotations

import os
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

# Check if we are in update mode
UPDATE_EXPECTED = os.environ.get("UPDATE_EXPECTED", "false").lower() == "true"


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

    if UPDATE_EXPECTED:
        print("\n" + "=" * 60)
        print("UPDATE_EXPECTED is true – printing new expected values for sweep test")
        print("Copy the lines below and replace the old hardcoded values in the test.\n")

        # Format as Python code that creates numpy arrays
        print("expected_input_impedance = np.array(")
        print("    [")
        for z in sweep.input_impedance:
            print(f"        np.complex128({z!r}),")
        print("    ],")
        print("    dtype=np.complex128,")
        print(")\n")

        print("expected_cone_velocity = np.array(")
        print("    [")
        for z in sweep.cone_velocity:
            print(f"        np.complex128({z!r}),")
        print("    ],")
        print("    dtype=np.complex128,")
        print(")\n")

        print("expected_cone_displacement = np.array(")
        print("    [")
        for z in sweep.cone_displacement:
            print(f"        np.complex128({z!r}),")
        print("    ],")
        print("    dtype=np.complex128,")
        print(")\n")
        print("=" * 60)
        return  # Skip assertions

    # Normal test execution
    expected_input_impedance = np.array(
        [
            np.complex128(6.229354155999273+3.3387734077370923j),
            np.complex128(6.440613345825014-4.438581511170099j),
            np.complex128(6.089099330284361-1.8056122825249394j),
        ],
        dtype=np.complex128,
    )
    expected_cone_velocity = np.array(
        [
            np.complex128(0.10178422499206721+0.16213300816775933j),
            np.complex128(0.14893350991939897-0.17597727301415453j),
            np.complex128(0.03811368665424757-0.10858169242208134j),
        ],
        dtype=np.complex128,
    )
    expected_cone_displacement = np.array(
        [
            np.complex128(0.001290213484412877-0.0008099731268132565j),
            np.complex128(-0.00028007652872034694-0.00023703504295698172j),
            np.complex128(-8.64065653912902e-05-3.032990815239551e-05j),
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

    p_obs = radiator_observation_pressure(sweep, system, "port_rad", 1.0)
    spl = radiator_spl(sweep, system, "port_rad", 1.0)

    if UPDATE_EXPECTED:
        print("\n" + "=" * 60)
        print("UPDATE_EXPECTED is true – printing new expected values for radiator test")
        print("Copy the lines below and replace the old hardcoded values in the test.\n")

        print("expected_observation_pressure = np.array(")
        print("    [")
        for z in p_obs:
            print(f"        np.complex128({z!r}),")
        print("    ],")
        print("    dtype=np.complex128,")
        print(")\n")

        print("expected_spl = np.array(")
        print("    [")
        for val in spl:
            print(f"        np.float64({val!r}),")
        print("    ],")
        print("    dtype=np.float64,")
        print(")\n")
        print("=" * 60)
        return

    # Normal test execution
    expected_observation_pressure = np.array(
        [
            np.complex128(-0.039044871026959804+0.024511677062589627j),
            np.complex128(0.21189423443634348+0.1793308392939483j),
            np.complex128(0.26148643169085634+0.09178538020075899j),
        ],
        dtype=np.complex128,
    )
    expected_spl = np.array(
        [
            np.float64(67.2536520948731),
            np.float64(82.84761779795964),
            np.float64(82.83299588656416),
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(p_obs, expected_observation_pressure, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(spl, expected_spl, rtol=1e-9, atol=1e-12)
