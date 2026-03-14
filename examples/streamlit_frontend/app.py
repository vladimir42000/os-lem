from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
import yaml

try:
    import streamlit as st
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "This app needs Streamlit installed locally. Run: pip install streamlit plotly pyyaml numpy"
    ) from exc


st.set_page_config(page_title="os-lem Simple Box Designer", layout="wide")


def _candidate_repo_roots() -> list[Path]:
    candidates: list[Path] = []
    env_repo = os.environ.get("OS_LEM_REPO")
    if env_repo:
        candidates.append(Path(env_repo).expanduser())

    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "src" / "os_lem").exists():
            candidates.append(p)

    cwd = Path.cwd()
    for p in [cwd, *cwd.parents]:
        if (p / "src" / "os_lem").exists():
            candidates.append(p)

    uniq: list[Path] = []
    seen: set[Path] = set()
    for p in candidates:
        rp = p.resolve()
        if rp not in seen:
            uniq.append(rp)
            seen.add(rp)
    return uniq


@st.cache_resource(show_spinner=False)
def load_solver(repo_root_text: str | None):
    repo_root: Path | None = None
    if repo_root_text:
        candidate = Path(repo_root_text).expanduser().resolve()
        if (candidate / "src" / "os_lem").exists():
            repo_root = candidate

    if repo_root is None:
        for cand in _candidate_repo_roots():
            if (cand / "src" / "os_lem").exists():
                repo_root = cand
                break

    if repo_root is None:
        raise FileNotFoundError(
            "Could not locate repo root containing src/os_lem. "
            "Set OS_LEM_REPO or type the repo path in the sidebar."
        )

    src_dir = repo_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from os_lem.assemble import assemble_system
    from os_lem.constants import P_REF
    from os_lem.parser import normalize_model
    from os_lem.solve import radiator_observation_pressure, radiator_spl, solve_frequency_sweep

    return {
        "repo_root": repo_root,
        "normalize_model": normalize_model,
        "assemble_system": assemble_system,
        "solve_frequency_sweep": solve_frequency_sweep,
        "radiator_observation_pressure": radiator_observation_pressure,
        "radiator_spl": radiator_spl,
        "P_REF": P_REF,
    }


def driver_ts_section(key_prefix: str = "") -> dict[str, float]:
    col1, col2 = st.columns(2)
    with col1:
        re = st.number_input("Re (Ω)", 1.0, 20.0, 5.8, 0.1, key=f"{key_prefix}re")
        fs = st.number_input("Fs (Hz)", 10.0, 200.0, 34.0, 0.5, key=f"{key_prefix}fs")
        qes = st.number_input("Qes", 0.1, 2.0, 0.42, 0.01, key=f"{key_prefix}qes")
        qms = st.number_input("Qms", 1.0, 20.0, 4.1, 0.1, key=f"{key_prefix}qms")
    with col2:
        vas_l = st.number_input("Vas (liters)", 1.0, 500.0, 55.0, 1.0, key=f"{key_prefix}vas")
        sd_cm2 = st.number_input("Sd (cm²)", 20.0, 1000.0, 132.0, 1.0, key=f"{key_prefix}sd")
        le_mh = st.number_input("Le (mH)", 0.0, 5.0, 0.35, 0.01, key=f"{key_prefix}le")

    return {
        "Re": re,
        "Fs": fs,
        "Qes": qes,
        "Qms": qms,
        "Vas": vas_l,
        "Sd": sd_cm2,
        "Le": le_mh,
    }


def base_driver_yaml(ts: dict[str, float]) -> dict[str, Any]:
    return {
        "id": "drv1",
        "model": "ts_classic",
        "Re": f"{ts['Re']} ohm",
        "Le": f"{ts['Le']} mH",
        "Fs": f"{ts['Fs']} Hz",
        "Qes": ts["Qes"],
        "Qms": ts["Qms"],
        "Vas": f"{ts['Vas']} l",
        "Sd": f"{ts['Sd']} cm2",
        "node_front": "front",
        "node_rear": "rear",
    }


