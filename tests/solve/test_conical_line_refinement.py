from __future__ import annotations

import copy
from pathlib import Path

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.parser import load_model, normalize_model
from os_lem.solve import solve_frequency_point, solve_frequency_sweep, waveguide_line_profile_pressure

_EXAMPLE = Path("examples/conical_line/model.yaml")
_VALIDATION_BAND_HZ = np.geomspace(30.0, 240.0, 120)
_PROFILE_FREQUENCY_HZ = 120.0
_PROFILE_POINTS = 65
_SEGMENT_COUNTS = (4, 8, 16, 32, 64)


def _example_with_segments(segments: int):
    model_dict = load_model(_EXAMPLE)
    model_dict = copy.deepcopy(model_dict)
    for element in model_dict["elements"]:
        if element["id"] == "line_1":
            element["segments"] = segments
            break
    normalized, warnings = normalize_model(model_dict)
    assert warnings == []
    system = assemble_system(normalized)
    return normalized, system


def _solve_example_case(segments: int):
    model, system = _example_with_segments(segments)
    sweep = solve_frequency_sweep(model, system, _VALIDATION_BAND_HZ)
    point = solve_frequency_point(model, system, _PROFILE_FREQUENCY_HZ)
    profile = waveguide_line_profile_pressure(point, system, "line_1", points=_PROFILE_POINTS)
    return sweep, profile


def test_conical_line_example_segmentation_refinement_remains_finite_across_official_grid() -> None:
    for segments in _SEGMENT_COUNTS:
        sweep, profile = _solve_example_case(segments)

        assert np.all(np.isfinite(sweep.input_impedance.real))
        assert np.all(np.isfinite(sweep.input_impedance.imag))
        assert np.all(np.isfinite(profile.values.real))
        assert np.all(np.isfinite(profile.values.imag))


def test_conical_line_example_segmentation_refinement_32_vs_64_meets_frozen_impedance_metrics() -> None:
    sweep_32, _ = _solve_example_case(32)
    sweep_64, _ = _solve_example_case(64)

    zmag_32 = np.abs(sweep_32.input_impedance)
    zmag_64 = np.abs(sweep_64.input_impedance)

    relative_mag_error = np.abs(zmag_32 - zmag_64) / np.maximum(zmag_64, 1.0e-30)
    assert np.max(relative_mag_error) < 0.02

    peak_idx_32 = int(np.argmax(zmag_32))
    peak_idx_64 = int(np.argmax(zmag_64))
    peak_shift = abs(_VALIDATION_BAND_HZ[peak_idx_32] - _VALIDATION_BAND_HZ[peak_idx_64]) / _VALIDATION_BAND_HZ[peak_idx_64]
    assert peak_shift < 0.01

    notch_idx_32 = int(np.argmin(zmag_32))
    notch_idx_64 = int(np.argmin(zmag_64))
    notch_shift = abs(_VALIDATION_BAND_HZ[notch_idx_32] - _VALIDATION_BAND_HZ[notch_idx_64]) / _VALIDATION_BAND_HZ[notch_idx_64]
    assert notch_shift < 0.01


def test_conical_line_example_segmentation_refinement_32_vs_64_meets_frozen_profile_metric() -> None:
    _, profile_32 = _solve_example_case(32)
    _, profile_64 = _solve_example_case(64)

    ref_mag = np.abs(profile_64.values)
    cmp_mag = np.abs(profile_32.values)
    mask = ref_mag >= 1.0e-9

    relative_profile_error = np.abs(cmp_mag[mask] - ref_mag[mask]) / ref_mag[mask]
    assert np.max(relative_profile_error) < 0.05
