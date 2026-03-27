from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from os_lem.api import LineProfileResult, run_simulation
from os_lem.assemble import assemble_system
from os_lem.elements.waveguide_1d import area_at_position
from os_lem.parser import load_and_normalize, load_model, normalize_model
from os_lem.solve import solve_frequency_point, solve_frequency_sweep

_EXAMPLE = Path("examples/conical_line/model.yaml")


def _load_conical_line_model():
    model, warnings = load_and_normalize(_EXAMPLE)
    return model, warnings


def test_conical_line_example_loads_as_lossy_conical_hero_example() -> None:
    model, warnings = _load_conical_line_model()

    assert warnings == []
    assert model.metadata["name"] == "conical_line"
    assert model.metadata["radiation_space"] == "2pi"
    assert [waveguide.id for waveguide in model.waveguides] == ["line_1"]

    waveguide = model.waveguides[0]
    assert waveguide.profile == "conical"
    assert waveguide.segments == 16
    assert waveguide.loss == pytest.approx(0.18)

    assert [obs.id for obs in model.observations] == [
        "zin",
        "spl_driver",
        "spl_mouth",
        "spl_total",
        "p_rear",
        "line_q_a",
        "line_q_b",
        "line_v_a",
        "line_v_b",
        "line_p_120",
        "line_q_120",
        "line_v_120",
    ]


def test_conical_line_example_solves_with_finite_outputs() -> None:
    model, _ = _load_conical_line_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [30.0, 60.0, 120.0, 240.0])

    assert sweep.frequency_hz.shape == (4,)
    assert np.all(np.isfinite(sweep.pressures.real))
    assert np.all(np.isfinite(sweep.pressures.imag))
    assert np.all(np.isfinite(sweep.input_impedance.real))
    assert np.all(np.isfinite(sweep.input_impedance.imag))
    assert np.all(np.isfinite(sweep.cone_velocity.real))
    assert np.all(np.isfinite(sweep.cone_velocity.imag))
    assert np.all(np.isfinite(sweep.cone_displacement.real))
    assert np.all(np.isfinite(sweep.cone_displacement.imag))



def test_conical_line_example_api_exposes_jointly_consistent_profiles_and_endpoint_observables() -> None:
    model_dict = load_model(_EXAMPLE)
    result = run_simulation(model_dict, [40.0, 80.0, 120.0, 160.0])

    assert result.warnings == ()
    assert result.units["line_q_a"] == "m^3/s"
    assert result.units["line_q_b"] == "m^3/s"
    assert result.units["line_v_a"] == "m/s"
    assert result.units["line_v_b"] == "m/s"
    assert result.units["line_p_120"] == "Pa"
    assert result.units["line_q_120"] == "m^3/s"
    assert result.units["line_v_120"] == "m/s"

    pressure_profile = result.get_series("line_p_120")
    flow_profile = result.get_series("line_q_120")
    particle_profile = result.get_series("line_v_120")

    assert isinstance(pressure_profile, LineProfileResult)
    assert isinstance(flow_profile, LineProfileResult)
    assert isinstance(particle_profile, LineProfileResult)

    np.testing.assert_allclose(pressure_profile.x_m, flow_profile.x_m)
    np.testing.assert_allclose(flow_profile.x_m, particle_profile.x_m)
    assert np.all(np.isfinite(pressure_profile.values.real))
    assert np.all(np.isfinite(pressure_profile.values.imag))
    assert np.all(np.isfinite(flow_profile.values.real))
    assert np.all(np.isfinite(flow_profile.values.imag))
    assert np.all(np.isfinite(particle_profile.values.real))
    assert np.all(np.isfinite(particle_profile.values.imag))

    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)
    point = solve_frequency_point(normalized, system, 120.0)
    idx = system.node_index
    waveguide = normalized.waveguides[0]

    np.testing.assert_allclose(pressure_profile.values[0], point.pressures[idx["rear"]])
    np.testing.assert_allclose(pressure_profile.values[-1], point.pressures[idx["mouth"]])
    np.testing.assert_allclose(flow_profile.values[0], point.waveguide_endpoint_flow["line_1"].node_a)
    np.testing.assert_allclose(flow_profile.values[-1], -point.waveguide_endpoint_flow["line_1"].node_b)
    np.testing.assert_allclose(particle_profile.values[0], point.waveguide_endpoint_velocity["line_1"].node_a)
    np.testing.assert_allclose(particle_profile.values[-1], -point.waveguide_endpoint_velocity["line_1"].node_b)

    area = np.array(
        [
            area_at_position(
                waveguide.length_m,
                waveguide.area_start_m2,
                waveguide.area_end_m2,
                float(x_m),
            )
            for x_m in flow_profile.x_m
        ],
        dtype=float,
    )
    np.testing.assert_allclose(particle_profile.values, flow_profile.values / area)

    np.testing.assert_allclose(result.series["line_q_a"], result.sweep.waveguide_endpoint_flow["line_1"].node_a)
    np.testing.assert_allclose(result.series["line_q_b"], -result.sweep.waveguide_endpoint_flow["line_1"].node_b)
    np.testing.assert_allclose(result.series["line_v_a"], result.sweep.waveguide_endpoint_velocity["line_1"].node_a)
    np.testing.assert_allclose(result.series["line_v_b"], -result.sweep.waveguide_endpoint_velocity["line_1"].node_b)