def build_closed_model(ts: dict[str, float], vb_l: float) -> dict[str, Any]:
    sd = ts["Sd"]
    return {
        "meta": {"name": "closed_box_demo"},
        "driver": base_driver_yaml(ts),
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "infinite_baffle_piston",
                "area": f"{sd} cm2",
            },
            {"id": "box", "type": "volume", "node": "rear", "value": f"{vb_l} l"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
        ],
    }


def build_vented_model(
    ts: dict[str, float],
    vb_l: float,
    port_len_cm: float,
    port_dia_cm: float,
) -> dict[str, Any]:
    sd = ts["Sd"]
    port_area_cm2 = np.pi * (port_dia_cm / 2.0) ** 2
    return {
        "meta": {"name": "vented_box_demo"},
        "driver": base_driver_yaml(ts),
        "elements": [
            {
                "id": "front_rad",
                "type": "radiator",
                "node": "front",
                "model": "infinite_baffle_piston",
                "area": f"{sd} cm2",
            },
            {"id": "box", "type": "volume", "node": "rear", "value": f"{vb_l} l"},
            {
                "id": "port",
                "type": "duct",
                "node_a": "rear",
                "node_b": "port_mouth",
                "length": f"{port_len_cm / 100.0} m",
                "area": f"{port_area_cm2} cm2",
            },
            {
                "id": "port_rad",
                "type": "radiator",
                "node": "port_mouth",
                "model": "unflanged_piston",
                "area": f"{port_area_cm2} cm2",
            },
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl_driver", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "spl_port", "type": "spl", "target": "port_rad", "distance": "1 m"},
            {
                "id": "spl_total",
                "type": "spl_sum",
                "terms": [
                    {"target": "front_rad", "distance": "1 m"},
                    {"target": "port_rad", "distance": "1 m"},
                ],
            },
            {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
        ],
    }


def run_model(model_dict: dict[str, Any], frequencies: np.ndarray, solver: dict[str, Any]) -> dict[str, np.ndarray]:
    normalize_model = solver["normalize_model"]
    assemble_system = solver["assemble_system"]
    solve_frequency_sweep = solver["solve_frequency_sweep"]
    radiator_spl = solver["radiator_spl"]
    radiator_observation_pressure = solver["radiator_observation_pressure"]
    p_ref = solver["P_REF"]

    model, warnings = normalize_model(model_dict)
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, frequencies)

    out: dict[str, np.ndarray] = {
        "frequency_hz": np.asarray(frequencies, dtype=float),
        "zin_mag": np.abs(sweep.input_impedance),
        "x_mm": np.abs(sweep.cone_displacement) * 1e3,
    }
    if warnings:
        out["warnings"] = np.array(warnings, dtype=object)

    radiator_ids = {r["id"] for r in model_dict["elements"] if r["type"] == "radiator"}
    if "front_rad" in radiator_ids:
        out["spl_driver_db"] = radiator_spl(sweep, system, "front_rad", 1.0)
        out["p_driver"] = radiator_observation_pressure(sweep, system, "front_rad", 1.0)
    if "port_rad" in radiator_ids:
        out["spl_port_db"] = radiator_spl(sweep, system, "port_rad", 1.0)
        out["p_port"] = radiator_observation_pressure(sweep, system, "port_rad", 1.0)

    if "p_driver" in out and "p_port" in out:
        p_total = out["p_driver"] + out["p_port"]
        out["spl_total_db"] = 20.0 * np.log10(np.maximum(np.abs(p_total), 1e-30) / p_ref)

    if "spl_driver_db" in out and "spl_total_db" not in out:
        out["spl_total_db"] = out["spl_driver_db"]

    return out


def make_yaml_preview(data: dict[str, Any]) -> str:
    return yaml.dump(data, sort_keys=False, allow_unicode=True)


def plot_curve(freq: np.ndarray, y: np.ndarray, title: str, ytitle: str, name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freq, y=y, mode="lines", name=name))
    fig.update_layout(title=title, xaxis_title="Frequency (Hz)", yaxis_title=ytitle, xaxis_type="log")
    return fig


