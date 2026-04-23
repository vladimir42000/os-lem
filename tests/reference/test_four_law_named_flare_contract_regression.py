from __future__ import annotations

import copy

import numpy as np
import pytest

from os_lem.assemble import assemble_system
from os_lem.elements.waveguide_1d import area_at_position
from os_lem.parser import ValidationError, normalize_model
from os_lem.reference_exponential_flare_smoke import build_exponential_model_with_segments
from os_lem.reference_tractrix_flare_smoke import build_tractrix_model_with_segments
from os_lem.reference_hyperbolic_flare_smoke import build_hyperbolic_model_with_segments
from os_lem.reference_parabolic_flare_smoke import build_parabolic_model_with_segments
from os_lem.solve import (
    solve_frequency_point,
    waveguide_line_profile_particle_velocity,
    waveguide_line_profile_pressure,
    waveguide_line_profile_volume_velocity,
)


ACCEPTED_FOUR_LAW_PROFILES = ("exponential", "tractrix", "hyperbolic", "parabolic")


def _named_flare_model(profile: str, *, segments: int = 12) -> dict:
    if profile == "exponential":
        model_dict = build_exponential_model_with_segments(segments)
    elif profile == "tractrix":
        model_dict = build_tractrix_model_with_segments(segments)
    elif profile == "hyperbolic":
        model_dict = build_hyperbolic_model_with_segments(segments)
    elif profile == "parabolic":
        model_dict = build_parabolic_model_with_segments(segments)
    else:
        model_dict = copy.deepcopy(build_exponential_model_with_segments(segments))
        for element in model_dict["elements"]:
            if element.get("id") == "wg1":
                element["profile"] = profile
                break
    return model_dict


@pytest.mark.parametrize("profile", ACCEPTED_FOUR_LAW_PROFILES)
def test_four_law_named_flare_contract_accepts_the_four_current_named_laws(profile: str) -> None:
    model, _ = normalize_model(_named_flare_model(profile))
    assert model.waveguides[0].profile == profile


@pytest.mark.parametrize("bad_profile", ["spherical", "Le Cleac'h", "", 123])
def test_four_law_named_flare_contract_still_rejects_non_contract_named_law_tokens(bad_profile) -> None:
    with pytest.raises((ValidationError, TypeError, ValueError)):
        normalize_model(_named_flare_model(bad_profile))


def _solve_shared_profile_contract(profile: str) -> dict:
    model, _ = normalize_model(_named_flare_model(profile, segments=12))
    system = assemble_system(model)
    point = solve_frequency_point(model, system, 120.0)
    pressure = waveguide_line_profile_pressure(point, system, "wg1", points=13)
    flow = waveguide_line_profile_volume_velocity(point, system, "wg1", points=13)
    particle = waveguide_line_profile_particle_velocity(point, system, "wg1", points=13)
    waveguide = model.waveguides[0]
    idx = {name: i for i, name in enumerate(system.node_order)}
    areas = np.array(
        [
            area_at_position(
                waveguide.length_m,
                waveguide.area_start_m2,
                waveguide.area_end_m2,
                float(x_m),
                profile=waveguide.profile,
            )
            for x_m in flow.x_m
        ],
        dtype=float,
    )
    return {
        "model": model,
        "system": system,
        "point": point,
        "pressure": pressure,
        "flow": flow,
        "particle": particle,
        "areas": areas,
        "node_index": idx,
    }


def test_four_law_named_flare_contract_preserves_shared_profile_and_endpoint_observability_semantics() -> None:
    solved = {profile: _solve_shared_profile_contract(profile) for profile in ACCEPTED_FOUR_LAW_PROFILES}

    for payload in solved.values():
        point = payload["point"]
        pressure = payload["pressure"]
        flow = payload["flow"]
        particle = payload["particle"]
        areas = payload["areas"]
        idx = payload["node_index"]

        assert np.all(np.isfinite(pressure.values.real))
        assert np.all(np.isfinite(pressure.values.imag))
        assert np.all(np.isfinite(flow.values.real))
        assert np.all(np.isfinite(flow.values.imag))
        assert np.all(np.isfinite(particle.values.real))
        assert np.all(np.isfinite(particle.values.imag))

        np.testing.assert_allclose(pressure.x_m, flow.x_m)
        np.testing.assert_allclose(flow.x_m, particle.x_m)
        np.testing.assert_allclose(pressure.values[0], point.pressures[idx["rear"]])
        np.testing.assert_allclose(pressure.values[-1], point.pressures[idx["mouth"]])
        np.testing.assert_allclose(flow.values[0], point.waveguide_endpoint_flow["wg1"].node_a)
        np.testing.assert_allclose(flow.values[-1], -point.waveguide_endpoint_flow["wg1"].node_b)
        np.testing.assert_allclose(particle.values[0], point.waveguide_endpoint_velocity["wg1"].node_a)
        np.testing.assert_allclose(particle.values[-1], -point.waveguide_endpoint_velocity["wg1"].node_b)
        np.testing.assert_allclose(particle.values, flow.values / areas)
        np.testing.assert_allclose(areas[0], payload["model"].waveguides[0].area_start_m2)
        np.testing.assert_allclose(areas[-1], payload["model"].waveguides[0].area_end_m2)

    first = solved[ACCEPTED_FOUR_LAW_PROFILES[0]]
    for profile in ACCEPTED_FOUR_LAW_PROFILES[1:]:
        payload = solved[profile]
        np.testing.assert_allclose(first["pressure"].x_m, payload["pressure"].x_m)
        np.testing.assert_allclose(first["areas"][[0, -1]], payload["areas"][[0, -1]])

    for i, left in enumerate(ACCEPTED_FOUR_LAW_PROFILES):
        for right in ACCEPTED_FOUR_LAW_PROFILES[i + 1 :]:
            assert np.max(np.abs(solved[left]["areas"][1:-1] - solved[right]["areas"][1:-1])) > 0.0
