"""Frequency-domain acoustic and first coupled solve utilities for Session 6."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from .assemble import AssembledElement, AssembledSystem
from .constants import C0, P_REF, RHO0
from .elements.duct import duct_admittance
from .elements.radiator import (
    default_radiation_space_for_model,
    normalize_radiation_space,
    radiator_impedance,
    solid_angle_for_radiation_space,
)
from .elements.volume import volume_admittance
from .elements.waveguide_1d import (
    area_at_position,
    segment_endpoint_positions,
    segment_midpoint_areas,
    uniform_segment_admittance,
)
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
class WaveguideEndpointFlowPoint:
    """Complex endpoint flows for one waveguide at one frequency."""

    node_a: complex
    node_b: complex


@dataclass(slots=True, frozen=True)
class WaveguideEndpointFlowSweep:
    """Complex endpoint flows for one waveguide over a sweep."""

    node_a: np.ndarray
    node_b: np.ndarray


@dataclass(slots=True, frozen=True)
class WaveguideEndpointVelocityPoint:
    """Complex endpoint particle velocities for one waveguide at one frequency."""

    node_a: complex
    node_b: complex


@dataclass(slots=True, frozen=True)
class WaveguideEndpointVelocitySweep:
    """Complex endpoint particle velocities for one waveguide over a sweep."""

    node_a: np.ndarray
    node_b: np.ndarray


@dataclass(slots=True, frozen=True)
class WaveguideLineProfile:
    """Sampled one-frequency line profile for one waveguide quantity."""

    quantity: str
    x_m: np.ndarray
    values: np.ndarray


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
    waveguide_endpoint_flow: Mapping[str, WaveguideEndpointFlowPoint]
    waveguide_endpoint_velocity: Mapping[str, WaveguideEndpointVelocityPoint]
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
    waveguide_endpoint_flow: Mapping[str, WaveguideEndpointFlowSweep]
    waveguide_endpoint_velocity: Mapping[str, WaveguideEndpointVelocitySweep]
    source_voltage_rms: float

    @property
    def input_impedance(self) -> np.ndarray:
        """Electrical input impedance V / I over the sweep."""

        return self.source_voltage_rms / self.coil_current


def _waveguide_full_admittance_matrix(
    omega: float,
    payload: Waveguide1DElement,
) -> np.ndarray:
    """Return the segmented full nodal admittance of one waveguide_1d."""

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
        Y_seg = uniform_segment_admittance(omega, dx, float(area_m2), loss_np_per_m=float(payload.loss or 0.0))
        i = seg_idx
        j = seg_idx + 1

        Y_full[i, i] += Y_seg[0, 0]
        Y_full[i, j] += Y_seg[0, 1]
        Y_full[j, i] += Y_seg[1, 0]
        Y_full[j, j] += Y_seg[1, 1]

    return Y_full


def _waveguide_equivalent_admittance_matrix(
    omega: float,
    payload: Waveguide1DElement,
) -> np.ndarray:
    """Return the reduced 2x2 nodal admittance of a segmented waveguide_1d."""

    Y_full = _waveguide_full_admittance_matrix(omega, payload)
    n_nodes = payload.segments + 1

    if n_nodes == 2:
        return Y_full

    end_idx = np.array([0, n_nodes - 1], dtype=int)
    internal_idx = np.arange(1, n_nodes - 1, dtype=int)

    Y_ee = Y_full[np.ix_(end_idx, end_idx)]
    Y_ei = Y_full[np.ix_(end_idx, internal_idx)]
    Y_ie = Y_full[np.ix_(internal_idx, end_idx)]
    Y_ii = Y_full[np.ix_(internal_idx, internal_idx)]

    return Y_ee - Y_ei @ np.linalg.solve(Y_ii, Y_ie)


def _waveguide_internal_nodal_pressures(
    omega: float,
    payload: Waveguide1DElement,
    pressure_a: complex,
    pressure_b: complex,
) -> np.ndarray:
    """Recover all segmented nodal pressures from the endpoint pressures."""

    nodal_pressures = np.empty(payload.segments + 1, dtype=np.complex128)
    nodal_pressures[0] = pressure_a
    nodal_pressures[-1] = pressure_b

    if payload.segments == 1:
        return nodal_pressures

    Y_full = _waveguide_full_admittance_matrix(omega, payload)
    end_idx = np.array([0, payload.segments], dtype=int)
    internal_idx = np.arange(1, payload.segments, dtype=int)

    Y_ie = Y_full[np.ix_(internal_idx, end_idx)]
    Y_ii = Y_full[np.ix_(internal_idx, internal_idx)]
    end_pressures = np.array([pressure_a, pressure_b], dtype=np.complex128)
    nodal_pressures[1:-1] = -np.linalg.solve(Y_ii, Y_ie @ end_pressures)
    return nodal_pressures




def _waveguide_segment_left_flows(
    omega: float,
    payload: Waveguide1DElement,
    nodal_pressures: np.ndarray,
) -> np.ndarray:
    """Return the +x-directed left-endpoint flow of each waveguide segment."""

    areas = segment_midpoint_areas(
        payload.length_m,
        payload.area_start_m2,
        payload.area_end_m2,
        payload.segments,
    )
    dx = payload.length_m / payload.segments
    left_flows = np.empty(payload.segments, dtype=np.complex128)

    for seg_idx, area_m2 in enumerate(areas):
        Y_seg = uniform_segment_admittance(omega, dx, float(area_m2), loss_np_per_m=float(payload.loss or 0.0))
        p_seg = np.array(
            [nodal_pressures[seg_idx], nodal_pressures[seg_idx + 1]],
            dtype=np.complex128,
        )
        q_seg = Y_seg @ p_seg
        left_flows[seg_idx] = q_seg[0]

    return left_flows


def _waveguide_sample_profile_quantity(
    point: SolvedFrequencyPoint,
    system: AssembledSystem,
    waveguide_id: str,
    points: int,
    quantity: str,
) -> WaveguideLineProfile:
    """Return a sampled one-frequency line profile for one waveguide quantity."""

    if points < 2:
        raise ValueError("points must be >= 2")

    if quantity not in {"pressure", "volume_velocity", "particle_velocity"}:
        raise ValueError(f"unsupported waveguide line profile quantity {quantity!r}")

    element = _find_waveguide_element(system, waveguide_id)
    payload = element.payload
    assert isinstance(payload, Waveguide1DElement)
    assert element.node_b is not None

    pressure_a = complex(point.pressures[element.node_a])
    pressure_b = complex(point.pressures[element.node_b])
    nodal_pressures = _waveguide_internal_nodal_pressures(
        point.omega_rad_s,
        payload,
        pressure_a,
        pressure_b,
    )

    segment_positions = segment_endpoint_positions(payload.length_m, payload.segments)
    segment_areas = segment_midpoint_areas(
        payload.length_m,
        payload.area_start_m2,
        payload.area_end_m2,
        payload.segments,
    )
    dx = payload.length_m / payload.segments

    x_m = np.linspace(0.0, payload.length_m, points, dtype=float)
    values = np.empty(points, dtype=np.complex128)

    gamma = complex(float(payload.loss or 0.0), point.omega_rad_s / C0)
    gamma_dx = gamma * dx
    sinh_gamma_dx = np.sinh(gamma_dx)

    for idx, x_sample in enumerate(x_m):
        if np.isclose(x_sample, payload.length_m):
            seg_idx = payload.segments - 1
            x_local = dx
        else:
            seg_idx = int(np.searchsorted(segment_positions, x_sample, side="right") - 1)
            seg_idx = max(0, min(seg_idx, payload.segments - 1))
            x_local = x_sample - segment_positions[seg_idx]

        p_left = complex(nodal_pressures[seg_idx])
        p_right = complex(nodal_pressures[seg_idx + 1])
        zc_a = RHO0 * C0 / float(segment_areas[seg_idx])
        left_weight = np.sinh(gamma * (dx - x_local)) / sinh_gamma_dx
        right_weight = np.sinh(gamma * x_local) / sinh_gamma_dx
        pressure = left_weight * p_left + right_weight * p_right
        volume_velocity = -(
            1.0 / (zc_a * sinh_gamma_dx)
        ) * (
            -p_left * np.cosh(gamma * (dx - x_local))
            + p_right * np.cosh(gamma * x_local)
        )

        if quantity == "pressure":
            values[idx] = pressure
        elif quantity == "volume_velocity":
            values[idx] = volume_velocity
        else:
            local_area_m2 = area_at_position(
                payload.length_m,
                payload.area_start_m2,
                payload.area_end_m2,
                x_sample,
            )
            values[idx] = volume_velocity / local_area_m2

    return WaveguideLineProfile(quantity=quantity, x_m=x_m, values=values)


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


def _waveguide_endpoint_flows_for_pressures(
    system: AssembledSystem,
    omega: float,
    pressures: np.ndarray,
) -> dict[str, WaveguideEndpointFlowPoint]:
    """Return endpoint flows for assembled waveguide branches.

    The sign/orientation follows the reduced branch two-port relation
    q = Y_branch @ [p(node_a), p(node_b)]^T, with port 0 mapped to node_a
    and port 1 mapped to node_b.
    """

    endpoint_flows: dict[str, WaveguideEndpointFlowPoint] = {}

    for element in system.branch_elements:
        if element.kind != "waveguide_1d":
            continue

        payload = element.payload
        assert isinstance(payload, Waveguide1DElement)
        assert element.node_b is not None

        endpoint_pressures = np.array(
            [pressures[element.node_a], pressures[element.node_b]],
            dtype=np.complex128,
        )
        Y_branch = _waveguide_equivalent_admittance_matrix(omega, payload)
        endpoint_flow = Y_branch @ endpoint_pressures

        endpoint_flows[element.id] = WaveguideEndpointFlowPoint(
            node_a=complex(endpoint_flow[0]),
            node_b=complex(endpoint_flow[1]),
        )

    return endpoint_flows


def _find_waveguide_element(system: AssembledSystem, waveguide_id: str) -> AssembledElement:
    for element in system.branch_elements:
        if element.kind == "waveguide_1d" and element.id == waveguide_id:
            return element
    raise ValueError(f"unknown waveguide id {waveguide_id!r}")


def _waveguide_endpoint_velocity_for_flow(
    system: AssembledSystem,
    endpoint_flow: Mapping[str, WaveguideEndpointFlowPoint],
) -> dict[str, WaveguideEndpointVelocityPoint]:
    """Return endpoint particle velocities for assembled waveguide branches."""

    endpoint_velocity: dict[str, WaveguideEndpointVelocityPoint] = {}

    for element in system.branch_elements:
        if element.kind != "waveguide_1d":
            continue

        payload = element.payload
        assert isinstance(payload, Waveguide1DElement)

        flow = endpoint_flow[element.id]
        endpoint_velocity[element.id] = WaveguideEndpointVelocityPoint(
            node_a=flow.node_a / payload.area_start_m2,
            node_b=flow.node_b / payload.area_end_m2,
        )

    return endpoint_velocity


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
    waveguide_endpoint_flow = _waveguide_endpoint_flows_for_pressures(
        system,
        built.omega_rad_s,
        pressures,
    )
    waveguide_endpoint_velocity = _waveguide_endpoint_velocity_for_flow(
        system,
        waveguide_endpoint_flow,
    )

    return SolvedFrequencyPoint(
        frequency_hz=frequency_hz,
        omega_rad_s=built.omega_rad_s,
        node_order=system.node_order,
        pressures=pressures,
        coil_current=coil_current,
        cone_velocity=cone_velocity,
        cone_displacement=cone_displacement,
        waveguide_endpoint_flow=waveguide_endpoint_flow,
        waveguide_endpoint_velocity=waveguide_endpoint_velocity,
        solution_vector=x,
    )


def waveguide_line_profile_pressure(
    point: SolvedFrequencyPoint,
    system: AssembledSystem,
    waveguide_id: str,
    points: int,
) -> WaveguideLineProfile:
    """Return a sampled one-frequency pressure profile for one waveguide."""

    return _waveguide_sample_profile_quantity(
        point,
        system,
        waveguide_id,
        points,
        quantity="pressure",
    )


def waveguide_line_profile_volume_velocity(
    point: SolvedFrequencyPoint,
    system: AssembledSystem,
    waveguide_id: str,
    points: int,
) -> WaveguideLineProfile:
    """Return a sampled one-frequency volume-velocity profile for one waveguide."""

    return _waveguide_sample_profile_quantity(
        point,
        system,
        waveguide_id,
        points,
        quantity="volume_velocity",
    )


def waveguide_line_profile_particle_velocity(
    point: SolvedFrequencyPoint,
    system: AssembledSystem,
    waveguide_id: str,
    points: int,
) -> WaveguideLineProfile:
    """Return a sampled one-frequency particle-velocity profile for one waveguide."""

    return _waveguide_sample_profile_quantity(
        point,
        system,
        waveguide_id,
        points,
        quantity="particle_velocity",
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

    waveguide_ids = tuple(points[0].waveguide_endpoint_flow.keys())
    waveguide_endpoint_flow = {
        waveguide_id: WaveguideEndpointFlowSweep(
            node_a=np.array(
                [point.waveguide_endpoint_flow[waveguide_id].node_a for point in points],
                dtype=np.complex128,
            ),
            node_b=np.array(
                [point.waveguide_endpoint_flow[waveguide_id].node_b for point in points],
                dtype=np.complex128,
            ),
        )
        for waveguide_id in waveguide_ids
    }
    waveguide_endpoint_velocity = {
        waveguide_id: WaveguideEndpointVelocitySweep(
            node_a=np.array(
                [point.waveguide_endpoint_velocity[waveguide_id].node_a for point in points],
                dtype=np.complex128,
            ),
            node_b=np.array(
                [point.waveguide_endpoint_velocity[waveguide_id].node_b for point in points],
                dtype=np.complex128,
            ),
        )
        for waveguide_id in waveguide_ids
    }

    return SolvedFrequencySweep(
        frequency_hz=frequency_hz.copy(),
        omega_rad_s=omega_rad_s,
        node_order=points[0].node_order,
        pressures=pressures,
        coil_current=coil_current,
        cone_velocity=cone_velocity,
        cone_displacement=cone_displacement,
        waveguide_endpoint_flow=waveguide_endpoint_flow,
        waveguide_endpoint_velocity=waveguide_endpoint_velocity,
        source_voltage_rms=model.driver.source_voltage_rms,
    )


def _radiator_observation_transfer(
    model_name: str,
    omega: float,
    distance_m: float,
    radiation_space: str | None = None,
) -> complex:
    if distance_m <= 0.0:
        raise ValueError("distance_m must be > 0")

    token = default_radiation_space_for_model(model_name) if radiation_space is None else normalize_radiation_space(radiation_space)
    scale = solid_angle_for_radiation_space(token) * distance_m
    return 1j * omega * RHO0 / scale


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
    radiation_space: str | None = None,
) -> np.ndarray:
    """Return complex on-axis far-field pressure for one radiator over a sweep."""

    element = _find_radiator_element(system, radiator_id)
    payload = element.payload
    assert isinstance(payload, RadiatorElement)

    node_pressures = sweep.pressures[:, element.node_a]
    observation_pressure = np.empty(len(sweep.frequency_hz), dtype=np.complex128)

    use_driver_front_kinematics = element.node_a == system.driver_front_index

    for idx, (omega, node_pressure) in enumerate(zip(sweep.omega_rad_s, node_pressures, strict=True)):
        if use_driver_front_kinematics:
            # Driver-front radiator follows the diaphragm kinematics directly.
            q_rad = sweep.cone_velocity[idx] * payload.area_m2
        else:
            # Passive mouth / port / terminus radiators must use the local
            # acoustic-node state, not the driver cone velocity.
            z_rad = radiator_impedance(payload.model, float(omega), payload.area_m2)
            q_rad = node_pressure / z_rad
        h_q = _radiator_observation_transfer(payload.model, float(omega), distance_m, radiation_space)
        observation_pressure[idx] = h_q * q_rad

    return observation_pressure


def radiator_spl(
    sweep: SolvedFrequencySweep,
    system: AssembledSystem,
    radiator_id: str,
    distance_m: float,
    radiation_space: str | None = None,
) -> np.ndarray:
    """Return one-radiator SPL in dB over a sweep."""

    p_obs = radiator_observation_pressure(sweep, system, radiator_id, distance_m, radiation_space)
    return 20.0 * np.log10(np.abs(p_obs) / P_REF)
