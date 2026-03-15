from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
import yaml

try:
    import streamlit as st
except ImportError as exc:
    raise SystemExit("This app needs Streamlit installed locally. Run: pip install streamlit plotly pyyaml numpy") from exc

st.set_page_config(page_title="os-lem Box Designer", layout="wide", page_icon="🔊")

# -----------------------------------------------------------------------------
# 1. OS-LEM BACKEND DISCOVERY & LOADING (From original app.py)
# -----------------------------------------------------------------------------
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
        repo_root = Path(repo_root_text)
    else:
        roots = _candidate_repo_roots()
        if not roots:
            st.error("Could not locate os-lem repository.")
            st.stop()
        repo_root = roots[0]

    src_dir = repo_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from os_lem.assemble import assemble_system
    from os_lem.parser import load_and_normalize
    from os_lem.solve import radiator_spl, solve_frequency_sweep

    class OsLemSolver:
        def __init__(self):
            self.load_and_normalize = load_and_normalize
            self.assemble_system = assemble_system
            self.solve_frequency_sweep = solve_frequency_sweep
            self.radiator_spl = radiator_spl

    return OsLemSolver()

solver = load_solver(None)
frequencies = np.logspace(np.log10(10), np.log10(1000), 300).tolist()

# -----------------------------------------------------------------------------
# 2. STATE MANAGEMENT (GLOBAL DRIVER)
# -----------------------------------------------------------------------------
if "driver_ts" not in st.session_state:
    st.session_state.driver_ts = {
        "Re": 5.8, "Le": 0.35, "Fs": 34.0, 
        "Qes": 0.42, "Qms": 4.1, "Vas": 55.0, "Sd": 132.0
    }

def get_driver_dict() -> dict[str, Any]:
    ts = st.session_state.driver_ts
    return {
        "id": "drv1",
        "model": "ts_classic",
        "Re": f"{ts['Re']} ohm",
        "Le": f"{ts['Le']} mH",
        "Fs": f"{ts['Fs']} Hz",
        "Qes": ts['Qes'],
        "Qms": ts['Qms'],
        "Vas": f"{ts['Vas']} l",
        "Sd": f"{ts['Sd']} cm2",
        "node_front": "front",
        "node_rear": "rear"
    }

# -----------------------------------------------------------------------------
# 3. SIDEBAR UI (LOAD / EDIT / SAVE)
# -----------------------------------------------------------------------------
st.sidebar.header("🔊 Global Driver")

uploaded_file = st.sidebar.file_uploader("Load Driver (YAML)", type=["yaml", "yml"])
if uploaded_file is not None:
    try:
        raw_yaml = yaml.safe_load(uploaded_file)
        driver_data = raw_yaml.get("driver", raw_yaml)
        for key in st.session_state.driver_ts.keys():
            if key in driver_data:
                val = str(driver_data[key]).split()[0]
                st.session_state.driver_ts[key] = float(val)
        st.sidebar.success("Loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading: {e}")

ts = st.session_state.driver_ts
ts["Re"] = st.sidebar.number_input("Re (Ω)", value=ts["Re"], step=0.1)
ts["Le"] = st.sidebar.number_input("Le (mH)", value=ts["Le"], step=0.05)
ts["Fs"] = st.sidebar.number_input("Fs (Hz)", value=ts["Fs"], step=0.5)
ts["Qes"] = st.sidebar.number_input("Qes", value=ts["Qes"], step=0.05)
ts["Qms"] = st.sidebar.number_input("Qms", value=ts["Qms"], step=0.1)
ts["Vas"] = st.sidebar.number_input("Vas (liters)", value=ts["Vas"], step=1.0)
ts["Sd"] = st.sidebar.number_input("Sd (cm²)", value=ts["Sd"], step=1.0)

st.sidebar.markdown("---")
export_name = st.sidebar.text_input("Save file as:", value="my_driver.yaml")
if not export_name.endswith(".yaml"):
    export_name += ".yaml"

st.sidebar.download_button(
    label="💾 Save Driver to YAML", 
    data=yaml.dump({"driver": get_driver_dict()}, sort_keys=False), 
    file_name=export_name, 
    mime="text/yaml"
)

