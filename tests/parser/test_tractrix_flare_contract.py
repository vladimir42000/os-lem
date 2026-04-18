from __future__ import annotations

import pytest

from os_lem.parser import ValidationError, normalize_model


def _base_model(profile: str, *, area_start: str = "10 cm2", area_end: str = "50 cm2") -> dict:
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
            {"id": "front_rad", "type": "radiator", "node": "front", "model": "infinite_baffle_piston", "area": "132 cm2"},
            {"id": "rear_vol", "type": "volume", "node": "rear", "value": "18 l"},
            {
                "id": "wg1",
                "type": "waveguide_1d",
                "node_a": "rear",
                "node_b": "mouth",
                "length": "40 cm",
                "area_start": area_start,
                "area_end": area_end,
                "profile": profile,
                "segments": 12,
            },
            {"id": "mouth_rad", "type": "radiator", "node": "mouth", "model": "unflanged_piston", "area": area_end},
        ],
        "observations": [{"id": "zin", "type": "input_impedance", "target": "drv1"}],
    }


def test_parser_accepts_tractrix_named_flare_contract() -> None:
    model, _ = normalize_model(_base_model("tractrix"))
    assert model.waveguides[0].profile == "tractrix"


@pytest.mark.parametrize("bad_profile", ["parabolic", "", 123])
def test_parser_rejects_non_contract_named_flare_tokens_after_tractrix_opening(bad_profile) -> None:
    with pytest.raises((ValidationError, TypeError, ValueError)):
        normalize_model(_base_model(bad_profile))


def test_parser_rejects_contract_breaking_tractrix_contraction() -> None:
    with pytest.raises(ValidationError, match="tractrix requires area_end >= area_start"):
        normalize_model(_base_model("tractrix", area_start="50 cm2", area_end="10 cm2"))
