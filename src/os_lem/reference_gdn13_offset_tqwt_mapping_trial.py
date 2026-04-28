"""Bounded GDN 13 offset-driver TQWT HornResp mapping trial.

This module supports exactly one v0.8.0 mapping trial:
- one operator-supplied Tonsil GDN 13/40/8 HornResp definition
- one operator-supplied HornResp response table
- one explicit os-lem model_dict construction
- one honest SPL / electrical impedance comparison report

It is intentionally not a HornResp importer, not an optimizer bridge, and not a
general topology framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from os_lem.api import run_simulation


@dataclass(frozen=True)
class Gdn13DriverDerivedParameters:
    """Driver parameters used in the explicit os-lem ts_classic mapping."""

    re_ohm: float
    le_mh: float
    sd_cm2: float
    bl_tm: float
    cms_m_per_n: float
    rms_mechanical: float
    mmd_g: float
    fs_hz: float
    qes: float
    qms: float
    vas_l: float


def parse_hornresp_definition_sections(path: str | Path) -> dict[str, dict[str, float]]:
    """Parse only the fixed sections needed to verify the supplied GDN13 fixture.

    This is deliberately narrow fixture validation for this mapping trial. It is
    not a general HornResp model parser.
    """

    text = Path(path).read_text(encoding="utf-8")
    sections: dict[str, dict[str, float]] = {}
    active: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("|"):
            if "TRADITIONAL DRIVER PARAMETER VALUES" in line:
                active = "traditional_driver"
                sections[active] = {}
            elif "ABSORBENT FILLING MATERIAL PARAMETER VALUES" in line:
                active = "absorbent"
                sections[active] = {}
            elif "RADIATION, SOURCE AND MOUTH PARAMETER VALUES" in line:
                active = "radiation_source_mouth"
                sections[active] = {}
            elif "HORN PARAMETER VALUES" in line:
                active = "horn"
                sections[active] = {}
            elif active is not None:
                active = None
            continue

        if active is None or "=" not in line:
            continue

        key, value = [part.strip() for part in line.split("=", 1)]
        # Keep the first duplicate S2/Par entries out of this fixed verifier;
        # the explicit model below owns the intended two-section interpretation.
        try:
            sections[active].setdefault(key, float(value.split()[0]))
        except (ValueError, IndexError):
            continue

    return sections


def load_hornresp_gdn13_response_table(path: str | Path) -> dict[str, np.ndarray]:
    """Load the fixed HornResp response table columns used by this trial."""

    frequencies: list[float] = []
    spl_db: list[float] = []
    ze_ohm: list[float] = []

    with Path(path).open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("Freq"):
                continue
            parts = line.split()
            if len(parts) < 16:
                continue
            try:
                frequency = float(parts[0])
                spl = float(parts[4])
                ze = float(parts[5])
            except ValueError:
                continue
            frequencies.append(frequency)
            spl_db.append(spl)
            ze_ohm.append(ze)

    if not frequencies:
        raise ValueError(f"no HornResp response rows could be read from {path}")

    frequency_hz = np.asarray(frequencies, dtype=float)
    spl_array = np.asarray(spl_db, dtype=float)
    ze_array = np.asarray(ze_ohm, dtype=float)

    if frequency_hz.ndim != 1 or spl_array.shape != frequency_hz.shape or ze_array.shape != frequency_hz.shape:
        raise ValueError("HornResp table columns are not one-dimensional aligned arrays")
    if not np.all(np.isfinite(frequency_hz)):
        raise ValueError("HornResp frequency column contains non-finite values")
    if not np.all(np.isfinite(spl_array)):
        raise ValueError("HornResp SPL column contains non-finite values")
    if not np.all(np.isfinite(ze_array)):
        raise ValueError("HornResp Ze column contains non-finite values")

    return {
        "frequency_hz": frequency_hz,
        "spl_db": spl_array,
        "ze_ohm": ze_array,
    }


def gdn13_hornresp_driver_derived_parameters() -> Gdn13DriverDerivedParameters:
    """Return HornResp driver inputs plus the ts_classic values used by os-lem."""

    re_ohm = 6.50
    le_mh = 1.00
    sd_cm2 = 82.00
    bl_tm = 6.16
    cms_m_per_n = 1.01e-3
    rms_mechanical = 0.49
    mmd_g = 8.50

    mmd_kg = mmd_g / 1000.0
    sd_m2 = sd_cm2 * 1.0e-4
    fs_hz = 1.0 / (2.0 * pi * sqrt(mmd_kg * cms_m_per_n))
    qms = (2.0 * pi * fs_hz * mmd_kg) / rms_mechanical
    qes = (2.0 * pi * fs_hz * mmd_kg * re_ohm) / (bl_tm * bl_tm)

    # Same bounded derivation used only to express the HornResp inputs through
    # os-lem's existing ts_classic driver surface.
    rho0 = 1.184
    c0 = 343.0
    vas_m3 = rho0 * c0 * c0 * sd_m2 * sd_m2 * cms_m_per_n
    vas_l = vas_m3 * 1000.0

    return Gdn13DriverDerivedParameters(
        re_ohm=re_ohm,
        le_mh=le_mh,
        sd_cm2=sd_cm2,
        bl_tm=bl_tm,
        cms_m_per_n=cms_m_per_n,
        rms_mechanical=rms_mechanical,
        mmd_g=mmd_g,
        fs_hz=fs_hz,
        qes=qes,
        qms=qms,
        vas_l=vas_l,
    )


def _fmt_m(value: float) -> str:
    return f"{value:.6g} m"


def _fmt_m2(value: float) -> str:
    return f"{value:.6g} m2"


def build_gdn13_offset_tqwt_model_dict(*, profile: str = "parabolic") -> dict[str, Any]:
    """Build the one explicit os-lem model_dict for this GDN13 TQWT trial."""

    if profile not in {"parabolic", "conical"}:
        raise ValueError("this bounded mapping trial supports only parabolic primary and conical diagnostic profiles")

    driver = gdn13_hornresp_driver_derived_parameters()

    # HornResp areas are in cm^2 and lengths are in cm.
    s1_m2 = 96.00e-4
    s2_m2 = 98.06e-4
    s3_m2 = 102.00e-4
    rear_stub_length_m = 55.80e-2
    forward_line_length_m = 106.46e-2

    return {
        "meta": {
            "name": "gdn13_offset_tqwt_hornresp_mapping_trial",
            "source": "operator_supplied_hornresp_gdn13_offset_tqwt",
            "radiation_space": "2pi",
            "mapping_trial_only": True,
        },
        "driver": {
            "id": "drv_gdn13",
            "model": "ts_classic",
            "Re": f"{driver.re_ohm:.6g} ohm",
            "Le": f"{driver.le_mh:.6g} mH",
            "Fs": f"{driver.fs_hz:.6g} Hz",
            "Qes": driver.qes,
            "Qms": driver.qms,
            "Vas": f"{driver.vas_l:.6g} l",
            "Sd": f"{driver.sd_cm2:.6g} cm2",
            "node_front": "driver_front",
            "node_rear": "tap_s2",
        },
        "elements": [
            {
                "id": "driver_front_radiation_diagnostic",
                "type": "radiator",
                "node": "driver_front",
                "model": "infinite_baffle_piston",
                "area": f"{driver.sd_cm2:.6g} cm2",
            },
            {
                "id": "rear_closed_stub_s1_to_s2",
                "type": "waveguide_1d",
                "node_a": "closed_end_s1",
                "node_b": "tap_s2",
                "length": _fmt_m(rear_stub_length_m),
                "area_start": _fmt_m2(s1_m2),
                "area_end": _fmt_m2(s2_m2),
                "profile": profile,
                "segments": 8,
            },
            {
                "id": "forward_open_line_s2_to_s3",
                "type": "waveguide_1d",
                "node_a": "tap_s2",
                "node_b": "mouth_s3",
                "length": _fmt_m(forward_line_length_m),
                "area_start": _fmt_m2(s2_m2),
                "area_end": _fmt_m2(s3_m2),
                "profile": profile,
                "segments": 16,
            },
            {
                "id": "mouth_s3_radiation",
                "type": "radiator",
                "node": "mouth_s3",
                "model": "unflanged_piston",
                "area": _fmt_m2(s3_m2),
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv_gdn13"},
            {
                "id": "spl_mouth",
                "type": "spl",
                "target": "mouth_s3_radiation",
                "distance": "1 m",
                "radiation_space": "2pi",
            },
            {
                "id": "spl_total_diagnostic",
                "type": "spl_sum",
                "radiation_space": "2pi",
                "terms": [
                    {"target": "driver_front_radiation_diagnostic", "distance": "1 m"},
                    {"target": "mouth_s3_radiation", "distance": "1 m"},
                ],
            },
        ],
    }


def _metric_summary(delta: np.ndarray) -> dict[str, float]:
    return {
        "max_abs": float(np.max(np.abs(delta))),
        "mean_abs": float(np.mean(np.abs(delta))),
        "rms": float(np.sqrt(np.mean(delta * delta))),
    }


def _peak_summary(frequency_hz: np.ndarray, values: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    masked_frequency = frequency_hz[mask]
    masked_values = values[mask]
    index = int(np.argmax(masked_values))
    return {
        "frequency_hz": float(masked_frequency[index]),
        "value": float(masked_values[index]),
    }


def _interpret_mapping(
    *,
    hornresp_peak_hz: float,
    oslem_peak_hz: float,
    impedance_low_mean_abs_ohm: float,
    spl_low_mean_abs_db: float,
    spl_low_zero_mean_mae_db: float,
    spl_low_level_shift_db: float,
) -> str:
    if hornresp_peak_hz <= 0.0 or oslem_peak_hz <= 0.0:
        return "undetermined_nonpositive_peak_frequency"
    octave_peak_error = abs(np.log2(oslem_peak_hz / hornresp_peak_hz))
    if octave_peak_error > 0.35 or impedance_low_mean_abs_ohm > 20.0:
        return "topology_or_driver_electrical_mapping_mismatch_likely"
    if spl_low_zero_mean_mae_db <= 6.0 and abs(spl_low_level_shift_db) > 6.0:
        return "spl_observation_or_radiation_output_convention_unresolved"
    if spl_low_mean_abs_db > 6.0:
        return "spl_observation_or_radiation_output_convention_unresolved"
    return "bounded_mapping_trial_no_large_first_order_mismatch_detected"


def evaluate_gdn13_offset_tqwt_mapping_trial(
    *,
    hornresp_definition_path: str | Path,
    hornresp_response_path: str | Path,
    profile: str = "parabolic",
) -> dict[str, Any]:
    """Run os-lem for the one GDN13 mapping trial and compare to HornResp."""

    definition_sections = parse_hornresp_definition_sections(hornresp_definition_path)
    traditional = definition_sections.get("traditional_driver", {})
    absorbent = definition_sections.get("absorbent", {})

    if float(traditional.get("Le", -1.0)) != 1.0:
        raise ValueError("expected latest HornResp fixture with traditional Le = 1.00 mH")
    if float(absorbent.get("Tal1", -1.0)) != 0.0 or float(absorbent.get("Tal2", -1.0)) != 0.0:
        raise ValueError("expected latest HornResp fixture with Tal1 = Tal2 = 0")

    hornresp = load_hornresp_gdn13_response_table(hornresp_response_path)
    frequency_hz = hornresp["frequency_hz"]
    hornresp_spl_db = hornresp["spl_db"]
    hornresp_ze_ohm = hornresp["ze_ohm"]

    model_dict = build_gdn13_offset_tqwt_model_dict(profile=profile)
    result_a = run_simulation(model_dict, frequency_hz)
    result_b = run_simulation(model_dict, frequency_hz)

    if result_a.zin_complex_ohm is None or result_b.zin_complex_ohm is None:
        raise RuntimeError("os-lem did not return input impedance for the GDN13 mapping trial")
    if "spl_mouth" not in result_a.series or "spl_mouth" not in result_b.series:
        raise RuntimeError("os-lem did not return the spl_mouth observation for the GDN13 mapping trial")

    oslem_spl_db = np.asarray(result_a.series["spl_mouth"], dtype=float)
    oslem_spl_repeat_db = np.asarray(result_b.series["spl_mouth"], dtype=float)
    oslem_ze_ohm = np.abs(np.asarray(result_a.zin_complex_ohm, dtype=complex))
    oslem_ze_repeat_ohm = np.abs(np.asarray(result_b.zin_complex_ohm, dtype=complex))

    if np.asarray(result_a.frequencies_hz).shape != frequency_hz.shape:
        raise RuntimeError("os-lem frequency vector shape does not match HornResp table")
    if oslem_spl_db.shape != frequency_hz.shape or oslem_ze_ohm.shape != frequency_hz.shape:
        raise RuntimeError("os-lem output shape does not match HornResp table")
    if not np.all(np.isfinite(oslem_spl_db)):
        raise RuntimeError("os-lem SPL output contains non-finite values")
    if not np.all(np.isfinite(oslem_ze_ohm)):
        raise RuntimeError("os-lem impedance output contains non-finite values")

    np.testing.assert_allclose(oslem_spl_db, oslem_spl_repeat_db, rtol=1.0e-12, atol=1.0e-12)
    np.testing.assert_allclose(oslem_ze_ohm, oslem_ze_repeat_ohm, rtol=1.0e-12, atol=1.0e-12)

    low_mask = frequency_hz <= 600.0
    if int(np.count_nonzero(low_mask)) < 10:
        raise RuntimeError("HornResp table has too few low-frequency rows for the required trial metrics")

    impedance_delta = oslem_ze_ohm - hornresp_ze_ohm
    spl_delta = oslem_spl_db - hornresp_spl_db
    spl_low_delta = spl_delta[low_mask]
    oslem_spl_low_centered = oslem_spl_db[low_mask] - float(np.mean(oslem_spl_db[low_mask]))
    hornresp_spl_low_centered = hornresp_spl_db[low_mask] - float(np.mean(hornresp_spl_db[low_mask]))
    spl_low_zero_mean_delta = oslem_spl_low_centered - hornresp_spl_low_centered

    hornresp_peak = _peak_summary(frequency_hz, hornresp_ze_ohm, low_mask)
    oslem_peak = _peak_summary(frequency_hz, oslem_ze_ohm, low_mask)
    impedance_low = _metric_summary(impedance_delta[low_mask])
    spl_low = _metric_summary(spl_low_delta)
    spl_full = _metric_summary(spl_delta)
    spl_low_zero_mean = _metric_summary(spl_low_zero_mean_delta)
    spl_low_level_shift_db = float(np.mean(spl_low_delta))

    interpretation = _interpret_mapping(
        hornresp_peak_hz=hornresp_peak["frequency_hz"],
        oslem_peak_hz=oslem_peak["frequency_hz"],
        impedance_low_mean_abs_ohm=impedance_low["mean_abs"],
        spl_low_mean_abs_db=spl_low["mean_abs"],
        spl_low_zero_mean_mae_db=spl_low_zero_mean["mean_abs"],
        spl_low_level_shift_db=spl_low_level_shift_db,
    )

    driver = gdn13_hornresp_driver_derived_parameters()
    mapping_trial_interpretation = (
        "Impedance/topology mapping is promising, but SPL observation/radiation/output "
        "convention remains unresolved."
    )

    return {
        "task": "test/v0.8.0-gdn13-offset-tqwt-hornresp-mapping-trial",
        "repair_scope": "fix/v0.8.0-gdn13-offset-tqwt-hornresp-mapping-trial-runtime-wording",
        "mapping_trial_interpretation": mapping_trial_interpretation,
        "spl_parity_non_claim": "not SPL parity success; SPL mismatch remains explicitly reported",
        "fixture_files": {
            "hornresp_definition": str(Path(hornresp_definition_path)),
            "hornresp_response": str(Path(hornresp_response_path)),
        },
        "compared_columns": ["Freq (hertz)", "SPL (dB)", "Ze (ohms)"],
        "frequency_count": int(frequency_hz.size),
        "low_frequency_count_le_600_hz": int(np.count_nonzero(low_mask)),
        "frequency_span_hz": [float(frequency_hz[0]), float(frequency_hz[-1])],
        "oslem_interpretation": {
            "topology": "offset-driver TQWT with rear closed stub S1-S2 and forward open line S2-S3",
            "profile": profile,
            "rear_closed_stub": "S1=96.00 cm2 to S2=98.06 cm2, length=55.80 cm",
            "driver_source_tap": "S2 tap, node tap_s2",
            "forward_open_line": "S2=98.06 cm2 to S3=102.00 cm2, length=106.46 cm",
            "mouth_radiation": "S3 mouth radiation, 2*pi observation",
            "front_radiation": "diagnostic driver-front radiator retained as explicit os-lem driver load; HornResp SPL comparison uses spl_mouth",
        },
        "driver_parameters_used": {
            "hornresp_inputs": {
                "Sd_cm2": driver.sd_cm2,
                "Bl_Tm": driver.bl_tm,
                "Cms_m_per_N": driver.cms_m_per_n,
                "Rms": driver.rms_mechanical,
                "Mmd_g": driver.mmd_g,
                "Le_mH": driver.le_mh,
                "Re_ohm": driver.re_ohm,
                "OD": 1,
            },
            "oslem_ts_classic_derived": {
                "Fs_hz": driver.fs_hz,
                "Qes": driver.qes,
                "Qms": driver.qms,
                "Vas_l": driver.vas_l,
            },
        },
        "model_dict_construction_path": "os_lem.reference_gdn13_offset_tqwt_mapping_trial.build_gdn13_offset_tqwt_model_dict(profile='parabolic')",
        "solver_call_path": "os_lem.api.run_simulation(model_dict, frequency_hz)",
        "impedance_comparison": {
            "metric_basis": "absolute difference of electrical impedance magnitude Ze in ohms",
            "full": _metric_summary(impedance_delta),
            "low_frequency_le_600_hz": impedance_low,
            "hornresp_low_frequency_peak": hornresp_peak,
            "oslem_low_frequency_peak": oslem_peak,
        },
        "spl_comparison": {
            "metric_basis": "HornResp SPL (dB) compared to os-lem spl_mouth (dB)",
            "full": spl_full,
            "low_frequency_le_600_hz": spl_low,
            "low_frequency_level_shift_db": spl_low_level_shift_db,
            "low_frequency_zero_mean_shape": spl_low_zero_mean,
        },
        "determinism": {
            "spl_repeat_allclose_rtol": 1.0e-12,
            "spl_repeat_allclose_atol": 1.0e-12,
            "impedance_repeat_allclose_rtol": 1.0e-12,
            "impedance_repeat_allclose_atol": 1.0e-12,
        },
        "mismatch_interpretation": interpretation,
        "non_claims": [
            "not HornResp parity",
            "not SPL parity success",
            "SPL observation/radiation/output convention remains unresolved",
            "no Akabak/HornResp replacement claim",
        ],
        "scope_guards": [
            "one mapping trial only",
            "no general HornResp importer",
            "no optimizer implementation",
            "no Studio work",
            "no topology expansion",
            "no Akabak/HornResp replacement claim",
        ],
    }
