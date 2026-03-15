from __future__ import annotations

from pathlib import Path

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import load_and_normalize
from os_lem.solve import (
    solve_frequency_point,
    solve_frequency_sweep,
    waveguide_line_profile_pressure,
)

_EXAMPLE = Path("examples/offset_line_minimal/model.yaml")


def _load_offset_line_model():
    model, warnings = load_and_normalize(_EXAMPLE)
    return model, warnings


def test_offset_line_minimal_example_loads_with_two_waveguides() -> None:
    model, warnings = _load_offset_line_model()

    assert warnings == []
    assert [waveguide.id for waveguide in model.waveguides] == ["tl_closed_stub", "tl_main"]


def test_offset_line_minimal_example_assembles_as_two_waveguide_branches() -> None:
    model, _ = _load_offset_line_model()
    system = assemble_system(model)

    waveguide_ids = [element.id for element in system.branch_elements if element.kind == "waveguide_1d"]

    assert waveguide_ids == ["tl_closed_stub", "tl_main"]


def test_offset_line_minimal_example_solves_with_finite_outputs() -> None:
    model, _ = _load_offset_line_model()
    system = assemble_system(model)

    sweep = solve_frequency_sweep(model, system, [30.0, 60.0, 120.0])

    assert sweep.frequency_hz.shape == (3,)
    assert sweep.pressures.shape[0] == 3
    assert np.all(np.isfinite(sweep.pressures.real))
    assert np.all(np.isfinite(sweep.pressures.imag))
    assert np.all(np.isfinite(sweep.input_impedance.real))
    assert np.all(np.isfinite(sweep.input_impedance.imag))
    assert np.all(np.isfinite(sweep.cone_velocity.real))
    assert np.all(np.isfinite(sweep.cone_velocity.imag))
    assert np.all(np.isfinite(sweep.cone_displacement.real))
    assert np.all(np.isfinite(sweep.cone_displacement.imag))


def test_offset_line_segment_pressure_profiles_match_endpoint_nodes() -> None:
    model, _ = _load_offset_line_model()
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 100.0)

    profile_stub = waveguide_line_profile_pressure(point, system, "tl_closed_stub", points=25)
    profile_main = waveguide_line_profile_pressure(point, system, "tl_main", points=25)

    idx = system.node_index

    np.testing.assert_allclose(profile_stub.values[0], point.pressures[idx["closed_end"]])
    np.testing.assert_allclose(profile_stub.values[-1], point.pressures[idx["rear"]])
    np.testing.assert_allclose(profile_main.values[0], point.pressures[idx["rear"]])
    np.testing.assert_allclose(profile_main.values[-1], point.pressures[idx["mouth"]])

    np.testing.assert_allclose(profile_stub.values[-1], profile_main.values[0])
