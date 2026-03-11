"""Minimal frequency-domain acoustic matrix build for Session 6 Patch 2."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .assemble import AssembledSystem
from .elements.duct import duct_admittance
from .elements.radiator import radiator_impedance
from .elements.volume import volume_admittance
from .model import DuctElement, RadiatorElement, VolumeElement


@dataclass(slots=True, frozen=True)
class AcousticMatrixBuild:
    """Acoustic nodal matrix for one frequency."""

    frequency_hz: float
    omega_rad_s: float
    Yaa: np.ndarray


def build_acoustic_matrix(system: AssembledSystem, frequency_hz: float) -> AcousticMatrixBuild:
    """Build the acoustic nodal admittance matrix for one frequency.

    Supported stamps in Patch 2:
    - volume: shunt admittance to reference
    - radiator: shunt admittance to reference
    - duct: branch admittance between two acoustic nodes
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
        if element.kind != "duct":
            raise RuntimeError(f"unsupported branch element kind {element.kind!r}")

        payload = element.payload
        assert isinstance(payload, DuctElement)
        y = duct_admittance(omega, payload.length_m, payload.area_m2)

        i = element.node_a
        j = element.node_b
        assert j is not None

        Yaa[i, i] += y
        Yaa[j, j] += y
        Yaa[i, j] -= y
        Yaa[j, i] -= y

    return AcousticMatrixBuild(
        frequency_hz=frequency_hz,
        omega_rad_s=omega,
        Yaa=Yaa,
    )
