"""
AquaGuard - AI Water Purifier Monitoring Dashboard
Theme: 'Let's Get Digital' (Frosted glassmorphism, azure-to-obsidian gradient, electric blue accents).
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import textwrap
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from src.virtual_sensors import VirtualSensorSimulator
from src.live_predictor import AquaGuardLivePredictor
from src.auth_ui import render_auth_page, render_user_sidebar
from src.ui_components import (
    inject_custom_css,
    render_aquaguard_header,
    render_sensor_monitoring_cards,
    render_ai_prediction_section,
    create_digital_trend_chart,
    render_alerts_panel,
    render_explainable_shap_panel,
    FILTER_SPECS,
    STATUS_NORMAL,
    STATUS_DEGRADING,
    STATUS_CLOGGED
)

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AquaGuard &bull; Digital AI Prognostics",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent


def _render_html(markup, sidebar=False):
    """Render indented HTML without Markdown treating it as a code block."""
    target = st.sidebar if sidebar else st
    target.markdown(textwrap.dedent(markup).strip(), unsafe_allow_html=True)



# ==================================================
# 2. AUTHENTICATION & ACCESS CONTROL
# ==================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

if not st.session_state["authenticated"]:
    render_auth_page()
    st.stop()


# ==================================================
# 3. INJECT 'LET'S GET DIGITAL' CSS THEME
# ==================================================

inject_custom_css()


# ==================================================
# 4. LOAD SIMULATOR AND MTNN PREDICTOR
# ==================================================

@st.cache_resource
def load_aquaguard():
    simulator = VirtualSensorSimulator()
    predictor = AquaGuardLivePredictor()
    return simulator, predictor


try:
    simulator, predictor = load_aquaguard()
except Exception as error:
    st.error(f"Could not initialize AquaGuard AI Engine: {error}")
    st.stop()


# ==================================================
# 5. SESSION STATE INITIALIZATION
# ==================================================

defaults = {
    "running": False,
    "sim_step": 0,
    "stream_speed": 2.0,
    "last_refresh_count": 0,
    "sensor_history": [],
    "current_reading": None,
    "current_prediction": None,
    "selected_filter": "sediment",
    "simulation_mode": "Automatic Live Simulation",
    "selected_scenario": "Normal",
    "cleaning_outcome": "Successful",
    "nav_section": "Dashboard",
    "trend_metric": "All Sensors"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 6. DIGITAL FROSTED GLASS SIDEBAR
# ==================================================

with st.sidebar:
    # A. Brand Header
    _render_html("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px; padding: 4px 0;">
            <div style="width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #0066FF 0%, #38bdf8 100%); display: flex; align-items: center; justify-content: center; font-size: 1.4rem; box-shadow: 0 6px 18px rgba(0, 102, 255, 0.45);">
                💧
            </div>
            <div>
                <div style="font-weight: 800; font-size: 1.2rem; color: #FFFFFF; letter-spacing: -0.3px;">
                    AquaGuard
                </div>
                <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">
                    Digital AI Studio
                </div>
            </div>
        </div>
    """)

    # Navigation is displayed horizontally at the top of the main page.
    st.divider()

    # C. Simulation Engine Controls
    st.markdown("<div style='font-size: 0.74rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.2px; margin-bottom: 8px;'>Telemetry Controller</div>", unsafe_allow_html=True)

    sim_mode = st.radio(
        "Simulation Mode",
        ["Automatic Live Simulation", "Scenario-Based Simulation"],
        index=0 if st.session_state["simulation_mode"] == "Automatic Live Simulation" else 1,
        label_visibility="collapsed"
    )
    st.session_state["simulation_mode"] = sim_mode

    # Active Filter Stage Selection
    st.markdown("<div style='font-size: 0.74rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.2px; margin-top: 12px; margin-bottom: 4px;'>Purifier Stage</div>", unsafe_allow_html=True)
    filter_keys = ["sediment", "carbon", "ro"]
    active_f_idx = filter_keys.index(st.session_state["selected_filter"]) if st.session_state["selected_filter"] in filter_keys else 0

    chosen_filter = st.selectbox(
        "Filter Stage",
        filter_keys,
        index=active_f_idx,
        format_func=lambda x: f"{FILTER_SPECS[x]['stage_num']} &bull; {FILTER_SPECS[x]['name']}",
        label_visibility="collapsed"
    )
    st.session_state["selected_filter"] = chosen_filter

    # Stream Controls
    if sim_mode == "Automatic Live Simulation":
        st.write("")
        c_p1, c_p2, c_p3 = st.columns([1.2, 1.2, 1])

        if not st.session_state.running:
            if c_p1.button("▶ Start", width="stretch"):
                st.session_state.running = True
                st.rerun()
            if c_p2.button("⏭ Next", width="stretch"):
                st.session_state.sim_step += 1
                st.rerun()
        else:
            if c_p1.button("⏸ Pause", width="stretch"):
                st.session_state.running = False
                st.rerun()
            if c_p2.button("↻ Step 0", width="stretch"):
                st.session_state.sim_step = 0
                st.rerun()

        if c_p3.button("🗑 Clear", width="stretch"):
            st.session_state.sensor_history = []
            st.toast("Telemetry buffer cleared")
            st.rerun()

        # Telemetry Clock Frequency
        clock_speed = st.slider(
            "Telemetry Clock (s)",
            min_value=0.5,
            max_value=4.0,
            value=float(st.session_state["stream_speed"]),
            step=0.5
        )
        st.session_state["stream_speed"] = clock_speed

        # Auto-refresh loop
        if st.session_state.running:
            refresh_count = st_autorefresh(
                interval=int(clock_speed * 1000),
                limit=None,
                key="aquaguard_live_refresh"
            )
            if refresh_count != st.session_state.last_refresh_count:
                st.session_state.sim_step += 1
                st.session_state.last_refresh_count = refresh_count

        reading = simulator.get_automatic_reading(
            chosen_filter,
            st.session_state.sim_step
        )

    else:
        st.session_state.running = False
        st.markdown("<div style='font-size: 0.74rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-top: 8px;'>Condition Injection</div>", unsafe_allow_html=True)

        scenarios = ["Normal", "Degrading", "Clogged", "Anomaly", "Cleaning"]
        chosen_scen = st.selectbox(
            "Select Scenario",
            scenarios,
            index=scenarios.index(st.session_state["selected_scenario"]) if st.session_state["selected_scenario"] in scenarios else 0,
            label_visibility="collapsed"
        )
        st.session_state["selected_scenario"] = chosen_scen

        cleaning_outcome = "Successful"
        if chosen_scen == "Cleaning":
            cleaning_outcome = st.selectbox(
                "Cleaning Outcome",
                ["Failed", "Partial", "Successful"],
                index=2
            )
            st.session_state["cleaning_outcome"] = cleaning_outcome

        reading = simulator.get_scenario_reading(
            filter_type=chosen_filter,
            scenario=chosen_scen,
            cleaning_outcome=cleaning_outcome
        )



