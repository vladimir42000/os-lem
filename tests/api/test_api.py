from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from os_lem.api import LineProfileResult, run_simulation
from os_lem.errors import ValidationError
from os_lem.elements.duct import duct_admittance
from os_lem.elements.radiator import radiator_impedance
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


def test_run_simulation_supports_term_level_mouth_directivity_only_contract() -> None:
    model_dict = load_model(Path("examples/vented_box/model.yaml"))
    model_dict["observations"] = [
        {"id": "spl_front_raw", "type": "spl", "target": "front_rad", "distance": "1 m", "radiation_space": "2pi"},
        {"id": "spl_port_candidate", "type": "spl", "target": "port_rad", "distance": "1 m", "radiation_space": "2pi", "observable_contract": "mouth_directivity_only"},
        {
            "id": "spl_total_candidate",
            "type": "spl_sum",
            "radiation_space": "2pi",
            "terms": [
                {"target": "front_rad", "distance": "1 m"},
                {"target": "port_rad", "distance": "1 m", "observable_contract": "mouth_directivity_only"},
            ],
        },
    ]
    frequencies = np.array([20.0, 30.0, 50.0, 80.0])

    result = run_simulation(model_dict, frequencies)

    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)
    sweep = solve_frequency_sweep(normalized, system, frequencies)
    p_front = radiator_observation_pressure(sweep, system, "front_rad", 1.0, radiation_space="2pi")
    p_port = radiator_observation_pressure(
        sweep,
        system,
        "port_rad",
        1.0,
        radiation_space="2pi",
        observable_contract="mouth_directivity_only",
    )
    expected = 20.0 * np.log10(np.maximum(np.abs(p_front + p_port), 1.0e-30) / 2.0e-5)

    np.testing.assert_allclose(result.series["spl_total_candidate"], expected)


def test_run_simulation_surfaces_mouth_area_consistency_error_for_candidate_contract() -> None:
    model_dict = {
        "meta": {"name": "mismatch_demo", "radiation_space": "2pi"},
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
            {"id": "rear_box", "type": "volume", "node": "rear", "value": "20 l"},
            {"id": "port_duct", "type": "duct", "node_a": "rear", "node_b": "port", "length": "12 cm", "area": "80 cm2"},
            {"id": "port_rad", "type": "radiator", "node": "port", "model": "flanged_piston", "area": "100 cm2"},
        ],
        "observations": [
            {"id": "spl_port_candidate", "type": "spl", "target": "port_rad", "distance": "1 m", "radiation_space": "2pi", "observable_contract": "mouth_directivity_only"},
        ],
    }

    with pytest.raises(ValueError, match="connected aperture area"):
        run_simulation(model_dict, [100.0])


def test_run_simulation_exposes_element_observables_for_duct_and_radiator_targets() -> None:
    model_dict = load_model(Path("examples/vented_box/model.yaml"))
    model_dict["observations"] = [
        {"id": "port_q", "type": "element_volume_velocity", "target": "port"},
        {"id": "port_v", "type": "element_particle_velocity", "target": "port"},
        {"id": "port_rad_q", "type": "element_volume_velocity", "target": "port_rad"},
        {"id": "port_rad_v", "type": "element_particle_velocity", "target": "port_rad"},
    ]
    frequencies = np.array([20.0, 30.0, 50.0, 80.0])

    result = run_simulation(model_dict, frequencies)

    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)
    sweep = solve_frequency_sweep(normalized, system, frequencies)

    port = normalized.ducts[0]
    p_rear = sweep.pressures[:, system.node_index[port.node_a]]
    p_mouth = sweep.pressures[:, system.node_index[port.node_b]]
    port_y = np.array(
        [duct_admittance(float(omega), port.length_m, port.area_m2) for omega in sweep.omega_rad_s],
        dtype=np.complex128,
    )
    expected_port_q = port_y * (p_rear - p_mouth)

    port_rad = normalized.radiators[1]
    p_port_node = sweep.pressures[:, system.node_index[port_rad.node]]
    port_rad_z = np.array(
        [radiator_impedance(port_rad.model, float(omega), port_rad.area_m2) for omega in sweep.omega_rad_s],
        dtype=np.complex128,
    )
    expected_port_rad_q = p_port_node / port_rad_z

    np.testing.assert_allclose(result.series["port_q"], expected_port_q)
    np.testing.assert_allclose(result.series["port_v"], expected_port_q / port.area_m2)
    np.testing.assert_allclose(result.series["port_rad_q"], expected_port_rad_q)
    np.testing.assert_allclose(result.series["port_rad_v"], expected_port_rad_q / port_rad.area_m2)
    assert result.units["port_q"] == "m^3/s"
    assert result.units["port_v"] == "m/s"
    assert result.units["port_rad_q"] == "m^3/s"
    assert result.units["port_rad_v"] == "m/s"


