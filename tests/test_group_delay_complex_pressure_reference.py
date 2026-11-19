"""Independent acoustic group-delay regressions for existing enclosure models.

The reference uses the lumped network and exact uniform-tube transfer matrix,
not the kernel's observation-pressure or group-delay implementation.  It shares
the public radiation-load impedance formula, so this is not external parity.
"""

import numpy as np
import pytest

from os_lem.api import run_simulation
from os_lem.constants import C0, RHO0
from os_lem.elements.radiator import radiator_impedance


FREQUENCIES = np.geomspace(10.0, 1000.0, 600)


def _model(enclosure):
    driver = {
        "id": "drv1", "model": "ts_classic", "Re": "5.8 ohm", "Le": "0.35 mH",
        "Fs": "34 Hz", "Qes": 0.42, "Qms": 4.1, "Vas": "55 l",
        "Sd": "132 cm2", "source_voltage_rms": 2.83,
        "node_front": "front", "node_rear": "rear",
    }
    elements = [
        {"id": "front_rad", "type": "radiator", "node": "front",
         "model": "infinite_baffle_piston", "area": "132 cm2"},
    ]
    if enclosure == "closed_box":
        elements.append({"id": "rear_box", "type": "volume", "node": "rear", "value": "28 l"})
    elif enclosure == "bass_reflex":
        elements.extend([
            {"id": "rear_box", "type": "volume", "node": "rear", "value": "28 l"},
            {"id": "vent_duct", "type": "duct", "node_a": "rear",
             "node_b": "vent_mouth", "area": "24 cm2", "length": "18 cm"},
            {"id": "outlet_rad", "type": "radiator", "node": "vent_mouth",
             "model": "unflanged_piston", "area": "24 cm2"},
        ])
    elif enclosure == "transmission_line":
        elements.extend([
            {"id": "rear_line", "type": "waveguide_1d", "node_a": "rear",
             "node_b": "mouth", "area_start": "132 cm2", "area_end": "132 cm2",
             "length": "160 cm", "profile": "conical", "segments": 64, "loss": 0},
            {"id": "outlet_rad", "type": "radiator", "node": "mouth",
             "model": "unflanged_piston", "area": "132 cm2"},
        ])
    else:
        raise AssertionError(enclosure)
    observations = [{"id": "zin", "type": "input_impedance", "target": "drv1"}]
    if enclosure == "closed_box":
        observations.append({"id": "acoustic_spl", "type": "spl", "target": "front_rad", "distance": "1 m"})
    else:
        observations.append({
            "id": "acoustic_spl", "type": "spl_sum",
            "terms": [{"target": "front_rad", "distance": "1 m"},
                      {"target": "outlet_rad", "distance": "1 m"}],
        })
    observations.append({"id": "acoustic_delay", "type": "group_delay", "target": "acoustic_spl"})
    observations.append({"id": "electrical_delay", "type": "group_delay", "target": "zin"})
    return {"meta": {"radiation_space": "2pi"}, "driver": driver,
            "elements": elements, "observations": observations}


def _independent_pressure(enclosure, frequency_hz):
    """Compute coherent far-field pressure from independent network equations."""
    w = 2.0 * np.pi * frequency_hz
    sd = 132.0e-4
    compliance = .055 / (RHO0 * C0**2 * sd**2)
    mass = 1.0 / ((2.0 * np.pi * 34.0)**2 * compliance)
    resistance = 2.0 * np.pi * 34.0 * mass / 4.1
    force_factor = np.sqrt(2.0 * np.pi * 34.0 * mass * 5.8 / .42)
    front_load = np.array([radiator_impedance("infinite_baffle_piston", x, sd) for x in w])

    if enclosure == "closed_box":
        rear_load = 1.0 / (1j * w * .028 / (RHO0 * C0**2))
        outlet_ratio = 0.0
    else:
        area = .0024 if enclosure == "bass_reflex" else .0132
        outlet_load = np.array([radiator_impedance("unflanged_piston", x, area) for x in w])
        if enclosure == "bass_reflex":
            box = 1.0 / (1j * w * .028 / (RHO0 * C0**2))
            vent = 1j * w * RHO0 * .18 / area + outlet_load
            rear_load = box * vent / (box + vent)
            outlet_ratio = box / (box + vent)
        else:
            zc = RHO0 * C0 / area
            a = np.cos(w * 1.6 / C0)
            b = 1j * zc * np.sin(w * 1.6 / C0)
            c = 1j / zc * np.sin(w * 1.6 / C0)
            rear_load = (a * outlet_load + b) / (c * outlet_load + a)
            outlet_ratio = 1.0 / (c * outlet_load + a)

    mechanical = resistance + 1j * w * mass + 1.0 / (1j * w * compliance) + sd**2 * (front_load + rear_load)
    zin = 5.8 + 1j * w * .00035 + force_factor**2 / mechanical
    velocity = force_factor * (2.83 / zin) / mechanical
    q_front = sd * velocity
    q_outlet = -q_front * outlet_ratio
    pressure = 1j * w * RHO0 / (2.0 * np.pi) * (q_front + q_outlet)
    return pressure, zin


@pytest.mark.parametrize("enclosure", ["closed_box", "bass_reflex", "transmission_line"])
def test_acoustic_group_delay_uses_pressure_phase_not_spl_magnitude(enclosure):
    model = _model(enclosure)
    actual = run_simulation(model, FREQUENCIES)
    independent_pressure, independent_zin = _independent_pressure(enclosure, FREQUENCIES)

    expected_ms = -1000.0 * np.gradient(
        np.unwrap(np.angle(independent_pressure)), 2.0 * np.pi * FREQUENCIES,
    )
    actual_ms = 1000.0 * actual.series["acoustic_delay"]

    # Direct lumped/ABCD equations and the 64-piece uniform tube are algebraically
    # equivalent here.  The 1e-6 ms bound covers accumulated floating-point error.
    np.testing.assert_allclose(actual.zin_complex_ohm, independent_zin, rtol=1e-8, atol=1e-8)
    np.testing.assert_allclose(actual_ms, expected_ms, rtol=1e-8, atol=1e-6)
    assert np.max(np.abs(expected_ms)) > 0.01  # A returned zero series must fail.

    expected_electrical_delay = -np.gradient(
        np.unwrap(np.angle(actual.zin_complex_ohm)), 2.0 * np.pi * FREQUENCIES,
    )
    np.testing.assert_allclose(actual.series["electrical_delay"], expected_electrical_delay,
                               rtol=1e-12, atol=1e-12)