# ==================================================
# 7. MTNN AI PREDICTION
# ==================================================

try:
    prediction = predictor.predict(reading)
except Exception as error:
    st.error(f"MTNN prediction pipeline failed: {error}")
    st.stop()

st.session_state.current_reading = reading
st.session_state.current_prediction = prediction


# ==================================================
# 8. BUFFER SENSOR HISTORY (100 OBSERVATIONS)
# ==================================================

if sim_mode == "Automatic Live Simulation" and st.session_state.running:
    if (
        not st.session_state.sensor_history
        or st.session_state.sensor_history[-1]["step"] != st.session_state.sim_step
    ):
        st.session_state.sensor_history.append({
            "step": st.session_state.sim_step,
            "pressure": float(reading["pressure_diff"]),
            "flow": float(reading["flow_rate"]),
            "turbidity": float(reading["turbidity"]),
            "temperature": float(reading["temperature"]),
            "fault": prediction["fault"]["status"]
        })
elif sim_mode == "Scenario-Based Simulation":
    st.session_state.sensor_history.append({
        "step": len(st.session_state.sensor_history) + 1,
        "pressure": float(reading["pressure_diff"]),
        "flow": float(reading["flow_rate"]),
        "turbidity": float(reading["turbidity"]),
        "temperature": float(reading["temperature"]),
        "fault": prediction["fault"]["status"]
    })

