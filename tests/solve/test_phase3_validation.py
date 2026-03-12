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
from os_lem.solve import solve_frequency_sweep


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


def _vented_model(rear_volume_m3: float, duct_length_m: float, duct_area_m2: float) -> NormalizedModel:
    return NormalizedModel(
        driver=_driver(),
        volumes=[
            VolumeElement(id="rear_vol", node="rear", value_m3=rear_volume_m3),
        ],
        ducts=[
            DuctElement(
                id="port_duct",
                node_a="front",
                node_b="port",
                length_m=duct_length_m,
                area_m2=duct_area_m2,
            ),
        ],
        radiators=[
            RadiatorElement(id="port_rad", node="port", model="flanged_piston", area_m2=duct_area_m2),
        ],
        node_order=["front", "rear", "port"],
    )


def test_larger_rear_volume_increases_low_frequency_cone_displacement() -> None:
    frequencies_hz = [20.0, 60.0, 100.0]

    small_model = _vented_model(rear_volume_m3=0.005, duct_length_m=0.10, duct_area_m2=0.010)
    base_model = _vented_model(rear_volume_m3=0.020, duct_length_m=0.10, duct_area_m2=0.010)
    large_model = _vented_model(rear_volume_m3=0.050, duct_length_m=0.10, duct_area_m2=0.010)

    small_sweep = solve_frequency_sweep(small_model, assemble_system(small_model), frequencies_hz)
    base_sweep = solve_frequency_sweep(base_model, assemble_system(base_model), frequencies_hz)
    large_sweep = solve_frequency_sweep(large_model, assemble_system(large_model), frequencies_hz)

    for idx in range(len(frequencies_hz)):
        assert np.abs(small_sweep.cone_displacement[idx]) < np.abs(base_sweep.cone_displacement[idx])
        assert np.abs(base_sweep.cone_displacement[idx]) < np.abs(large_sweep.cone_displacement[idx])


def test_longer_duct_increases_port_pressure_magnitude_at_selected_frequencies() -> None:
    frequencies_hz = [20.0, 60.0, 100.0, 200.0]

    short_model = _vented_model(rear_volume_m3=0.020, duct_length_m=0.05, duct_area_m2=0.010)
    base_model = _vented_model(rear_volume_m3=0.020, duct_length_m=0.10, duct_area_m2=0.010)
    long_model = _vented_model(rear_volume_m3=0.020, duct_length_m=0.20, duct_area_m2=0.010)

    short_sweep = solve_frequency_sweep(short_model, assemble_system(short_model), frequencies_hz)
    base_sweep = solve_frequency_sweep(base_model, assemble_system(base_model), frequencies_hz)
    long_sweep = solve_frequency_sweep(long_model, assemble_system(long_model), frequencies_hz)

    short_port = np.abs(short_sweep.pressures[:, 2])
    base_port = np.abs(base_sweep.pressures[:, 2])
    long_port = np.abs(long_sweep.pressures[:, 2])

    for idx in range(len(frequencies_hz)):
        assert short_port[idx] < base_port[idx]
        assert base_port[idx] < long_port[idx]


def test_smaller_duct_area_increases_port_pressure_magnitude_at_selected_frequencies() -> None:
    frequencies_hz = [20.0, 60.0, 100.0, 200.0]

    large_area_model = _vented_model(rear_volume_m3=0.020, duct_length_m=0.10, duct_area_m2=0.020)
    base_model = _vented_model(rear_volume_m3=0.020, duct_length_m=0.10, duct_area_m2=0.010)
    small_area_model = _vented_model(rear_volume_m3=0.020, duct_length_m=0.10, duct_area_m2=0.005)

    large_area_sweep = solve_frequency_sweep(large_area_model, assemble_system(large_area_model), frequencies_hz)
    base_sweep = solve_frequency_sweep(base_model, assemble_system(base_model), frequencies_hz)
    small_area_sweep = solve_frequency_sweep(small_area_model, assemble_system(small_area_model), frequencies_hz)

    large_area_port = np.abs(large_area_sweep.pressures[:, 2])
    base_port = np.abs(base_sweep.pressures[:, 2])
    small_area_port = np.abs(small_area_sweep.pressures[:, 2])

    for idx in range(len(frequencies_hz)):
        assert large_area_port[idx] < base_port[idx]
        assert base_port[idx] < small_area_port[idx]
