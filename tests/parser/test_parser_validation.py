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


def test_duct_loss_is_rejected_as_unsupported_current_checkpoint():
    model = _base_model()
    model["elements"].append(
        {
            "id": "d1",
            "type": "duct",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "10 cm",
            "area": "10 cm2",
            "loss": 0.1,
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
    with pytest.raises(ValidationError, match="duct.loss"):
        normalize_model(model)


def test_waveguide_loss_is_accepted_for_cylindrical_and_conical_cases():
    model = _base_model()
    model["elements"].append(
        {
            "id": "wg1",
            "type": "waveguide_1d",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "20 cm",
            "area_start": "10 cm2",
            "area_end": "10 cm2",
            "profile": "conical",
            "segments": 4,
            "loss": 0.15,
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
    assert normalized.waveguides[0].loss == pytest.approx(0.15)

    model = _base_model()
    model["elements"].append(
        {
            "id": "wg1",
            "type": "waveguide_1d",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "20 cm",
            "area_start": "10 cm2",
            "area_end": "20 cm2",
            "profile": "conical",
            "segments": 4,
            "loss": 0.15,
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
    assert normalized.waveguides[0].loss == pytest.approx(0.15)

    model = _base_model()
    model["elements"].append(
        {
            "id": "wg1",
            "type": "waveguide_1d",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "20 cm",
            "area_start": "10 cm2",
            "area_end": "20 cm2",
            "profile": "conical",
            "segments": 4,
            "loss": 0.0,
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
    assert normalized.waveguides[0].loss == pytest.approx(0.0)


def test_waveguide_loss_rejects_negative_values():
    model = _base_model()
    model["elements"].append(
        {
            "id": "wg1",
            "type": "waveguide_1d",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "20 cm",
            "area_start": "10 cm2",
            "area_end": "20 cm2",
            "profile": "conical",
            "segments": 4,
            "loss": -0.1,
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
    with pytest.raises(ValidationError, match="must be >= 0"):
        normalize_model(model)


def test_meta_radiation_space_is_accepted_and_invalid_token_rejected():
    model = _base_model()
    model["meta"] = {"name": "demo", "radiation_space": "2pi"}
    normalized, warnings = normalize_model(model)
    assert normalized.metadata["radiation_space"] == "2pi"
    assert warnings == []

    model["meta"]["radiation_space"] = "3pi"
    with pytest.raises(ValidationError, match="Unsupported radiation_space"):
        normalize_model(model)


def test_spl_sum_warns_when_mixed_radiation_spaces_are_resolved():
    model = _base_model()
    model["elements"].append(
        {
            "id": "port",
            "type": "duct",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "20 cm",
            "area": "20 cm2",
        }
    )
    model["elements"].append(
        {
            "id": "port_rad",
            "type": "radiator",
            "node": "mouth",
            "model": "unflanged_piston",
            "area": "20 cm2",
        }
    )
    model["observations"] = [
        {
            "id": "spl_total",
            "type": "spl_sum",
            "terms": [
                {"target": "front_rad", "distance": "1 m"},
                {"target": "port_rad", "distance": "1 m"},
            ],
        }
    ]
    _, warnings = normalize_model(model)
    assert any("different radiation_space values" in warning for warning in warnings)


def test_spl_sum_parent_radiation_space_suppresses_mixed_space_warning():
    model = _base_model()
    model["elements"].append(
        {
            "id": "port",
            "type": "duct",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "20 cm",
            "area": "20 cm2",
        }
    )
    model["elements"].append(
        {
            "id": "port_rad",
            "type": "radiator",
            "node": "mouth",
            "model": "unflanged_piston",
            "area": "20 cm2",
        }
    )
    model["observations"] = [
        {
            "id": "spl_total",
            "type": "spl_sum",
            "radiation_space": "2pi",
            "terms": [
                {"target": "front_rad", "distance": "1 m"},
                {"target": "port_rad", "distance": "1 m"},
            ],
        }
    ]
    _, warnings = normalize_model(model)
    assert warnings == []


def test_element_observable_rejects_volume_target():
    model = _base_model()
    model["observations"] = [
        {"id": "rear_q", "type": "element_volume_velocity", "target": "rear_box"},
    ]
    with pytest.raises(ValidationError, match="requires target element type duct, radiator, or waveguide_1d"):
        normalize_model(model)


def test_waveguide_element_observable_requires_explicit_location():
    model = _base_model()
    model["elements"].append(
        {
            "id": "rear_line",
            "type": "waveguide_1d",
            "node_a": "rear",
            "node_b": "mouth",
            "length": "1.6 m",
            "area_start": "132 cm2",
            "area_end": "132 cm2",
            "profile": "conical",
            "segments": 8,
        }
    )
    model["elements"].append(
        {
            "id": "mouth_rad",
            "type": "radiator",
            "node": "mouth",
            "model": "unflanged_piston",
            "area": "132 cm2",
        }
    )
    model["observations"] = [
        {"id": "rear_q", "type": "element_volume_velocity", "target": "rear_line"},
    ]
    with pytest.raises(ValidationError, match="requires location 'a' or 'b'"):
        normalize_model(model)

    model["observations"][0]["location"] = "c"
    with pytest.raises(ValidationError, match="requires location 'a' or 'b'"):
        normalize_model(model)


def test_non_waveguide_element_observable_rejects_location():
    model = _base_model()
    model["observations"] = [
        {"id": "front_v", "type": "element_particle_velocity", "target": "front_rad", "location": "a"},
    ]
    with pytest.raises(ValidationError, match="does not accept location"):
        normalize_model(model)
