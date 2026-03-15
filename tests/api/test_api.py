from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from os_lem.api import LineProfileResult, run_simulation
from os_lem.assemble import assemble_system
from os_lem.parser import load_model, normalize_model
from os_lem.solve import radiator_observation_pressure, solve_frequency_sweep


def test_run_simulation_accepts_dict_and_returns_ready_to_plot_common_series() -> None:
    model_dict = {
        "meta": {"name": "closed_demo", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "front",
            "node_rear": "rear",
        },
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "infinite_baffle_piston",
                "area": "132 cm2",
            },
            {"id": "rear_box", "type": "volume", "node": "rear", "value": "18 l"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl_front", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
        ],
    }

    result = run_simulation(model_dict, [20.0, 50.0, 100.0])

    assert result.frequencies_hz.shape == (3,)
    assert result.zin_complex_ohm is not None
    assert result.zin_mag_ohm is not None
    assert result.cone_displacement_m is not None
    assert result.cone_excursion_mm is not None
    assert result.units["spl_front"] == "dB"
    assert result.series["spl_front"].shape == (3,)
    np.testing.assert_allclose(result.cone_excursion_mm, np.abs(result.cone_displacement_m) * 1.0e3)


def test_run_simulation_spl_sum_matches_manual_complex_pressure_sum() -> None:
    model_dict = load_model(Path("examples/vented_box/model.yaml"))
    frequencies = np.array([20.0, 30.0, 50.0, 80.0])

    result = run_simulation(model_dict, frequencies)

    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)
    sweep = solve_frequency_sweep(normalized, system, frequencies)
    p_driver = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space="2pi")
    p_port = radiator_observation_pressure(sweep, system, "port_rad", 1.0, radiation_space="2pi")
    expected = 20.0 * np.log10(np.maximum(np.abs(p_driver + p_port), 1.0e-30) / 2.0e-5)

    np.testing.assert_allclose(result.series["spl_total"], expected)



def test_run_simulation_exposes_line_profile_without_temp_yaml_workaround() -> None:
    model_dict = load_model(Path("examples/line_basic/model.yaml"))
    result = run_simulation(model_dict, [50.0, 100.0, 200.0])

    profile = result.get_series("line_p_200")
    assert isinstance(profile, LineProfileResult)
    assert profile.frequency_hz == 200.0
    assert profile.quantity == "pressure"
    assert profile.x_m.ndim == 1
    assert profile.values.ndim == 1
    assert result.units["line_p_200"] == "Pa"



def test_run_simulation_group_delay_uses_preceding_complex_observation() -> None:
    model_dict = {
        "meta": {"name": "closed_with_gd", "radiation_space": "2pi"},
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": "5.8 ohm",
            "Le": "0.35 mH",
            "Fs": "34 Hz",
            "Qes": 0.42,
            "Qms": 4.1,
            "Vas": "55 l",
            "Sd": "132 cm2",
            "node_front": "front",
            "node_rear": "rear",
        },
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "infinite_baffle_piston",
                "area": "132 cm2",
            },
            {"id": "rear_box", "type": "volume", "node": "rear", "value": "18 l"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "zin_gd", "type": "group_delay", "target": "zin"},
        ],
    }

    result = run_simulation(model_dict, [20.0, 40.0, 80.0, 160.0])

    assert result.series["zin_gd"].shape == (4,)
    assert result.units["zin_gd"] == "s"
    assert np.all(np.isfinite(result.series["zin_gd"]))