st.session_state.sensor_history = st.session_state.sensor_history[-100:]
history_df = pd.DataFrame(st.session_state.sensor_history) if st.session_state.sensor_history else pd.DataFrame()


# ==================================================
# 9. ICONIC 'LET'S GET DIGITAL' HERO BANNER
# ==================================================

op_hours = float(reading.get("operating_hours", 0.0))
purifier_unit_id = str(reading.get("purifier_id", "AQG-PRO-2026-X1"))

# Signed-in operator details are shown at the top-right of the dashboard.
render_user_sidebar(in_sidebar=False)

render_aquaguard_header(
    reading=reading,
    prediction=prediction,
    running=st.session_state["running"],
    sim_step=st.session_state["sim_step"],
    sim_mode=st.session_state["simulation_mode"],
    chosen_filter=st.session_state["selected_filter"]
)


# ==================================================
# 10. TOP DASHBOARD NAVIGATION
# ==================================================

nav_options = [
    "Dashboard",
    "Live Monitoring",
    "Filter Health",
    "RUL Predictions",
    "Anomaly Detection",
    "Cleaning Verification",
    "Explainable AI",
    "Sensor History",
    "Settings"
]

st.markdown(
    "<div style='font-size:0.74rem;font-weight:700;text-transform:uppercase;"
    "color:#94a3b8;letter-spacing:1.2px;margin:14px 0 6px 0;'>"
    "AQUAGUARD NAVIGATION</div>",
    unsafe_allow_html=True
)

selected_nav = st.radio(
    "Dashboard navigation",
    nav_options,
    index=nav_options.index(st.session_state["nav_section"])
        if st.session_state["nav_section"] in nav_options else 0,
    horizontal=True,
    label_visibility="collapsed",
    key="top_nav_selector"
)
st.session_state["nav_section"] = selected_nav


# ==================================================
# 11. NAVIGATION ROUTING
# ==================================================

nav = st.session_state["nav_section"]

