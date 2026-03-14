import streamlit as st
import yaml
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# ────────────────────────────────────────────────
#   ATTEMPT TO IMPORT YOUR SOLVER – adjust name/path as needed
# ────────────────────────────────────────────────
try:
    # Possible real imports once API is public (examples of likely patterns):
    # from os_lem import Session, simulate_model, load_from_yaml
    # from os_lem.core import solve_system
    # from os_lem.solver import run_simulation   ← adjust to your actual module

    # For now: placeholder – replace with real import when ready
    HAS_SOLVER = False
    st.warning("Solver integration is placeholder-only → real curves appear after API hook is added.")
except ImportError:
    HAS_SOLVER = False

st.set_page_config(page_title="os-lem Box Designer", layout="wide")
st.title("🪄 os-lem Simple Box Designer")
st.caption("Closed & vented box models using your current YAML format (feature/p5 branch)")

tab_closed, tab_vented = st.tabs(["Closed Box", "Vented (Bass-Reflex)"])

# Shared TS parameters helper
def driver_ts_section(key_prefix=""):
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
        "Re": re, "Fs": fs, "Qes": qes, "Qms": qms,
        "Vas": vas_l, "Sd": sd_cm2, "Le": le_mh
    }

# Common frequency axis for plots
frequencies = np.logspace(np.log10(10), np.log10(1000), 200)   # typical audio range

# ────────────────────────────────────────────────
#   CLOSED BOX TAB
# ────────────────────────────────────────────────
with tab_closed:
    st.subheader("Closed Box")
    ts = driver_ts_section("closed_")
    
    vb_l = st.slider("Box volume Vb (liters)", 5.0, 100.0, 18.0, 1.0)
    
    yaml_data = {
        "meta": {"name": "closed_box_demo"},
        "driver": {
            "id": "drv1",
            "model": "ts_classic",
            "Re": f"{ts['Re']} ohm",
            "Le": f"{ts['Le']} mH",
            "Fs": f"{ts['Fs']} Hz",
            "Qes": ts['Qes'],
            "Qms": ts['Qms'],
            "Vas": f"{ts['Vas']} l",
            "Sd": f"{ts['Sd']} cm2"
        },
        "node_front": "front",
        "node_rear": "rear",
        "elements": [
            {"id": "front_rad", "type": "radiator", "node": "front",
             "model": "infinite_baffle_piston", "area": f"{ts['Sd']} cm2"},
            {"id": "box", "type": "volume", "node": "rear", "value": f"{vb_l} l"}
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "exc", "type": "displacement", "target": "drv1"}   # or velocity
        ]
    }
    
    yaml_str = yaml.dump(yaml_data, sort_keys=False, allow_unicode=True)
    st.code(yaml_str, language="yaml")
    
    if st.button("🚀 Simulate Closed Box", type="primary"):
        if not HAS_SOLVER:
            st.info("Solver not hooked yet → showing example placeholder curves")
            # Placeholder data (replace with real results)
            spl_db = 80 + 20 * np.log10(frequencies / 50) - 10 * np.log10(frequencies / 100)**2  # fake rolloff
            imp_mag = 6 + 40 / (1 + (frequencies / 60)**2)  # fake impedance peak
            exc_mm = 2.0 / (1 + (frequencies / 80)**4)      # fake excursion
        else:
            # REAL CALL – replace with your actual API when ready, example patterns:
            # session = Session.from_yaml_string(yaml_str)
            # results = session.solve(frequencies=frequencies)
            #   or
            # results = simulate_model(yaml_data, freqs=frequencies)
            # spl_db    = results["spl"]["front_rad"]["magnitude_db"]
            # imp_mag   = np.abs(results["input_impedance"])
            # exc_mm    = np.abs(results["displacement"]) * 1e3   # μm → mm
            # etc.
            st.error("Real solver call placeholder – implement here")
            spl_db = imp_mag = exc_mm = np.zeros_like(frequencies)  # safety
        
        # ── Plots ────────────────────────────────────────
        fig_spl = go.Figure()
        fig_spl.add_trace(go.Scatter(x=frequencies, y=spl_db, mode='lines', name='SPL (dB)'))
        fig_spl.update_layout(title="On-axis SPL @ 1 m", xaxis_title="Frequency (Hz)", yaxis_title="SPL (dB)", xaxis_type="log")
        
        fig_imp = go.Figure()
        fig_imp.add_trace(go.Scatter(x=frequencies, y=imp_mag, mode='lines', name='|Zin| (Ω)'))
        fig_imp.update_layout(title="Input Impedance Magnitude", xaxis_title="Frequency (Hz)", yaxis_title="Impedance (Ω)", xaxis_type="log")
        
        fig_exc = go.Figure()
        fig_exc.add_trace(go.Scatter(x=frequencies, y=exc_mm, mode='lines', name='Excursion (mm)'))
        fig_exc.update_layout(title="Diaphragm Displacement", xaxis_title="Frequency (Hz)", yaxis_title="Displacement (mm)", xaxis_type="log")
        
        st.plotly_chart(fig_spl, use_container_width=True)
        st.plotly_chart(fig_imp, use_container_width=True)
        st.plotly_chart(fig_exc, use_container_width=True)

