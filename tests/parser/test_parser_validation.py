from pathlib import Path

import pytest
import yaml

from os_lem.errors import SchemaError, ValidationError
from os_lem.parser import load_and_normalize, normalize_model


def _base_model():
    return {
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
                "id": "rear_box",
                "type": "volume",
                "node": "rear",
                "value": "18 l",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
        ],
    }


def test_unknown_top_level_field_rejected():
    model = _base_model()
    model["nonsense"] = 123
    with pytest.raises(SchemaError):
        normalize_model(model)


def test_unknown_element_field_rejected():
    model = _base_model()
    model["elements"][0]["oops"] = 1
    with pytest.raises(ValidationError):
        normalize_model(model)


def test_duplicate_ids_rejected():
    model = _base_model()
    model["elements"][1]["id"] = "front_rad"
    with pytest.raises(ValidationError):
        normalize_model(model)


def test_missing_observation_target_rejected():
    model = _base_model()
    model["observations"].append({"id": "p1", "type": "node_pressure", "target": "ghost"})
    with pytest.raises(ValidationError):
        normalize_model(model)


def test_parallel_paths_are_legal():
    model = _base_model()
    model["elements"].append(
        {
            "id": "d1",
            "type": "duct",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "10 cm",
            "area": "10 cm2",
        }
    )
    model["elements"].append(
        {
            "id": "d2",
            "type": "duct",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "10 cm",
            "area": "10 cm2",
        }
    )
    model["elements"].append(
        {
            "id": "mouth_rad",
            "type": "radiator",
            "node": "mouth",
            "model": "unflanged_piston",
            "area": "20 cm2",
        }
    )
    normalized, _ = normalize_model(model)
    assert len(normalized.ducts) == 2


def test_floating_component_without_shunt_rejected():
    model = _base_model()
    model["elements"].append(
        {
            "id": "d1",
            "type": "duct",
            "node_a": "x1",
            "node_b": "x2",
            "length": "10 cm",
            "area": "10 cm2",
        }
    )
    with pytest.raises(ValidationError):
        normalize_model(model)


def test_examples_load(example_root=Path("examples")):
    for path in example_root.glob("*/model.yaml"):
        normalized, warnings = load_and_normalize(path)
        assert normalized.driver.id == "drv1"
        assert isinstance(warnings, list)
