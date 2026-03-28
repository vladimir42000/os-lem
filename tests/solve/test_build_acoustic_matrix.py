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




def test_build_acoustic_matrix_waveguide_constant_area_is_segmentation_invariant() -> None:
    coarse = Waveguide1DElement(
        id="wg_coarse",
        node_a="front",
        node_b="port",
        length_m=0.4,
        area_start_m2=0.01,
        area_end_m2=0.01,
        profile="conical",
        segments=1,
    )
    fine = Waveguide1DElement(
        id="wg_fine",
        node_a="front",
        node_b="port",
        length_m=0.4,
        area_start_m2=0.01,
        area_end_m2=0.01,
        profile="conical",
        segments=16,
    )

    coarse_model = NormalizedModel(
        driver=_driver(),
        waveguides=[coarse],
        node_order=["front", "rear", "port"],
    )
    fine_model = NormalizedModel(
        driver=_driver(),
        waveguides=[fine],
        node_order=["front", "rear", "port"],
    )

    coarse_system = assemble_system(coarse_model)
    fine_system = assemble_system(fine_model)

    coarse_matrix = build_acoustic_matrix(coarse_system, 100.0).Yaa
    fine_matrix = build_acoustic_matrix(fine_system, 100.0).Yaa

    np.testing.assert_allclose(coarse_matrix, fine_matrix, rtol=1e-12, atol=1e-15)


def test_build_acoustic_matrix_waveguide_refinement_differences_shrink() -> None:
    def _matrix_for_segments(segments: int) -> np.ndarray:
        model = NormalizedModel(
            driver=_driver(),
            waveguides=[
                Waveguide1DElement(
                    id=f"wg_{segments}",
                    node_a="front",
                    node_b="port",
                    length_m=0.4,
                    area_start_m2=0.01,
                    area_end_m2=0.02,
                    profile="conical",
                    segments=segments,
                )
            ],
            node_order=["front", "rear", "port"],
        )
        system = assemble_system(model)
        return build_acoustic_matrix(system, 100.0).Yaa

    Y4 = _matrix_for_segments(4)
    Y8 = _matrix_for_segments(8)
    Y16 = _matrix_for_segments(16)
    Y32 = _matrix_for_segments(32)

    d_4_8 = np.linalg.norm(Y8 - Y4)
    d_8_16 = np.linalg.norm(Y16 - Y8)
    d_16_32 = np.linalg.norm(Y32 - Y16)

    assert d_8_16 < d_4_8
    assert d_16_32 < d_8_16

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


def test_build_acoustic_matrix_superposes_parallel_waveguide_bundle_between_same_nodes() -> None:
    wg_main = Waveguide1DElement(
        id="wg_main",
        node_a="rear",
        node_b="mouth",
        length_m=0.55,
        area_start_m2=0.010,
        area_end_m2=0.012,
        profile="conical",
        segments=6,
    )
    wg_shunt = Waveguide1DElement(
        id="wg_shunt",
        node_a="rear",
        node_b="mouth",
        length_m=0.32,
        area_start_m2=0.006,
        area_end_m2=0.008,
        profile="conical",
        segments=4,
    )
    model = NormalizedModel(
        driver=_driver(),
        waveguides=[wg_main, wg_shunt],
        node_order=["front", "rear", "mouth"],
    )
    system = assemble_system(model)

    built = build_acoustic_matrix(system, 100.0)
    omega = 2.0 * np.pi * 100.0
    Y_main = _waveguide_expected_equivalent_admittance(omega, wg_main)
    Y_shunt = _waveguide_expected_equivalent_admittance(omega, wg_shunt)

    expected = np.zeros((3, 3), dtype=np.complex128)
    expected[1, 1] += Y_main[0, 0] + Y_shunt[0, 0]
    expected[1, 2] += Y_main[0, 1] + Y_shunt[0, 1]
    expected[2, 1] += Y_main[1, 0] + Y_shunt[1, 0]
    expected[2, 2] += Y_main[1, 1] + Y_shunt[1, 1]

    np.testing.assert_allclose(built.Yaa, expected)
