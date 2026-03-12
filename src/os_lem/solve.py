"""Frequency-domain acoustic and first coupled solve utilities for Session 6."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .assemble import AssembledElement, AssembledSystem
from .constants import C0, P_REF, RHO0
from .elements.duct import duct_admittance
from .elements.radiator import radiator_impedance
from .elements.volume import volume_admittance
from .elements.waveguide_1d import segment_midpoint_areas, uniform_segment_admittance
from .model import (
    DuctElement,
    NormalizedModel,
    RadiatorElement,
    VolumeElement,
    Waveguide1DElement,
)


@dataclass(slots=True, frozen=True)
class AcousticMatrixBuild:
    """Acoustic nodal matrix for one frequency."""

    frequency_hz: float
    omega_rad_s: float
    Yaa: np.ndarray


@dataclass(slots=True, frozen=True)
class CoupledSystemBuild:
    """Full first coupled linear system for one frequency."""

    frequency_hz: float
    omega_rad_s: float
    A: np.ndarray
    b: np.ndarray
    acoustic_matrix: np.ndarray


@dataclass(slots=True, frozen=True)
class SolvedFrequencyPoint:
    """Solved first coupled state for one frequency."""

    frequency_hz: float
    omega_rad_s: float
    node_order: tuple[str, ...]
    pressures: np.ndarray
    coil_current: complex
    cone_velocity: complex
    cone_displacement: complex
    solution_vector: np.ndarray


@dataclass(slots=True, frozen=True)
class SolvedFrequencySweep:
    """Solved state arrays over a frequency sweep."""

    frequency_hz: np.ndarray
    omega_rad_s: np.ndarray
    node_order: tuple[str, ...]
    pressures: np.ndarray
    coil_current: np.ndarray
    cone_velocity: np.ndarray
    cone_displacement: np.ndarray
    source_voltage_rms: float

    @property
    def input_impedance(self) -> np.ndarray:
        """Electrical input impedance V / I over the sweep."""

        return self.source_voltage_rms / self.coil_current


def _waveguide_equivalent_admittance_matrix(
    omega: float,
    payload: Waveguide1DElement,
) -> np.ndarray:
    """Return the reduced 2x2 nodal admittance of a segmented waveguide_1d."""

    areas = segment_midpoint_areas(
        payload.length_m,
        payload.area_start_m2,
        payload.area_end_m2,
        payload.segments,
    )
    dx = payload.length_m / payload.segments

    n_nodes = payload.segments + 1
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


def build_acoustic_matrix(system: AssembledSystem, frequency_hz: float) -> AcousticMatrixBuild:
    """Build the acoustic nodal admittance matrix for one frequency.

    Supported stamps in Patch 2:
    - volume: shunt admittance to reference
    - radiator: shunt admittance to reference
    - duct: branch admittance between two acoustic nodes
    - waveguide_1d: reduced 2-port branch admittance between two acoustic nodes
    """

    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be > 0")

    omega = 2.0 * np.pi * frequency_hz
    n = len(system.node_order)
    Yaa = np.zeros((n, n), dtype=np.complex128)

    for element in system.shunt_elements:
        if element.kind == "volume":
            payload = element.payload
            assert isinstance(payload, VolumeElement)
            y = volume_admittance(omega, payload.value_m3)
            Yaa[element.node_a, element.node_a] += y

        elif element.kind == "radiator":
            payload = element.payload
            assert isinstance(payload, RadiatorElement)
            z = radiator_impedance(payload.model, omega, payload.area_m2)
            y = 1.0 / z
            Yaa[element.node_a, element.node_a] += y

        else:
            raise RuntimeError(f"unsupported shunt element kind {element.kind!r}")

    for element in system.branch_elements:
        i = element.node_a
        j = element.node_b
        assert j is not None

        if element.kind == "duct":
            payload = element.payload
            assert isinstance(payload, DuctElement)
            y = duct_admittance(omega, payload.length_m, payload.area_m2)

            Yaa[i, i] += y
            Yaa[j, j] += y
            Yaa[i, j] -= y
            Yaa[j, i] -= y

        elif element.kind == "waveguide_1d":
            payload = element.payload
            assert isinstance(payload, Waveguide1DElement)
            Y_branch = _waveguide_equivalent_admittance_matrix(omega, payload)

            Yaa[i, i] += Y_branch[0, 0]
            Yaa[i, j] += Y_branch[0, 1]
            Yaa[j, i] += Y_branch[1, 0]
            Yaa[j, j] += Y_branch[1, 1]

        else:
            raise RuntimeError(f"unsupported branch element kind {element.kind!r}")

    return AcousticMatrixBuild(
        frequency_hz=frequency_hz,
        omega_rad_s=omega,
        Yaa=Yaa,
    )


def _electrical_impedance(model: NormalizedModel, omega: float) -> complex:
    driver = model.driver
    return complex(driver.Re, omega * driver.Le)


def _mechanical_impedance(model: NormalizedModel, omega: float) -> complex:
    driver = model.driver
    return complex(driver.Rms, omega * driver.Mms - 1.0 / (omega * driver.Cms))


def build_coupled_system(
    model: NormalizedModel,
    system: AssembledSystem,
    frequency_hz: float,
) -> CoupledSystemBuild:
    """Build the first coupled electromechano-acoustic linear system.

    Unknown vector ordering:
        [p_0, p_1, ..., p_(N-1), i_vc, u_cone]

    where:
    - p_k are acoustic node pressures
    - i_vc is voice-coil current
    - u_cone is cone velocity

    This is the minimal Phase 1 coupled model.
    """

    acoustic = build_acoustic_matrix(system, frequency_hz)
    omega = acoustic.omega_rad_s
    Yaa = acoustic.Yaa
    n = Yaa.shape[0]

    driver = model.driver
    A = np.zeros((n + 2, n + 2), dtype=np.complex128)
    b = np.zeros(n + 2, dtype=np.complex128)

    # Acoustic block.
    A[:n, :n] = Yaa

    # Cone velocity coupling into acoustic nodes.
    #
    # Convention used here:
    # - positive cone velocity injects +Sd volume velocity into the front node
    # - positive cone velocity injects -Sd volume velocity into the rear node
    #
    # With acoustic equations written as A x = b, this becomes:
    #   Yaa p + c*u = 0
    # where c has:
    #   c_front = -Sd
    #   c_rear  = +Sd
    cone_col = n + 1
    A[system.driver_front_index, cone_col] += -driver.Sd
    A[system.driver_rear_index, cone_col] += +driver.Sd

    # Electrical equation:
    #   Ze * i + Bl * u = Vs
    row_e = n
    col_i = n
    col_u = n + 1
    A[row_e, col_i] = _electrical_impedance(model, omega)
    A[row_e, col_u] = driver.Bl
    b[row_e] = driver.source_voltage_rms

    # Mechanical equation:
    #   Bl * i + Zm * u - Sd * p_front + Sd * p_rear = 0
    row_m = n + 1
    A[row_m, system.driver_front_index] = -driver.Sd
    A[row_m, system.driver_rear_index] = +driver.Sd
    A[row_m, col_i] = driver.Bl
    A[row_m, col_u] = -_mechanical_impedance(model, omega)

    return CoupledSystemBuild(
        frequency_hz=frequency_hz,
        omega_rad_s=omega,
        A=A,
        b=b,
        acoustic_matrix=Yaa.copy(),
    )


def solve_frequency_point(
    model: NormalizedModel,
    system: AssembledSystem,
    frequency_hz: float,
) -> SolvedFrequencyPoint:
    """Solve the first coupled one-frequency system."""

    built = build_coupled_system(model, system, frequency_hz)
    x = np.linalg.solve(built.A, built.b)

    n = len(system.node_order)
    pressures = x[:n].copy()
    coil_current = complex(x[n])
    cone_velocity = complex(x[n + 1])
    cone_displacement = cone_velocity / (1j * built.omega_rad_s)

    return SolvedFrequencyPoint(
        frequency_hz=frequency_hz,
        omega_rad_s=built.omega_rad_s,
        node_order=system.node_order,
        pressures=pressures,
        coil_current=coil_current,
        cone_velocity=cone_velocity,
        cone_displacement=cone_displacement,
        solution_vector=x,
    )


def solve_frequency_sweep(
    model: NormalizedModel,
    system: AssembledSystem,
    frequencies_hz: np.ndarray | list[float] | tuple[float, ...],
) -> SolvedFrequencySweep:
    """Solve the current coupled model over a 1D frequency sweep."""

    frequency_hz = np.asarray(frequencies_hz, dtype=np.float64)
    if frequency_hz.ndim != 1:
        raise ValueError("frequencies_hz must be a 1D sequence")
    if frequency_hz.size == 0:
        raise ValueError("frequencies_hz must not be empty")
    if np.any(frequency_hz <= 0.0):
        raise ValueError("all frequencies_hz values must be > 0")

    points = [solve_frequency_point(model, system, float(f)) for f in frequency_hz]

    pressures = np.stack([point.pressures for point in points], axis=0)
    coil_current = np.array([point.coil_current for point in points], dtype=np.complex128)
    cone_velocity = np.array([point.cone_velocity for point in points], dtype=np.complex128)
    cone_displacement = np.array([point.cone_displacement for point in points], dtype=np.complex128)
    omega_rad_s = np.array([point.omega_rad_s for point in points], dtype=np.float64)

    return SolvedFrequencySweep(
        frequency_hz=frequency_hz.copy(),
        omega_rad_s=omega_rad_s,
        node_order=points[0].node_order,
        pressures=pressures,
        coil_current=coil_current,
        cone_velocity=cone_velocity,
        cone_displacement=cone_displacement,
        source_voltage_rms=model.driver.source_voltage_rms,
    )


def _radiator_observation_transfer(model_name: str, omega: float, distance_m: float) -> complex:
    if distance_m <= 0.0:
        raise ValueError("distance_m must be > 0")

    if model_name in {"infinite_baffle_piston", "flanged_piston"}:
        scale = 2.0 * np.pi * distance_m
    elif model_name == "unflanged_piston":
        scale = 4.0 * np.pi * distance_m
    else:
        raise ValueError(f"unsupported radiator model {model_name!r}")

    k = omega / C0
    return (1j * omega * RHO0 / scale) * np.exp(-1j * k * distance_m)


def _find_radiator_element(system: AssembledSystem, radiator_id: str) -> AssembledElement:
    for element in system.shunt_elements:
        if element.kind == "radiator" and element.id == radiator_id:
            return element
    raise ValueError(f"unknown radiator id {radiator_id!r}")


def radiator_observation_pressure(
    sweep: SolvedFrequencySweep,
    system: AssembledSystem,
    radiator_id: str,
    distance_m: float,
) -> np.ndarray:
    """Return complex on-axis far-field pressure for one radiator over a sweep."""

    element = _find_radiator_element(system, radiator_id)
    payload = element.payload
    assert isinstance(payload, RadiatorElement)

    node_pressures = sweep.pressures[:, element.node_a]
    observation_pressure = np.empty_like(node_pressures)

    for idx, (omega, node_pressure) in enumerate(zip(sweep.omega_rad_s, node_pressures, strict=True)):
        z_rad = radiator_impedance(payload.model, float(omega), payload.area_m2)
        q_rad = node_pressure / z_rad
        h_q = _radiator_observation_transfer(payload.model, float(omega), distance_m)
        observation_pressure[idx] = h_q * q_rad

    return observation_pressure


def radiator_spl(
    sweep: SolvedFrequencySweep,
    system: AssembledSystem,
    radiator_id: str,
    distance_m: float,
) -> np.ndarray:
    """Return one-radiator SPL in dB over a sweep."""

    p_obs = radiator_observation_pressure(sweep, system, radiator_id, distance_m)
    return 20.0 * np.log10(np.abs(p_obs) / P_REF)
