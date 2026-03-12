from __future__ import annotations

import numpy as np

from os_lem.assemble import assemble_system
from os_lem.elements.duct import duct_admittance
from os_lem.elements.radiator import radiator_impedance
from os_lem.elements.volume import volume_admittance
from os_lem.elements.waveguide_1d import segment_midpoint_areas, uniform_segment_admittance
from os_lem.model import (
    Driver,
    DuctElement,
    NormalizedModel,
    RadiatorElement,
    VolumeElement,
    Waveguide1DElement,
)
from os_lem.solve import build_acoustic_matrix


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


def _waveguide_expected_equivalent_admittance(
    omega: float,
    waveguide: Waveguide1DElement,
) -> np.ndarray:
    areas = segment_midpoint_areas(
        waveguide.length_m,
        waveguide.area_start_m2,
        waveguide.area_end_m2,
        waveguide.segments,
    )
    dx = waveguide.length_m / waveguide.segments
    n_nodes = waveguide.segments + 1

    Y_full = np.zeros((n_nodes, n_nodes), dtype=np.complex128)

    for seg_idx, area_m2 in enumerate(areas):
        Y_seg = uniform_segment_admittance(omega, dx, float(area_m2))
        i = seg_idx
        j = seg_idx + 1

        Y_full[i, i] += Y_seg[0, 0]
        Y_full[i, j] += Y_seg[0, 1]
        Y_full[j, i] += Y_seg[1, 0]
        Y_full[j, j] += Y_seg[1, 1]

    if n_nodes == 2:
        return Y_full

    end_idx = np.array([0, n_nodes - 1], dtype=int)
    internal_idx = np.arange(1, n_nodes - 1, dtype=int)

    Y_ee = Y_full[np.ix_(end_idx, end_idx)]
    Y_ei = Y_full[np.ix_(end_idx, internal_idx)]
    Y_ie = Y_full[np.ix_(internal_idx, end_idx)]
    Y_ii = Y_full[np.ix_(internal_idx, internal_idx)]

    return Y_ee - Y_ei @ np.linalg.solve(Y_ii, Y_ie)


def test_build_acoustic_matrix_returns_complex_square_matrix() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="v1", node="rear", value_m3=0.02)],
        ducts=[DuctElement(id="d1", node_a="front", node_b="port", length_m=0.1, area_m2=0.01)],
        radiators=[RadiatorElement(id="r1", node="port", model="flanged_piston", area_m2=0.01)],
        node_order=["front", "rear", "port"],
    )
    system = assemble_system(model)

    built = build_acoustic_matrix(system, 100.0)

    assert built.frequency_hz == 100.0
    assert built.Yaa.shape == (3, 3)
    assert np.iscomplexobj(built.Yaa)


def test_build_acoustic_matrix_stamps_volume_and_radiator_on_diagonal() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="v1", node="rear", value_m3=0.02)],
        radiators=[RadiatorElement(id="r1", node="port", model="flanged_piston", area_m2=0.01)],
        node_order=["front", "rear", "port"],
    )
    system = assemble_system(model)

    built = build_acoustic_matrix(system, 100.0)
    omega = 2.0 * np.pi * 100.0
    yv = volume_admittance(omega, model.volumes[0].value_m3)
    yr = 1.0 / radiator_impedance(model.radiators[0].model, omega, model.radiators[0].area_m2)

    np.testing.assert_allclose(built.Yaa[1, 1], yv)
    np.testing.assert_allclose(built.Yaa[2, 2], yr)
    np.testing.assert_allclose(built.Yaa[0, 0], 0.0 + 0.0j)


def test_build_acoustic_matrix_stamps_duct_as_two_node_branch() -> None:
    model = NormalizedModel(
        driver=_driver(),
        ducts=[DuctElement(id="d1", node_a="front", node_b="port", length_m=0.1, area_m2=0.01)],
        node_order=["front", "rear", "port"],
    )
    system = assemble_system(model)

    built = build_acoustic_matrix(system, 100.0)
    omega = 2.0 * np.pi * 100.0
    y = duct_admittance(omega, model.ducts[0].length_m, model.ducts[0].area_m2)

    expected = np.zeros((3, 3), dtype=np.complex128)
    expected[0, 0] += y
    expected[2, 2] += y
    expected[0, 2] -= y
    expected[2, 0] -= y

    np.testing.assert_allclose(built.Yaa, expected)


def test_build_acoustic_matrix_stamps_waveguide_as_reduced_two_port_branch() -> None:
    model = NormalizedModel(
        driver=_driver(),
        waveguides=[
            Waveguide1DElement(
                id="wg1",
                node_a="front",
                node_b="port",
                length_m=0.4,
                area_start_m2=0.01,
                area_end_m2=0.02,
                profile="conical",
                segments=8,
            )
        ],
        node_order=["front", "rear", "port"],
    )
    system = assemble_system(model)

    built = build_acoustic_matrix(system, 100.0)
    omega = 2.0 * np.pi * 100.0
    Y_eq = _waveguide_expected_equivalent_admittance(omega, model.waveguides[0])

    expected = np.zeros((3, 3), dtype=np.complex128)
    expected[0, 0] += Y_eq[0, 0]
    expected[0, 2] += Y_eq[0, 1]
    expected[2, 0] += Y_eq[1, 0]
    expected[2, 2] += Y_eq[1, 1]

    np.testing.assert_allclose(built.Yaa, expected)


def test_build_acoustic_matrix_superposes_all_supported_stamps() -> None:
    model = NormalizedModel(
        driver=_driver(),
        volumes=[VolumeElement(id="v1", node="rear", value_m3=0.02)],
        ducts=[DuctElement(id="d1", node_a="front", node_b="port", length_m=0.1, area_m2=0.01)],
        radiators=[RadiatorElement(id="r1", node="port", model="flanged_piston", area_m2=0.01)],
        node_order=["front", "rear", "port"],
    )
    system = assemble_system(model)

    built = build_acoustic_matrix(system, 100.0)

    omega = 2.0 * np.pi * 100.0
    yv = volume_admittance(omega, model.volumes[0].value_m3)
    yd = duct_admittance(omega, model.ducts[0].length_m, model.ducts[0].area_m2)
    yr = 1.0 / radiator_impedance(model.radiators[0].model, omega, model.radiators[0].area_m2)

    expected = np.zeros((3, 3), dtype=np.complex128)
    expected[1, 1] += yv
    expected[2, 2] += yr
    expected[0, 0] += yd
    expected[2, 2] += yd
    expected[0, 2] -= yd
    expected[2, 0] -= yd

    np.testing.assert_allclose(built.Yaa, expected)


def test_build_acoustic_matrix_rejects_nonpositive_frequency() -> None:
    model = NormalizedModel(
        driver=_driver(),
        node_order=["front", "rear", "port"],
    )
    system = assemble_system(model)

    try:
        build_acoustic_matrix(system, 0.0)
    except ValueError as exc:
        assert "must be > 0" in str(exc)
    else:
        raise AssertionError("expected ValueError for nonpositive frequency")