# --------------------------------------------------
# SECTION: DASHBOARD
# --------------------------------------------------
if nav == "Dashboard":

    # 1. Four Frosted Glass Sensor Telemetry Cards
    st.markdown("<div style='font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin: 10px 0 8px 0;'>Virtual IoT Sensor Stream</div>", unsafe_allow_html=True)
    render_sensor_monitoring_cards(reading, history_df)

    st.write("")

    # 2. Four AI Prediction Cards
    st.markdown("<div style='font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin: 14px 0 8px 0;'>Multi-Task Neural Network (MTNN) Prognostics</div>", unsafe_allow_html=True)
    render_ai_prediction_section(prediction, reading)

    st.write("")

    # 3. Two-Column Layout: Chrono-Graph + Alerts
    col_chart, col_side = st.columns([1.65, 1.0])

    with col_chart:
        st.markdown("<div style='font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 8px;'>Multi-Sensor Telemetry Chrono-Graph</div>", unsafe_allow_html=True)
        if not history_df.empty:
            view_choice = st.selectbox(
                "Filter Sensor Channel",
                ["All Sensors", "Differential Pressure", "Flow Rate", "Turbidity", "Temperature"],
                index=["All Sensors", "Differential Pressure", "Flow Rate", "Turbidity", "Temperature"].index(st.session_state["trend_metric"]),
                key="trend_selector_main"
            )
            st.session_state["trend_metric"] = view_choice
            fig_trend = create_digital_trend_chart(history_df, view_choice)
            st.plotly_chart(fig_trend, width="stretch")
        else:
            st.info("Start simulation to display real-time sensor trajectories.")

    with col_side:
        st.markdown("<div style='font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 8px;'>Prognostic Alerts & Advisories</div>", unsafe_allow_html=True)
        render_alerts_panel(prediction, reading)

    st.write("")

    # 4. Multi-Stage Filter Health Diagnostics
    st.markdown("<div style='font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin: 14px 0 8px 0;'>Purifier Multi-Stage Health State</div>", unsafe_allow_html=True)
    c_f1, c_f2, c_f3 = st.columns(3)

    for col, stage_key in zip([c_f1, c_f2, c_f3], ["sediment", "carbon", "ro"]):
        stage_spec = FILTER_SPECS[stage_key]
        stage_reading = simulator.get_automatic_reading(stage_key, st.session_state.sim_step)
        stage_pred = predictor.predict(stage_reading)
        s_fault = stage_pred["fault"]
        s_rul = float(stage_pred["rul_days"])
        s_col = STATUS_NORMAL if s_fault["status"] == "Normal" else STATUS_DEGRADING if s_fault["status"] == "Degrading" else STATUS_CLOGGED

        with col:
            _render_html(f"""
                <div class="digital-glass-panel">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.72rem; font-weight: 700; color: #94a3b8; letter-spacing: 1px;">{stage_spec['stage_num']}</span>
                        <span style="font-size: 0.76rem; font-weight: 700; color: {s_col};">● {s_fault['status']}</span>
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;">
                        {stage_spec['name']}
                    </div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 8px;">
                        Pore: <strong>{stage_spec['pore']}</strong> &bull; {stage_spec['material']}
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: #94a3b8; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 8px;">
                        <span>Estimated RUL: <strong style="color: #FFFFFF;">~{s_rul:.0f} days</strong></span>
                        <span>Confidence: <strong style="color: #FFFFFF;">{s_fault['confidence']*100:.0f}%</strong></span>
                    </div>
                </div>
            """)

    st.write("")

    # 5. Explainable AI Preview
    with st.expander("Explainable AI (SHAP) Diagnostics"):
        render_explainable_shap_panel(BASE_DIR)

    # 6. Raw IoT Telemetry Table
    with st.expander("Raw Virtual IoT Telemetry Payload"):
        clean_dict = {
            k: (v.item() if isinstance(v, np.generic) else v)
            for k, v in reading.to_dict().items()
        }
        # Telemetry contains numeric readings and text labels. Convert values to
        # strings so Arrow receives one consistent column type.
        df_raw = pd.DataFrame({
            "Telemetry Signal": list(clean_dict.keys()),
            "Transducer Value": [str(value) for value in clean_dict.values()]
        })
        st.dataframe(df_raw, width="stretch", hide_index=True)


# --------------------------------------------------
# SECTION: LIVE MONITORING
# --------------------------------------------------
elif nav == "Live Monitoring":
    st.markdown("### 📡 Live Transducer Telemetry & Gauge Array")
    render_sensor_monitoring_cards(reading, history_df)

    st.write("")
    st.markdown("#### High-Resolution Time-Series Trace")
    if not history_df.empty:
        metric_opt = st.radio(
            "Select Trace",
            ["All Sensors", "Differential Pressure", "Flow Rate", "Turbidity", "Temperature"],
            horizontal=True
        )
        fig_live = create_digital_trend_chart(history_df, metric_opt)
        st.plotly_chart(fig_live, width="stretch")
    else:
        st.info("Start simulation stream to collect sensor observations.")


# --------------------------------------------------
# SECTION: FILTER HEALTH
# --------------------------------------------------
elif nav == "Filter Health":
    st.markdown("### 🩺 Multi-Stage Filter Health & Diagnostics")

    c1, c2, c3 = st.columns(3)
    for col, stage_key in zip([c1, c2, c3], ["sediment", "carbon", "ro"]):
        spec = FILTER_SPECS[stage_key]
        s_read = simulator.get_automatic_reading(stage_key, st.session_state.sim_step)
        s_pred = predictor.predict(s_read)
        fault = s_pred["fault"]
        rul = float(s_pred["rul_days"])
        col_st = STATUS_NORMAL if fault["status"] == "Normal" else STATUS_DEGRADING if fault["status"] == "Degrading" else STATUS_CLOGGED

        with col:
            _render_html(f"""
                <div class="digital-glass-panel">
                    <div style="font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase;">
                        {spec['stage_num']} &bull; {spec['material']}
                    </div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;">
                        {spec['name']}
                    </div>
                    <div style="font-size: 2rem; font-weight: 800; color: {col_st}; margin: 6px 0;">
                        {fault['status']}
                    </div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.5;">
                        • Confidence: <strong>{fault['confidence']*100:.1f}%</strong><br>
                        • Nominal Flow: <strong>{spec['flow']}</strong><br>
                        • Operating ΔP: <strong>{spec['nominal_p']}</strong><br>
                        • Projected Life: <strong>~{rul:.0f} days</strong>
                    </div>
                </div>
            """)


