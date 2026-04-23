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
from os_lem.solve import (
    solve_frequency_point,
    waveguide_line_profile_particle_velocity,
    waveguide_line_profile_pressure,
    waveguide_line_profile_volume_velocity,
)


ACCEPTED_THREE_LAW_PROFILES = ("exponential", "tractrix", "hyperbolic")


def _named_flare_model(profile: str, *, segments: int = 12) -> dict:
    if profile == "exponential":
        model_dict = build_exponential_model_with_segments(segments)
    elif profile == "tractrix":
        model_dict = build_tractrix_model_with_segments(segments)
    elif profile == "hyperbolic":
        model_dict = build_hyperbolic_model_with_segments(segments)
    else:
        model_dict = copy.deepcopy(build_exponential_model_with_segments(segments))
        for element in model_dict["elements"]:
            if element.get("id") == "wg1":
                element["profile"] = profile
                break
    return model_dict


@pytest.mark.parametrize("profile", ACCEPTED_THREE_LAW_PROFILES)
def test_three_law_named_flare_contract_accepts_the_three_current_named_laws(profile: str) -> None:
    model, _ = normalize_model(_named_flare_model(profile))
    assert model.waveguides[0].profile == profile


@pytest.mark.parametrize("bad_profile", ["spherical", "Le Cleac'h", "", 123])
def test_three_law_named_flare_contract_still_rejects_non_contract_named_law_tokens(bad_profile) -> None:
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


def test_three_law_named_flare_contract_preserves_shared_profile_and_endpoint_observability_semantics() -> None:
    solved = {profile: _solve_shared_profile_contract(profile) for profile in ACCEPTED_THREE_LAW_PROFILES}

    for profile, payload in solved.items():
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

    exp = solved["exponential"]
    trx = solved["tractrix"]
    hyp = solved["hyperbolic"]

    np.testing.assert_allclose(exp["pressure"].x_m, trx["pressure"].x_m)
    np.testing.assert_allclose(exp["pressure"].x_m, hyp["pressure"].x_m)
    np.testing.assert_allclose(exp["areas"][[0, -1]], trx["areas"][[0, -1]])
    np.testing.assert_allclose(exp["areas"][[0, -1]], hyp["areas"][[0, -1]])

    assert np.max(np.abs(exp["areas"][1:-1] - trx["areas"][1:-1])) > 0.0
    assert np.max(np.abs(exp["areas"][1:-1] - hyp["areas"][1:-1])) > 0.0
    assert np.max(np.abs(trx["areas"][1:-1] - hyp["areas"][1:-1])) > 0.0