def plot_vented_spl(freq: np.ndarray, curves: dict[str, np.ndarray]) -> go.Figure:
    fig = go.Figure()
    if "spl_driver_db" in curves:
        fig.add_trace(go.Scatter(x=freq, y=curves["spl_driver_db"], mode="lines", name="Driver SPL"))
    if "spl_port_db" in curves:
        fig.add_trace(go.Scatter(x=freq, y=curves["spl_port_db"], mode="lines", name="Port SPL"))
    if "spl_total_db" in curves:
        fig.add_trace(go.Scatter(x=freq, y=curves["spl_total_db"], mode="lines", name="Total SPL"))
    fig.update_layout(title="SPL @ 1 m", xaxis_title="Frequency (Hz)", yaxis_title="SPL (dB)", xaxis_type="log")
    return fig


st.title("🪄 os-lem Simple Box Designer")
st.caption("Closed & vented box models on top of the current low-level os-lem kernel")

with st.sidebar:
    st.subheader("Solver hookup")
    default_repo = str(_candidate_repo_roots()[0]) if _candidate_repo_roots() else ""
    repo_root_text = st.text_input("Repo root (folder containing src/os_lem)", value=default_repo)
    f_start = st.number_input("f_start (Hz)", 5.0, 500.0, 10.0, 1.0)
    f_stop = st.number_input("f_stop (Hz)", 20.0, 5000.0, 1000.0, 10.0)
    n_points = st.slider("points", 50, 800, 200, 10)

try:
    solver = load_solver(repo_root_text)
    st.success(f"Solver found at: {solver['repo_root']}")
except Exception as exc:
    solver = None
    st.error(str(exc))
    st.stop()

frequencies = np.logspace(np.log10(f_start), np.log10(f_stop), int(n_points))

tab_closed, tab_vented = st.tabs(["Closed Box", "Vented (Bass-Reflex)"])

with tab_closed:
    st.subheader("Closed Box")
    ts = driver_ts_section("closed_")
    vb_l = st.slider("Box volume Vb (liters)", 5.0, 100.0, 18.0, 1.0)

    closed_model = build_closed_model(ts, vb_l)
    with st.expander("Generated YAML preview", expanded=False):
        st.code(make_yaml_preview(closed_model), language="yaml")

    if st.button("🚀 Simulate Closed Box", type="primary"):
        try:
            result = run_model(closed_model, frequencies, solver)
            if "warnings" in result:
                for w in result["warnings"]:
                    st.warning(str(w))

            st.plotly_chart(plot_curve(frequencies, result["spl_total_db"], "On-axis SPL @ 1 m", "SPL (dB)", "SPL"), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["zin_mag"], "Input Impedance Magnitude", "Impedance (Ω)", "|Zin|"), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["x_mm"], "Diaphragm Displacement", "Displacement (mm)", "Excursion"), use_container_width=True)
        except Exception as exc:
            st.exception(exc)

with tab_vented:
    st.subheader("Vented Box (Bass-Reflex)")
    ts_v = driver_ts_section("vented_")
    vb_v_l = st.slider("Box volume Vb (liters)", 10.0, 150.0, 35.0, 1.0, key="vb_vent")
    port_len_cm = st.slider("Port length (cm)", 5.0, 60.0, 20.0, 1.0)
    port_dia_cm = st.slider("Port diameter (cm)", 3.0, 15.0, 5.0, 0.1)

    vented_model = build_vented_model(ts_v, vb_v_l, port_len_cm, port_dia_cm)
    with st.expander("Generated YAML preview", expanded=False):
        st.code(make_yaml_preview(vented_model), language="yaml")

    if st.button("🚀 Simulate Vented Box", type="primary"):
        try:
            result = run_model(vented_model, frequencies, solver)
            if "warnings" in result:
                for w in result["warnings"]:
                    st.warning(str(w))

            st.plotly_chart(plot_vented_spl(frequencies, result), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["zin_mag"], "Input Impedance Magnitude", "Impedance (Ω)", "|Zin|"), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["x_mm"], "Diaphragm Displacement", "Displacement (mm)", "Excursion"), use_container_width=True)
        except Exception as exc:
            st.exception(exc)

st.markdown("---")
st.caption(
    "This frontend stays outside the core dev tree. It uses the current low-level parser → assembler → sweep → post-processing path directly."
)
