import math

from os_lem.assemble import assemble_system
from os_lem.model import Driver, NormalizedModel, RadiatorElement, VolumeElement
from os_lem.solve import solve_frequency_sweep


def _closed_box_model(rear_volume_m3: float) -> NormalizedModel:
    return NormalizedModel(
        driver=Driver(
            id="drv1",
            Re=5.8,
            Le=0.35e-3,
            Bl=5.38,
            Mms=9.8e-3,
            Cms=2.23e-3,
            Rms=0.51,
            Sd=132e-4,
            node_front="front",
            node_rear="rear",
            source_voltage_rms=2.83,
        ),
        volumes=[VolumeElement(id="rear_box", node="rear", value_m3=rear_volume_m3)],
        radiators=[
            RadiatorElement(
                id="front_rad",
                node="front",
                model="infinite_baffle_piston",
                area_m2=132e-4,
            )
        ],
        node_order=["front", "rear"],
    )


def test_closed_box_baffled_radiator_restores_strong_impedance_peak():
    model = _closed_box_model(18e-3)
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, [20.0, 40.0, 60.0, 68.95, 80.0, 100.0])

    zin_mag = abs(sweep.input_impedance[3])
    assert zin_mag > 30.0


def test_closed_box_larger_rear_volume_increases_low_frequency_peak_excursion():
    frequencies_hz = [20.0, 30.0, 40.0, 50.0, 60.0, 68.95, 80.0, 100.0]

    closed_model = _closed_box_model(18e-3)
    closed_system = assemble_system(closed_model)
    closed_sweep = solve_frequency_sweep(closed_model, closed_system, frequencies_hz)

    large_model = _closed_box_model(1000.0)
    large_system = assemble_system(large_model)
    large_sweep = solve_frequency_sweep(large_model, large_system, frequencies_hz)

    closed_peak_excursion_mm = max(abs(x) for x in closed_sweep.cone_displacement) * 1e3
    large_peak_excursion_mm = max(abs(x) for x in large_sweep.cone_displacement) * 1e3

    assert large_peak_excursion_mm > closed_peak_excursion_mm
