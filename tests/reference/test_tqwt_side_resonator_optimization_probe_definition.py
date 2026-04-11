from os_lem.reference_tqwt_side_resonator_optimization_probe import (
    ProbeParameters,
    ResonatorType,
    compute_probe_score,
    phase1_execution_plan,
    render_probe_yaml,
    validate_probe_parameters,
)


def test_validate_chamber_neck_accepts_bounded_parameters() -> None:
    params = ProbeParameters(
        x_attach_norm=0.42,
        resonator_type=ResonatorType.CHAMBER_NECK,
        l_res_m=0.30,
        s_res_m2=8.0e-4,
        v_res_m3=3.0e-3,
    )
    assert validate_probe_parameters(params) == []


def test_validate_rejects_out_of_bounds_attach() -> None:
    params = ProbeParameters(
        x_attach_norm=0.95,
        resonator_type=ResonatorType.CHAMBER_NECK,
        l_res_m=0.30,
        s_res_m2=8.0e-4,
        v_res_m3=3.0e-3,
    )
    errors = validate_probe_parameters(params)
    assert any("x_attach_norm out of bounds" in error for error in errors)


def test_validate_side_pipe_rejects_non_null_volume() -> None:
    params = ProbeParameters(
        x_attach_norm=0.50,
        resonator_type=ResonatorType.SIDE_PIPE,
        l_res_m=0.25,
        s_res_m2=1.2e-3,
        v_res_m3=2.0e-3,
    )
    errors = validate_probe_parameters(params)
    assert any("v_res_m3 must be None or 0.0" in error for error in errors)


def test_compute_probe_score_has_zero_penalties_when_within_limits() -> None:
    score = compute_probe_score(
        spl_band_db=[84.0, 84.5, 84.0, 83.8, 84.2],
        excursion_band_mm=[2.0, 2.5, 3.1, 2.9, 2.2],
        baseline_mean_spl_band_db=84.0,
        geometry_is_valid=True,
    )
    assert score.excursion_penalty == 0.0
    assert score.output_penalty == 0.0
    assert score.geometry_penalty == 0.0
    assert score.total_score >= 0.0


def test_compute_probe_score_adds_penalties_explicitly() -> None:
    score = compute_probe_score(
        spl_band_db=[80.0, 81.0, 79.0, 80.5, 79.5],
        excursion_band_mm=[4.8, 5.0, 4.4, 4.6, 4.9],
        baseline_mean_spl_band_db=84.0,
        geometry_is_valid=False,
    )
    assert score.excursion_penalty > 0.0
    assert score.output_penalty > 0.0
    assert score.geometry_penalty == 1_000_000.0
    assert score.total_score > 1_000_000.0


def test_render_probe_yaml_emits_type_and_core_parameters() -> None:
    params = ProbeParameters(
        x_attach_norm=0.40,
        resonator_type=ResonatorType.SIDE_PIPE,
        l_res_m=0.22,
        s_res_m2=1.1e-3,
    )
    rendered = render_probe_yaml(params)
    assert "resonator_type: side_pipe" in rendered
    assert "x_attach_norm: 0.4" in rendered
    assert "V_res_m3: null" in rendered


def test_phase1_execution_plan_is_frozen_and_reproducible() -> None:
    plan = phase1_execution_plan()
    assert plan == {
        "method": "random_uniform",
        "seed": 2026,
        "samples_per_resonator_type": 256,
        "total_samples": 512,
    }