# -----------------------------------------------------------------------------
# 4. MODEL BUILDERS
# -----------------------------------------------------------------------------
def build_closed_model(vb_l: float) -> dict:
    return {
        "meta": {"name": "closed_box"},
        "driver": get_driver_dict(),
        "elements": [
            {"id": "front_rad", "type": "radiator", "node": "front", "model": "infinite_baffle_piston", "area": f"{ts['Sd']} cm2"},
            {"id": "rear_box", "type": "volume", "node": "rear", "value": f"{vb_l} l"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl_total", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
        ]
    }

def build_vented_model(vb_l: float, port_len_cm: float, port_dia_cm: float) -> dict:
    port_area = np.pi * ((port_dia_cm / 2) ** 2)
    return {
        "meta": {"name": "vented_box"},
        "driver": get_driver_dict(),
        "elements": [
            {"id": "front_rad", "type": "radiator", "node": "front", "model": "unflanged_piston", "area": f"{ts['Sd']} cm2"},
            {"id": "rear_box", "type": "volume", "node": "rear", "value": f"{vb_l} l"},
            {"id": "port", "type": "duct", "node_a": "rear", "node_b": "port_mouth", "length": f"{port_len_cm} cm", "area": f"{port_area} cm2"},
            {"id": "port_rad", "type": "radiator", "node": "port_mouth", "model": "unflanged_piston", "area": f"{port_area} cm2"},
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl_driver", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "spl_port", "type": "spl", "target": "port_rad", "distance": "1 m"},
            {"id": "spl_total", "type": "spl_sum", "terms": [{"target": "front_rad", "distance": "1 m"}, {"target": "port_rad", "distance": "1 m"}]},
            {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
        ]
    }

def build_tl_model(length_m: float, offset_pct: float, sc_cm2: float, so_cm2: float) -> dict:
    elements = [
        {"id": "front_rad", "type": "radiator", "node": "front", "model": "unflanged_piston", "area": f"{ts['Sd']} cm2"}
    ]
    
    if offset_pct > 0:
        driver_offset_m = length_m * (offset_pct / 100.0)
        main_length_m = length_m - driver_offset_m
        sd_pos_cm2 = sc_cm2 + (so_cm2 - sc_cm2) * (offset_pct / 100.0)
        
        # Segment 1: Closed end (Sc) to Driver Rear
        elements.append({
            "id": "tl_closed_stub", "type": "waveguide_1d", 
            "node_a": "closed_end", "node_b": "rear", 
            "length": f"{driver_offset_m} m", 
            "area_start": f"{sc_cm2} cm2", "area_end": f"{sd_pos_cm2} cm2",
            "profile": "conical"  # <-- ADD THIS
        })
        
        # Segment 2: Driver Rear to Open Terminus (So)
        elements.append({
            "id": "tl_main", "type": "waveguide_1d", 
            "node_a": "rear", "node_b": "tl_mouth", 
            "length": f"{main_length_m} m", 
            "area_start": f"{sd_pos_cm2} cm2", "area_end": f"{so_cm2} cm2"
        })
    else:
        elements.append({
            "id": "tl_main", "type": "waveguide_1d", 
            "node_a": "rear", "node_b": "tl_mouth", 
            "length": f"{length_m} m", 
            "area_start": f"{sc_cm2} cm2", "area_end": f"{so_cm2} cm2"
        })
        
    elements.append({
        "id": "port_rad", "type": "radiator", "node": "tl_mouth", 
        "model": "unflanged_piston", "area": f"{so_cm2} cm2"
    })
    
    return {
        "meta": {"name": "transmission_line_tapered_offset"},
        "driver": get_driver_dict(),
        "elements": elements,
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl_driver", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "spl_port", "type": "spl", "target": "port_rad", "distance": "1 m"},
            {"id": "spl_total", "type": "spl_sum", "terms": [{"target": "front_rad", "distance": "1 m"}, {"target": "port_rad", "distance": "1 m"}]},
            {"id": "xcone", "type": "cone_displacement", "target": "drv1"},
        ]
    }

# -----------------------------------------------------------------------------
# 5. EXECUTION & PLOTTING (Exactly from your original app.py)
# -----------------------------------------------------------------------------
def run_model(model_dict: dict, frequencies: list[float], solver) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        yaml.dump(model_dict, f, sort_keys=False)
        tmp_path = f.name

    try:
        norm_model, warnings = solver.load_and_normalize(Path(tmp_path))
        sys_asm = solver.assemble_system(norm_model)
        sweep = solver.solve_frequency_sweep(sys_asm, frequencies)

        results: dict[str, Any] = {"freq": sweep.omega_rad_s / (2 * np.pi), "warnings": warnings}

        for obs in norm_model.observations:
            if obs.type == "input_impedance":
                drv_idx = sys_asm.driver_front_index
                z_in = sweep.zin_driver
                results[f"{obs.id}_mag"] = np.abs(z_in)
                results[f"{obs.id}_phase"] = np.angle(z_in, deg=True)
            elif obs.type == "spl":
                p_complex = solver.radiator_spl(sweep, sys_asm, obs.target, obs.distance_m)
                p_ref = 2e-5
                results[f"{obs.id}_db"] = 20 * np.log10(np.abs(p_complex) / p_ref)
                results[f"{obs.id}_p"] = p_complex
            elif obs.type == "spl_sum":
                p_total = np.zeros_like(sweep.omega_rad_s, dtype=complex)
                for term in obs.terms:
                    p_term = solver.radiator_spl(sweep, sys_asm, term.target, term.distance_m)
                    p_total += p_term
                p_ref = 2e-5
                results[f"{obs.id}_db"] = 20 * np.log10(np.abs(p_total) / p_ref)
            elif obs.type == "cone_displacement":
                x_m = np.abs(sweep.x_cone)
                results[f"{obs.id}_mm"] = x_m * 1000.0

        return results
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def plot_curve(freqs: np.ndarray, y: np.ndarray, title: str, ylabel: str, name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freqs, y=y, mode="lines", name=name))
    fig.update_layout(
        title=title, xaxis_title="Frequency (Hz)", yaxis_title=ylabel,
        xaxis_type="log", margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig

def plot_vented_spl(freqs: np.ndarray, result: dict[str, Any]) -> go.Figure:
    fig = go.Figure()
    if "spl_total_db" in result:
        fig.add_trace(go.Scatter(x=freqs, y=result["spl_total_db"], mode="lines", name="Total SPL", line=dict(width=3, color="gold")))
    if "spl_driver_db" in result:
        fig.add_trace(go.Scatter(x=freqs, y=result["spl_driver_db"], mode="lines", name="Driver SPL", line=dict(dash="dash")))
    if "spl_port_db" in result:
        fig.add_trace(go.Scatter(x=freqs, y=result["spl_port_db"], mode="lines", name="Port SPL", line=dict(dash="dot")))
    fig.update_layout(
        title="SPL (1m, 2.83V) - Vented / TL", xaxis_title="Frequency (Hz)", yaxis_title="SPL (dB)",
        xaxis_type="log", margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig

# -----------------------------------------------------------------------------
# 6. MAIN UI TABS
# -----------------------------------------------------------------------------
st.title("os-lem Prototyper")

tab_closed, tab_vented, tab_tl = st.tabs(["Closed Box", "Vented Box", "Transmission Line (1D)"])

with tab_closed:
    st.subheader("Closed Box")
    vb_c = st.slider("Closed Box Volume (liters)", 5.0, 150.0, 18.0, 1.0)
    if st.button("🚀 Simulate Closed Box", type="primary"):
        try:
            result = run_model(build_closed_model(vb_c), frequencies, solver)
            for w in result.get("warnings", []):
                st.warning(str(w))
            st.plotly_chart(plot_curve(frequencies, result["spl_total_db"], "Total SPL (1m, 2.83V)", "SPL (dB)", "Total SPL"), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["zin_mag"], "Input Impedance Magnitude", "Impedance (Ω)", "|Zin|"), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["xcone_mm"], "Cone Excursion (Peak)", "Excursion (mm)", "X_peak"), use_container_width=True)
        except Exception as e:
            st.error(f"Solver Error: {e}")