def test_run_simulation_exposes_waveguide_element_observables_with_frozen_endpoint_signs() -> None:
    model_dict = load_model(Path("examples/line_basic/model.yaml"))
    model_dict["observations"] = [
        {"id": "rear_q_a", "type": "element_volume_velocity", "target": "rear_line", "location": "a"},
        {"id": "rear_q_b", "type": "element_volume_velocity", "target": "rear_line", "location": "b"},
        {"id": "rear_v_a", "type": "element_particle_velocity", "target": "rear_line", "location": "a"},
        {"id": "rear_v_b", "type": "element_particle_velocity", "target": "rear_line", "location": "b"},
    ]
    frequencies = np.array([50.0, 100.0, 200.0])

    result = run_simulation(model_dict, frequencies)

    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)
    sweep = solve_frequency_sweep(normalized, system, frequencies)

    np.testing.assert_allclose(result.series["rear_q_a"], sweep.waveguide_endpoint_flow["rear_line"].node_a)
    np.testing.assert_allclose(result.series["rear_q_b"], -sweep.waveguide_endpoint_flow["rear_line"].node_b)
    np.testing.assert_allclose(result.series["rear_v_a"], sweep.waveguide_endpoint_velocity["rear_line"].node_a)
    np.testing.assert_allclose(result.series["rear_v_b"], -sweep.waveguide_endpoint_velocity["rear_line"].node_b)
    assert result.units["rear_q_a"] == "m^3/s"
    assert result.units["rear_q_b"] == "m^3/s"
    assert result.units["rear_v_a"] == "m/s"
    assert result.units["rear_v_b"] == "m/s"



def test_run_simulation_rejects_element_observable_on_unsupported_target_kind() -> None:
    model_dict = {
        "meta": {"name": "bad_element_observable", "radiation_space": "2pi"},
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
            {"id": "rear_q", "type": "element_volume_velocity", "target": "rear_box"},
        ],
    }

    with pytest.raises(ValidationError, match="requires target element type duct, radiator, or waveguide_1d"):
        run_simulation(model_dict, [100.0])


@pytest.mark.parametrize(
    ("observation", "message"),
    [
        (
            {"id": "rear_q", "type": "element_volume_velocity", "target": "rear_line"},
            "requires location 'a' or 'b'",
        ),
        (
            {"id": "rear_q", "type": "element_volume_velocity", "target": "rear_line", "location": "c"},
            "requires location 'a' or 'b'",
        ),
    ],
)
def test_run_simulation_rejects_missing_or_invalid_waveguide_location_for_element_observables(
    observation: dict[str, str],
    message: str,
) -> None:
    model_dict = load_model(Path("examples/line_basic/model.yaml"))
    model_dict["observations"] = [observation]

    with pytest.raises(ValidationError, match=message):
        run_simulation(model_dict, [100.0])


@pytest.mark.parametrize("target", ["port", "port_rad"])
def test_run_simulation_rejects_location_on_non_waveguide_element_observables(target: str) -> None:
    model_dict = load_model(Path("examples/vented_box/model.yaml"))
    model_dict["observations"] = [
        {"id": "bad_v", "type": "element_particle_velocity", "target": target, "location": "a"},
    ]

    with pytest.raises(ValidationError, match="does not accept location"):
        run_simulation(model_dict, [100.0])