# --------------------------------------------------
# SECTION: RUL PREDICTIONS
# --------------------------------------------------
elif nav == "RUL Predictions":
    st.markdown("### ⏳ Remaining Useful Life (RUL) Prognostics")
    rul = float(prediction["rul_days"])
    rul_pct = (min(max(rul, 0.0), 180.0) / 180.0) * 100.0
    rul_color = STATUS_NORMAL if rul > 40 else STATUS_DEGRADING if rul > 15 else STATUS_CLOGGED

    c_rul1, c_rul2 = st.columns([1, 1.5])
    with c_rul1:
        _render_html(f"""
            <div class="digital-glass-panel" style="text-align: center;">
                <div style="font-size: 0.76rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Estimated Remaining Useful Life</div>
                <div style="font-size: 3.2rem; font-weight: 800; color: {rul_color}; margin: 8px 0;">
                    {rul:.1f}
                </div>
                <div style="font-size: 1rem; color: #cbd5e1; font-weight: 600;">
                    Calendar Days to Threshold
                </div>
                <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 14px;">
                    Cycle Wear Factor: <strong>{100 - rul_pct:.1f}%</strong>
                </div>
            </div>
        """)

    with c_rul2:
        _render_html("""
            <div class="digital-glass-panel">
                <div style="font-weight: 700; font-size: 1rem; color: #FFFFFF; margin-bottom: 8px;">
                    Maintenance Scheduling Advisory
                </div>
                <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6;">
                    • <strong>Current Filter:</strong> Sediment Pre-Filter Stage<br>
                    • <strong>Estimated Service Window:</strong> Standard scheduled replacement within 30 days.<br>
                    • <strong>Degradation Rate:</strong> Non-linear parabolic pore accumulation model.<br>
                    • <strong>Neural Latent Confidence:</strong> MTNN RUL head normalized against 180-day baseline.
                </div>
            </div>
        """)


# --------------------------------------------------
# SECTION: ANOMALY DETECTION
# --------------------------------------------------
elif nav == "Anomaly Detection":
    st.markdown("### 🛡️ Sentinel Anomaly Detection & Isolation")
    anomaly = prediction["anomaly"]
    anom_prob = anomaly["probability"] * 100.0
    anom_status = "ANOMALY FLAGGED" if anomaly["detected"] else "ALL SIGNALS NOMINAL"
    anom_col = STATUS_CLOGGED if anomaly["detected"] else STATUS_NORMAL

    col_a1, col_a2 = st.columns([1, 1.5])
    with col_a1:
        _render_html(f"""
            <div class="digital-glass-panel" style="text-align: center;">
                <div style="font-size: 0.76rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Neural Anomaly Classifier</div>
                <div style="font-size: 2.8rem; font-weight: 800; color: {anom_col}; margin: 8px 0;">
                    {anom_prob:.1f}%
                </div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">
                    {anom_status}
                </div>
                <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 10px;">
                    Threshold: 50.0% Sigmoid Boundary
                </div>
            </div>
        """)

    with col_a2:
        _render_html("""
            <div class="digital-glass-panel">
                <div style="font-weight: 700; font-size: 1rem; color: #FFFFFF; margin-bottom: 8px;">
                    Transducer Verification Analysis
                </div>
                <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6;">
                    The MTNN anomaly detection branch isolates multivariate sensor incongruities, such as sudden pressure drops without flow increases or high turbidity spikes without corresponding pre-filter delta.
                </div>
            </div>
        """)