with tab_vented:
    st.subheader("Vented Box")
    col1, col2, col3 = st.columns(3)
    vb_v = col1.slider("Vented Box Volume (liters)", 5.0, 150.0, 28.0, 1.0)
    port_len = col2.slider("Port Length (cm)", 5.0, 60.0, 18.0, 1.0)
    port_dia = col3.slider("Port Diameter (cm)", 3.0, 15.0, 5.5, 0.1)
    
    if st.button("🚀 Simulate Vented Box", type="primary"):
        try:
            result = run_model(build_vented_model(vb_v, port_len, port_dia), frequencies, solver)
            for w in result.get("warnings", []):
                st.warning(str(w))
            st.plotly_chart(plot_vented_spl(frequencies, result), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["zin_mag"], "Input Impedance Magnitude", "Impedance (Ω)", "|Zin|"), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["xcone_mm"], "Cone Excursion (Peak)", "Excursion (mm)", "X_peak"), use_container_width=True)
        except Exception as e:
            st.error(f"Solver Error: {e}")

with tab_tl:
    st.subheader("Offset-Driver Tapered Transmission Line")
    
    col1, col2 = st.columns(2)
    tl_len = col1.slider("Total Line Length (m)", 0.5, 4.0, 1.5, 0.1)
    offset_pct = col2.slider("Driver Offset (% from closed end)", 0, 50, 33, 1)
    
    col3, col4 = st.columns(2)
    sc_area = col3.slider("Sc: Closed End Area (cm²)", 10.0, 500.0, float(st.session_state.driver_ts["Sd"]) * 1.5, 5.0)
    so_area = col4.slider("So: Open Terminus Area (cm²)", 10.0, 500.0, float(st.session_state.driver_ts["Sd"]), 5.0)
    
    if st.button("🚀 Simulate Transmission Line", type="primary"):
        try:
            result = run_model(build_tl_model(tl_len, offset_pct, sc_area, so_area), frequencies, solver)
            for w in result.get("warnings", []):
                st.warning(str(w))
            # We can reuse plot_vented_spl because we named the terminus observation "spl_port"!
            st.plotly_chart(plot_vented_spl(frequencies, result), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["zin_mag"], "Input Impedance Magnitude", "Impedance (Ω)", "|Zin|"), use_container_width=True)
            st.plotly_chart(plot_curve(frequencies, result["xcone_mm"], "Cone Excursion (Peak)", "Excursion (mm)", "X_peak"), use_container_width=True)
        except Exception as e:
            st.error(f"Solver Error: {e}")