def test_run_simulation_supports_minimal_split_recombine_waveguide_bundle() -> None:
    model_dict = {
        "meta": {"name": "split_recombine_bundle", "radiation_space": "2pi"},
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
            {
                "id": "main_path",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "mouth",
                "length": "55 cm",
                "area_start": "100 cm2",
                "area_end": "120 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "tap_path",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "mouth",
                "length": "32 cm",
                "area_start": "60 cm2",
                "area_end": "80 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "mouth_rad",
                "type": "radiator",
                "node": "mouth",
                "model": "flanged_piston",
                "area": "200 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "main_path", "location": "a"},
            {"id": "tap_q_a", "type": "element_volume_velocity", "target": "tap_path", "location": "a"},
            {"id": "main_q_b", "type": "element_volume_velocity", "target": "main_path", "location": "b"},
            {"id": "tap_q_b", "type": "element_volume_velocity", "target": "tap_path", "location": "b"},
        ],
    }
    frequencies = np.array([60.0, 120.0, 240.0])

    result = run_simulation(model_dict, frequencies)
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert len(system.parallel_branch_bundles) == 1
    bundle = system.parallel_branch_bundles[0]
    assert bundle.node_names == ("rear", "mouth")
    assert bundle.element_ids == ("main_path", "tap_path")

    assert result.series["main_q_a"].shape == (3,)
    assert result.series["tap_q_a"].shape == (3,)
    assert result.units["main_q_a"] == "m^3/s"
    assert result.units["tap_q_a"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["main_q_a"].real))
    assert np.all(np.isfinite(result.series["main_q_a"].imag))
    assert np.all(np.isfinite(result.series["tap_q_a"].real))
    assert np.all(np.isfinite(result.series["tap_q_a"].imag))
    assert np.all(np.isfinite(result.series["main_q_b"].real))
    assert np.all(np.isfinite(result.series["main_q_b"].imag))
    assert np.all(np.isfinite(result.series["tap_q_b"].real))
    assert np.all(np.isfinite(result.series["tap_q_b"].imag))
    assert not np.allclose(result.series["main_q_a"], result.series["tap_q_a"])
    assert not np.allclose(result.series["main_q_b"], result.series["tap_q_b"])


def test_run_simulation_supports_minimal_true_junction_waveguide_topology() -> None:
    model_dict = {
        "meta": {"name": "junction_demo", "radiation_space": "2pi"},
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
            {
                "id": "stem",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "junction",
                "length": "30 cm",
                "area_start": "90 cm2",
                "area_end": "95 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "main_branch",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "mouth_main",
                "length": "45 cm",
                "area_start": "95 cm2",
                "area_end": "110 cm2",
                "profile": "conical",
                "segments": 6,
            },
            {
                "id": "tap_branch",
                "type": "waveguide_1d",
                "node_a": "junction",
                "node_b": "mouth_tap",
                "length": "26 cm",
                "area_start": "40 cm2",
                "area_end": "55 cm2",
                "profile": "conical",
                "segments": 4,
            },
            {
                "id": "main_rad",
                "type": "radiator",
                "node": "mouth_main",
                "model": "flanged_piston",
                "area": "110 cm2",
            },
            {
                "id": "tap_rad",
                "type": "radiator",
                "node": "mouth_tap",
                "model": "flanged_piston",
                "area": "55 cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "p_junction", "type": "node_pressure", "target": "junction"},
            {"id": "stem_q_b", "type": "element_volume_velocity", "target": "stem", "location": "b"},
            {"id": "main_q_a", "type": "element_volume_velocity", "target": "main_branch", "location": "a"},
            {"id": "tap_q_a", "type": "element_volume_velocity", "target": "tap_branch", "location": "a"},
        ],
    }
    frequencies = np.array([60.0, 120.0, 240.0])

    result = run_simulation(model_dict, frequencies)
    normalized, _ = normalize_model(model_dict)
    system = assemble_system(normalized)

    assert len(system.parallel_branch_bundles) == 0
    assert len(system.acoustic_junctions) == 1
    junction = system.acoustic_junctions[0]
    assert junction.node_name == "junction"
    assert junction.incident_element_ids == ("stem", "main_branch", "tap_branch")

    assert result.series["stem_q_b"].shape == (3,)
    assert result.series["main_q_a"].shape == (3,)
    assert result.series["tap_q_a"].shape == (3,)
    assert result.units["p_junction"] == "Pa"
    assert result.units["stem_q_b"] == "m^3/s"
    assert result.units["main_q_a"] == "m^3/s"
    assert result.units["tap_q_a"] == "m^3/s"
    assert np.all(np.isfinite(result.zin_mag_ohm))
    assert np.all(np.isfinite(result.series["p_junction"].real))
    assert np.all(np.isfinite(result.series["p_junction"].imag))
    np.testing.assert_allclose(
        result.series["stem_q_b"],
        result.series["main_q_a"] + result.series["tap_q_a"],
        rtol=1e-10,
        atol=1e-12,
    )
    assert not np.allclose(result.series["main_q_a"], result.series["tap_q_a"])
