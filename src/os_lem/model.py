"""Canonical normalized internal model types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Driver:
    id: str
    Re: float
    Le: float
    Bl: float
    Mms: float
    Cms: float
    Rms: float
    Sd: float
    node_front: str
    node_rear: str
    source_voltage_rms: float


@dataclass(slots=True)
class VolumeElement:
    id: str
    node: str
    value_m3: float


@dataclass(slots=True)
class DuctElement:
    id: str
    node_a: str
    node_b: str
    length_m: float
    area_m2: float
    loss: float | None = None


@dataclass(slots=True)
class Waveguide1DElement:
    id: str
    node_a: str
    node_b: str
    length_m: float
    area_start_m2: float
    area_end_m2: float
    profile: str
    segments: int = 8
    loss: float | None = None


@dataclass(slots=True)
class RadiatorElement:
    id: str
    node: str
    model: str
    area_m2: float


@dataclass(slots=True)
class Observation:
    id: str
    type: str
    data: dict[str, Any]


@dataclass(slots=True)
class NormalizedModel:
    driver: Driver
    volumes: list[VolumeElement] = field(default_factory=list)
    ducts: list[DuctElement] = field(default_factory=list)
    waveguides: list[Waveguide1DElement] = field(default_factory=list)
    radiators: list[RadiatorElement] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    node_order: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