# --------------------------------------------------
# SECTION: CLEANING VERIFICATION
# --------------------------------------------------
elif nav == "Cleaning Verification":
    st.markdown("### 🧹 Filter Regeneration & Cleaning Verification")
    cleaning = prediction.get("cleaning")

    if cleaning is not None:
        c_status = cleaning["status"]
        c_col = STATUS_NORMAL if c_status == "Successful" else STATUS_DEGRADING if c_status == "Partial" else STATUS_CLOGGED
        pre_p = float(reading.get("pre_pressure", 0.0))
        post_p = float(reading.get("post_pressure", 0.0))
        pre_f = float(reading.get("pre_flow", 0.0))
        post_f = float(reading.get("post_flow", 0.0))

        c1, c2 = st.columns(2)
        with c1:
            _render_html(f"""
                <div class="digital-glass-panel">
                    <div style="font-size: 0.76rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Cleaning Outcome</div>
                    <div style="font-size: 2.4rem; font-weight: 800; color: {c_col}; margin: 6px 0;">
                        {c_status}
                    </div>
                    <div style="font-size: 0.82rem; color: #cbd5e1;">
                        Recovery Efficiency: <strong>{cleaning['probabilities'].get(c_status, 1.0)*100:.1f}%</strong>
                    </div>
                </div>
            """)

        with c2:
            _render_html(f"""
                <div class="digital-glass-panel">
                    <div style="font-size: 0.76rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Pre vs Post Dynamics</div>
                    <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6; margin-top: 6px;">
                        • Pre-Cleaning ΔP: <strong>{pre_p:.2f} bar</strong> &bull; Post-Cleaning ΔP: <strong>{post_p:.2f} bar</strong><br>
                        • Pre-Cleaning Flow: <strong>{pre_f:.2f} L/min</strong> &bull; Post-Cleaning Flow: <strong>{post_f:.2f} L/min</strong><br>
                        • Permeability Recovery: <strong>{max(0.0, (pre_p - post_p)/pre_p * 100 if pre_p > 0 else 0):.1f}%</strong>
                    </div>
                </div>
            """)
    else:
        st.info("No active cleaning event in the current telemetry frame. Switch to 'Scenario-Based Simulation' and select 'Cleaning' in the sidebar to simulate restorative backwash.")


# --------------------------------------------------
# SECTION: EXPLAINABLE AI
# --------------------------------------------------
elif nav == "Explainable AI":
    st.markdown("### 🧠 Explainable AI & SHAP Attribution Suite")
    render_explainable_shap_panel(BASE_DIR)


# --------------------------------------------------
# SECTION: SENSOR HISTORY
# --------------------------------------------------
elif nav == "Sensor History":
    st.markdown("### 📈 Sensor History Telemetry Log")
    if not history_df.empty:
        st.plotly_chart(create_digital_trend_chart(history_df, "All Sensors"), width="stretch")
        st.dataframe(history_df, width="stretch", hide_index=True)
    else:
        st.info("No sensor history recorded yet. Start simulation stream from sidebar.")


# --------------------------------------------------
# SECTION: SETTINGS
# --------------------------------------------------
elif nav == "Settings":
    st.markdown("### ⚙️ System Settings & Calibrations")
    _render_html("""
        <div class="digital-glass-panel">
            <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF; margin-bottom: 6px;">AquaGuard Purifier Calibration Profile</div>
            <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6;">
                • Model Version: <code>AquaGuard-MTNN-v1.4</code><br>
                • Model Checkpoint: <code>models/aquaguard_mtnn.pth</code><br>
                • Preprocessing Scaler: <code>models/preprocessing.pkl</code><br>
                • Transducer Interface: <code>Simulated 4-Channel Virtual Transducer</code><br>
                • Theme: <code>'Let's Get Digital' Frosted Glassmorphism</code>
            </div>
        </div>
    """)


# ==================================================
# 11. DIGITAL FOOTER
# ==================================================

st.divider()

_render_html("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; padding: 12px 0;">
        AquaGuard &bull; Intelligent Water Purifier Prognostics Lab<br>
        <span style="font-size: 0.74rem; color: rgba(255, 255, 255, 0.45);">
            Multi-Task Neural Network &bull; Virtual IoT Transducers &bull; SHAP Explainability Engine
        </span>
    </div>
""")
