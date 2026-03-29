from __future__ import annotations

from pathlib import Path

import yaml

from os_lem.api import LineProfileResult, get_frontend_contract_v1, run_simulation


ROOT = Path(__file__).resolve().parents[2]


def test_get_frontend_contract_v1_declares_stable_and_experimental_surface() -> None:
    manifest = get_frontend_contract_v1()

    assert manifest["contract_name"] == "os_lem_frontend_contract_v1"
    assert manifest["contract_version"] == 1
    assert manifest["api_function"] == "run_simulation"
    assert manifest["machine_readable_function"] == "get_frontend_contract_v1"

    stable = manifest["stable"]
    experimental = manifest["experimental"]

    assert "waveguide_1d" in stable["element_types"]
    assert "line_profile" in stable["observation_types"]
    assert stable["stable_workflows"] == [
        "closed_box_with_front_radiator",
        "single_rear_conical_line_with_one_mouth_radiator",
    ]
    assert "dual_junction_split_merge_horn_skeletons" in experimental["topology_openings"]
    assert "stable" not in experimental["note"].lower()


def test_get_frontend_contract_v1_returns_a_defensive_copy() -> None:
    manifest = get_frontend_contract_v1()
    manifest["stable"]["driver_models"].append("broken")

    fresh = get_frontend_contract_v1()
    assert "broken" not in fresh["stable"]["driver_models"]


def test_frontend_contract_examples_match_manifest_and_run() -> None:
    manifest = get_frontend_contract_v1()

    for example in manifest["stable"]["canonical_examples"]:
        path = ROOT / example["path"]
        assert path.exists(), path
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        result = run_simulation(data, [20.0, 50.0, 100.0])
        assert set(result.series) == {obs["id"] for obs in data["observations"]}
        assert result.frequencies_hz.shape == (3,)
        assert result.units

        if example["id"] == "closed_box_minimal":
            assert result.zin_mag_ohm is not None
            assert result.cone_excursion_mm is not None
        if example["id"] == "conical_line_minimal":
            profile = result.get_series("mouth_profile")
            assert isinstance(profile, LineProfileResult)
            assert profile.quantity == "pressure"
            assert profile.values.shape == (5,)


def test_frontend_contract_docs_exist() -> None:
    assert (ROOT / "docs/frontend_api.md").exists()
    assert (ROOT / "docs/input_format.md").exists()
    assert (ROOT / "docs/frontend_handoff.md").exists()
    assert (ROOT / "examples/frontend_contract_v1/README.md").exists()