# ────────────────────────────────────────────────
#   VENTED BOX TAB (very similar structure)
# ────────────────────────────────────────────────
with tab_vented:
    st.subheader("Vented Box (Bass-Reflex)")
    ts_v = driver_ts_section("vented_")
    
    vb_l = st.slider("Box volume Vb (liters)", 10.0, 150.0, 35.0, 1.0, key="vb_vent")
    port_len_cm = st.slider("Port length (cm)", 5.0, 60.0, 20.0, 1.0)
    port_dia_cm = st.slider("Port diameter (cm)", 3.0, 15.0, 5.0, 0.1)
    port_area_cm2 = np.pi * (port_dia_cm / 2)**2
    
    yaml_data_v = {
        "meta": {"name": "vented_box_demo"},
        "driver": {**yaml_data["driver"]},  # reuse driver
        "node_front": "front",
        "node_rear": "rear",
        "node_port_mouth": "port_mouth",
        "elements": [
            {"id": "front_rad", "type": "radiator", "node": "front",
             "model": "infinite_baffle_piston", "area": f"{ts_v['Sd']} cm2"},
            {"id": "box", "type": "volume", "node": "rear", "value": f"{vb_l} l"},
            {"id": "port", "type": "duct", "node_a": "rear", "node_b": "port_mouth",
             "length": f"{port_len_cm/100} m", "area": f"{port_area_cm2} cm2"},
            {"id": "port_rad", "type": "radiator", "node": "port_mouth",
             "model": "unflanged_piston", "area": f"{port_area_cm2} cm2"}
        ],
        "observations": [
            {"id": "zin", "type": "input_impedance", "target": "drv1"},
            {"id": "spl_driver", "type": "spl", "target": "front_rad", "distance": "1 m"},
            {"id": "spl_port", "type": "spl", "target": "port_rad", "distance": "1 m"},
            {"id": "spl_total", "type": "spl_sum", "terms": [
                {"target": "front_rad", "distance": "1 m"},
                {"target": "port_rad", "distance": "1 m"}
            ]},
            {"id": "exc", "type": "displacement", "target": "drv1"}
        ]
    }
    
    yaml_str_v = yaml.dump(yaml_data_v, sort_keys=False, allow_unicode=True)
    st.code(yaml_str_v, language="yaml")
    
    if st.button("🚀 Simulate Vented Box", type="primary"):
        st.info("Same placeholder logic as closed box – connect real solver here")
        # Reuse placeholder data or compute differently if desired
        spl_db = 82 + 18 * np.log10(frequencies / 40)   # fake vented boost
        imp_mag = 7 + 50 / (1 + ((frequencies - 35)/15)**4)
        exc_mm = 1.8 / (1 + (frequencies / 70)**4)
        
        # Plots (same as above – can be refactored into function later)
        fig_spl = go.Figure(go.Scatter(x=frequencies, y=spl_db, mode='lines', name='Total SPL'))
        fig_spl.update_layout(title="Combined SPL @ 1 m", xaxis_title="Frequency (Hz)", yaxis_title="SPL (dB)", xaxis_type="log")
        
        fig_imp = go.Figure(go.Scatter(x=frequencies, y=imp_mag, mode='lines', name='|Zin|'))
        fig_imp.update_layout(title="Input Impedance", xaxis_title="Frequency (Hz)", yaxis_title="Ω", xaxis_type="log")
        
        fig_exc = go.Figure(go.Scatter(x=frequencies, y=exc_mm, mode='lines', name='Excursion'))
        fig_exc.update_layout(title="Displacement", xaxis_title="Frequency (Hz)", yaxis_title="mm", xaxis_type="log")
        
        st.plotly_chart(fig_spl, use_container_width=True)
        st.plotly_chart(fig_imp, use_container_width=True)
        st.plotly_chart(fig_exc, use_container_width=True)

st.markdown("---")
st.caption("Once the high-level solver API is exposed (e.g. Session / simulate_model), replace the placeholder block with 5–10 lines of real code → plots become live.")
