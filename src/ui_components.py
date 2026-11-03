"""
UI Components for AquaGuard.
Theme: 'Let's Get Digital' – azure-to-obsidian gradient, frosted glassmorphism,
electric cobalt #0066FF accents, uppercase tracked typography.
Layout: matches the screenshot structure with tabs-based navigation.
"""

import streamlit as st
import textwrap
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# ==================================================
# THEME PALETTE
# ==================================================
COLOR_BG_DEEP   = "#050811"
COLOR_BG_SLATE  = "#0b111e"
COLOR_AZURE     = "#0066FF"
COLOR_SKY       = "#38bdf8"
COLOR_WHITE     = "#FFFFFF"
COLOR_MUTED     = "#94a3b8"
COLOR_BORDER    = "rgba(255, 255, 255, 0.22)"

STATUS_NORMAL   = "#10b981"
STATUS_DEGRADING = "#f59e0b"
STATUS_CLOGGED  = "#ef4444"


def _render_html(markup, sidebar=False):
    """Dedent custom HTML before passing it to Streamlit Markdown."""
    target = st.sidebar if sidebar else st
    target.markdown(textwrap.dedent(markup).strip(), unsafe_allow_html=True)


FILTER_SPECS = {
    "sediment": {
        "stage_num": "STAGE 01",
        "name": "Sediment Pre-Filter",
        "material": "Melt-Blown Polypropylene",
        "pore": "5.0 µm",
        "flow": "2.0 – 2.4 L/min",
        "nominal_p": "0.10 – 0.35 bar",
        "target": "Silt, Sand, Rust & Suspended Particulates",
        "icon": "🧱",
        "label": "Stage 1 (Sediment)"
    },
    "carbon": {
        "stage_num": "STAGE 02",
        "name": "Activated Carbon Block",
        "material": "Extruded Carbon Block",
        "pore": "1.0 µm",
        "flow": "1.6 – 2.0 L/min",
        "nominal_p": "0.15 – 0.45 bar",
        "target": "Chlorine, Pesticides, VOCs & Odor",
        "icon": "⬛",
        "label": "Stage 2 (Carbon)"
    },
    "ro": {
        "stage_num": "STAGE 03",
        "name": "RO Polyamide Membrane",
        "material": "Thin-Film Composite (TFC)",
        "pore": "0.0001 µm",
        "flow": "1.2 – 1.6 L/min",
        "nominal_p": "0.20 – 0.60 bar",
        "target": "Dissolved Solids (TDS), Heavy Metals & Pathogens",
        "icon": "🔬",
        "label": "Stage 3 (RO Membrane)"
    }
}


# ==================================================
# CSS INJECTION
# ==================================================

def inject_custom_css():
    """Injects the 'Let's Get Digital' theme CSS."""
    _render_html(f"""
        <style>
        /* ── Remove Streamlit's top chrome and reclaim viewport space ── */
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        #MainMenu,
        footer {{
            display: none !important;
            height: 0 !important;
            visibility: hidden !important;
        }}

        [data-testid="stAppViewContainer"] {{
            padding-top: 0 !important;
        }}

        [data-testid="stMain"] {{
            padding-top: 0 !important;
        }}

        .stMainBlockContainer,
        section.main > div.block-container {{
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }}

        /* ── Global Background ── */
        .stApp {{
            background: radial-gradient(circle at 15% 5%, rgba(0, 102, 255, 0.32) 0%, transparent 42%),
                        radial-gradient(circle at 85% 12%, rgba(56, 189, 248, 0.18) 0%, transparent 38%),
                        linear-gradient(180deg, #0e1c36 0%, #070e1c 45%, #03060d 100%) !important;
            color: #FFFFFF !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif !important;
        }}

        /* ── Scrollbars ── */
        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: #050811; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.18); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(0,102,255,0.55); }}

        /* ── Keyframes ── */
        @keyframes pulseDot {{
            0%   {{ opacity: 1; transform: scale(1); }}
            50%  {{ opacity: 0.3; transform: scale(0.82); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(14px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        /* ── AquaGuard Header Card ── */
        .aq-header-card {{
            background: linear-gradient(135deg, rgba(0,102,255,0.14) 0%, rgba(255,255,255,0.04) 60%, rgba(0,0,0,0.15) 100%);
            border: 1px solid rgba(0,102,255,0.35);
            border-radius: 18px;
            padding: 26px 30px 20px 30px;
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.12);
            margin-bottom: 6px;
            animation: fadeInUp 0.5s ease both;
        }}

        .aq-logo-row {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 8px;
        }}

        .aq-logo-title {{
            font-size: 2.4rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.8px;
            line-height: 1;
        }}

        .aq-version-badge {{
            background: rgba(0,102,255,0.25);
            border: 1px solid rgba(0,102,255,0.5);
            color: #60a5fa;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 4px 10px;
            border-radius: 6px;
            text-transform: uppercase;
            vertical-align: middle;
        }}

        .aq-subtitle {{
            font-size: 0.84rem;
            color: #94a3b8;
            margin-bottom: 14px;
            font-weight: 400;
        }}

        .aq-status-row {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .aq-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 9999px;
            padding: 5px 12px;
            font-size: 0.76rem;
            font-weight: 600;
            color: #cbd5e1;
            white-space: nowrap;
        }}

        /* ── Standard Frosted Glass Panel ── */
        .digital-glass-panel {{
            background: linear-gradient(135deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.02) 100%);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 16px;
            padding: 20px 22px;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
            transition: all 0.28s cubic-bezier(0.25,0.8,0.25,1);
            position: relative;
            overflow: hidden;
        }}

        .digital-glass-panel:hover {{
            border-color: rgba(255,255,255,0.24);
            transform: translateY(-2px);
            box-shadow: 0 18px 40px rgba(0,102,255,0.18);
        }}

        /* ── Sensor Cards ── */
        .sensor-card {{
            background: linear-gradient(145deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.01) 100%);
            border: 1px solid rgba(255,255,255,0.11);
            border-radius: 16px;
            padding: 18px 20px 14px 20px;
            backdrop-filter: blur(18px);
            box-shadow: 0 8px 28px rgba(0,0,0,0.45);
            transition: all 0.25s ease;
            height: 100%;
        }}

        .sensor-card:hover {{
            border-color: rgba(0,102,255,0.35);
            transform: translateY(-2px);
            box-shadow: 0 14px 36px rgba(0,0,0,0.55);
        }}

        .sensor-eyebrow {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.6px;
            color: rgba(255,255,255,0.5);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .sensor-value {{
            font-size: 2.6rem;
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: -0.5px;
            line-height: 1;
            margin-bottom: 2px;
        }}

        .sensor-unit {{
            font-size: 1rem;
            font-weight: 400;
            color: rgba(255,255,255,0.6);
            margin-left: 4px;
        }}

        .sensor-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 600;
            margin-top: 10px;
        }}

        .pill-normal   {{ background: rgba(16,185,129,0.18); color: {STATUS_NORMAL}; border: 1px solid rgba(16,185,129,0.3); }}
        .pill-warning  {{ background: rgba(245,158,11,0.18); color: {STATUS_DEGRADING}; border: 1px solid rgba(245,158,11,0.3); }}
        .pill-danger   {{ background: rgba(239,68,68,0.18);  color: {STATUS_CLOGGED}; border: 1px solid rgba(239,68,68,0.3); }}

        /* ── Prediction Cards ── */
        .pred-card {{
            background: linear-gradient(145deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.01) 100%);
            border: 1px solid rgba(255,255,255,0.11);
            border-radius: 16px;
            padding: 18px 20px;
            backdrop-filter: blur(18px);
            box-shadow: 0 8px 28px rgba(0,0,0,0.45);
            transition: all 0.25s ease;
            height: 100%;
        }}

        .pred-card:hover {{
            border-color: rgba(255,255,255,0.22);
            transform: translateY(-2px);
            box-shadow: 0 14px 36px rgba(0,0,0,0.55);
        }}

        .pred-eyebrow {{
            font-size: 0.66rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: rgba(255,255,255,0.45);
            margin-bottom: 8px;
        }}

        .pred-value {{
            font-size: 1.9rem;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 4px;
        }}

        .pred-sub {{
            font-size: 0.75rem;
            color: #94a3b8;
            line-height: 1.4;
        }}

        /* ── Progress Bar ── */
        .conf-bar-bg {{
            background: rgba(255,255,255,0.1);
            border-radius: 9999px;
            height: 4px;
            width: 100%;
            margin: 8px 0;
            overflow: hidden;
        }}

        /* ── Live Filter HUD (sidebar) ── */
        .hud-card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 14px;
            padding: 12px 14px;
            margin: 10px 0;
        }}

        .hud-header {{
            font-size: 0.66rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: rgba(255,255,255,0.5);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .hud-active-dot {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 0.62rem;
            font-weight: 700;
            color: {STATUS_NORMAL};
        }}

        .live-dot {{
            width: 7px; height: 7px;
            border-radius: 50%;
            background: {STATUS_NORMAL};
            box-shadow: 0 0 8px {STATUS_NORMAL};
            animation: pulseDot 1.8s infinite;
            display: inline-block;
        }}

        /* ── Alerts ── */
        .alert-item {{
            background: rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 11px 14px;
            margin-bottom: 8px;
        }}

        .alert-title {{
            font-size: 0.84rem;
            font-weight: 700;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 7px;
        }}

        .alert-desc {{
            font-size: 0.76rem;
            color: #94a3b8;
            margin-top: 3px;
            line-height: 1.4;
        }}

        /* ── Floating glass sidebar: viewport-fitted, no visible overflow ── */
        section[data-testid="stSidebar"] {{
            background: transparent !important;
            border: 0 !important;
            min-width: 300px !important;
            max-width: 300px !important;
            padding: 10px 0 10px 14px !important;
            box-sizing: border-box !important;
        }}

        section[data-testid="stSidebar"] > div {{
            height: calc(100dvh - 20px) !important;
            max-height: calc(100dvh - 20px) !important;
            min-height: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            background: linear-gradient(160deg, rgba(13, 29, 55, 0.97) 0%, rgba(5, 10, 22, 0.98) 100%) !important;
            border: 1px solid rgba(148, 190, 255, 0.18) !important;
            border-radius: 22px !important;
            box-shadow: 0 18px 48px rgba(0, 0, 0, 0.48), inset 0 1px 0 rgba(255,255,255,0.08) !important;
            overflow: hidden !important;
            backdrop-filter: blur(22px);
            -webkit-backdrop-filter: blur(22px);
        }}

        section[data-testid="stSidebar"] div[data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {{
            height: 100% !important;
            max-height: 100% !important;
            min-height: 0 !important;
            overflow: hidden !important;
            padding: 8px 10px 8px 10px !important;
            box-sizing: border-box !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlock"] {{
            height: 100% !important;
            min-height: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0.28rem !important;
        }}

        /* The profile card is the second-last sidebar block; push it and Sign Out down. */
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlock"] > div:nth-last-child(2) {{
            margin-top: auto !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.28rem !important;
        }}

        section[data-testid="stSidebar"] hr {{
            margin: 0.18rem 0 !important;
        }}

        section[data-testid="stSidebar"] div.stButton > button {{
            min-height: 1.9rem !important;
            height: 1.9rem !important;
            padding: 0.2rem 0.45rem !important;
            font-size: 0.68rem !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
            font-size: 0.76rem !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {{
            margin-bottom: 0 !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stSlider"] {{
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }}

        section[data-testid="stSidebar"] .hud-card {{
            padding: 8px 10px !important;
            margin: 4px 0 !important;
        }}

        section[data-testid="stSidebar"] .stMarkdown p {{
            margin-bottom: 0.2rem !important;
        }}

        section[data-testid="stSidebar"] .stMarkdown div[style*="margin-bottom: 14px"] {{
            margin-bottom: 4px !important;
        }}

        @media (max-height: 900px) {{
            section[data-testid="stSidebar"] {{
                padding-top: 6px !important;
                padding-bottom: 6px !important;
            }}
            section[data-testid="stSidebar"] div[data-testid="stSidebarContent"],
            section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {{
                padding-top: 5px !important;
                padding-bottom: 5px !important;
            }}
            section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
                gap: 0.2rem !important;
            }}
            section[data-testid="stSidebar"] .stMarkdown p {{
                font-size: 0.72rem !important;
                line-height: 1.25 !important;
            }}
        }}

        /* Comfortable spacing between sidebar controls */
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.62rem !important;
        }}
        section[data-testid="stSidebar"] .stMarkdown p {{
            margin-top: 0.18rem !important;
            margin-bottom: 0.38rem !important;
            line-height: 1.42 !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stRadio"] {{
            margin-top: 0.12rem !important;
            margin-bottom: 0.42rem !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {{
            gap: 0.36rem !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSelectbox"] {{
            margin-top: 0.12rem !important;
            margin-bottom: 0.38rem !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSlider"] {{
            margin-top: 0.18rem !important;
            margin-bottom: 0.45rem !important;
        }}
        section[data-testid="stSidebar"] hr {{
            margin-top: 0.42rem !important;
            margin-bottom: 0.42rem !important;
        }}
        section[data-testid="stSidebar"] .stButton {{
            margin-top: 0.12rem !important;
            margin-bottom: 0.22rem !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{
            gap: 0.42rem !important;
            margin-top: 0.18rem !important;
            margin-bottom: 0.28rem !important;
        }}
        @media (max-height: 900px) {{
            section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.48rem !important; }}
            section[data-testid="stSidebar"] .stMarkdown p {{ margin-bottom: 0.28rem !important; line-height: 1.35 !important; }}
        }}

        /* ── Buttons ── */
        div.stButton > button {{
            background: #0066FF !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.22) !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.9px !important;
            box-shadow: 0 5px 18px rgba(0,102,255,0.38) !important;
            transition: all 0.22s ease !important;
        }}

        div.stButton > button:hover {{
            background: #1a75ff !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 9px 26px rgba(0,102,255,0.55) !important;
        }}

        /* ── Tab styling ── */
        button[data-baseweb="tab"] {{
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: #94a3b8 !important;
            padding: 8px 4px !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important;
            border-bottom: 2px solid #0066FF !important;
        }}

        div[data-baseweb="tab-list"] {{
            background: transparent !important;
            border-bottom: 1px solid rgba(255,255,255,0.1) !important;
            gap: 24px !important;
        }}

        /* ── Section heading ── */
        .section-heading {{
            font-size: 1.35rem;
            font-weight: 700;
            color: #FFFFFF;
            margin: 18px 0 12px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* ── Divider ── */
        hr {{ border-color: rgba(255,255,255,0.08) !important; }}

        /* ── Inputs / selects ── */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div:first-child {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
        }}
        </style>
    """)


# ==================================================
# HELPER SVG GENERATORS
# ==================================================

def _sparkline_svg(values: List[float], color: str = "#0066FF",
                   width: int = 110, height: int = 30) -> str:
    if not values or len(values) < 2:
        values = [1.0, 1.05, 0.98, 1.02, 1.01]
    pts = values[-14:]
    mn, mx = min(pts), max(pts)
    span = mx - mn if mx != mn else 1.0
    step = width / (len(pts) - 1)
    coords = [f"{i*step:.1f},{height - ((v - mn)/span*(height-6)+3):.1f}"
              for i, v in enumerate(pts)]
    last_x = (len(pts)-1)*step
    area = (f"M {coords[0]} " + " ".join(f"L {c}" for c in coords[1:])
            + f" L {last_x:.1f},{height} L 0,{height} Z")
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="overflow:visible">
        <path d="{area}" fill="{color}" fill-opacity="0.1"/>
        <polyline fill="none" stroke="{color}" stroke-width="1.8"
                  stroke-linecap="round" stroke-linejoin="round"
                  points="{' '.join(coords)}"/>
        <circle cx="{coords[-1].split(',')[0]}" cy="{coords[-1].split(',')[1]}"
                r="2.8" fill="{color}"/>
    </svg>"""


def _arc_gauge_svg(pct: float, color: str = "#0066FF", size: int = 66) -> str:
    p = min(max(pct, 0.0), 100.0)
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 36 36"
         style="transform:rotate(-90deg)">
        <path d="M18 2.0845 a15.9155 15.9155 0 0 1 0 31.831 a15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="3"/>
        <path d="M18 2.0845 a15.9155 15.9155 0 0 1 0 31.831 a15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" stroke="{color}" stroke-width="3.2"
              stroke-dasharray="{p:.1f},100" stroke-linecap="round"/>
    </svg>"""


def _sensor_status_label(metric: str, value: float) -> tuple:
    """Returns (label_text, pill_css_class) based on sensor metric and value."""
    if metric == "pressure":
        if value < 0.20:
            return "Normal Flow", "pill-normal"
        elif value < 0.45:
            return "Slightly Elevated", "pill-warning"
        else:
            return "High Pressure", "pill-danger"
    elif metric == "flow":
        if value >= 1.9:
            return "High Throughput", "pill-normal"
        elif value >= 1.2:
            return "Normal Flow", "pill-normal"
        else:
            return "Low Flow", "pill-warning"
    elif metric == "turbidity":
        if value < 1.5:
            return "Crystal Clear", "pill-normal"
        elif value < 5.0:
            return "Slightly Turbid", "pill-warning"
        else:
            return "High Turbidity", "pill-danger"
    elif metric == "temperature":
        if 18 <= value <= 30:
            return "Ideal Temp", "pill-normal"
        elif value > 30:
            return "High Temp", "pill-warning"
        else:
            return "Low Temp", "pill-warning"
    return "Nominal", "pill-normal"


# ==================================================
# AQUAGUARD HEADER
# ==================================================

def render_aquaguard_header(reading, prediction, running: bool,
                             sim_step: int, sim_mode: str,
                             chosen_filter: str):
    """Renders the wide AquaGuard header card matching the screenshot."""
    now_str = datetime.now().strftime("%d %b %Y  %H:%M:%S")
    spec     = FILTER_SPECS.get(chosen_filter, FILTER_SPECS["sediment"])
    op_hours = float(reading.get("operating_hours", 0.0))

    if running:
        sim_dot   = f'<span class="live-dot"></span>'
        sim_label = "Simulation Running"
    else:
        sim_dot   = '<span style="width:7px;height:7px;border-radius:50%;background:#f59e0b;display:inline-block;"></span>'
        sim_label = "Simulation Paused"

    _render_html(f"""
        <div class="aq-header-card">
            <div class="aq-logo-row">
                <span style="font-size:2rem;">💧</span>
                <span class="aq-logo-title">AquaGuard</span>
                <span class="aq-version-badge">AI Prognostics v2.0</span>
            </div>
            <div class="aq-subtitle">
                Deep Multi-Task Neural Network (MTNN) Filter Health &amp; Predictive Maintenance Platform
            </div>
            <div class="aq-status-row">
                <span class="aq-status-pill">
                    {sim_dot} {sim_label}
                </span>
                <span class="aq-status-pill">
                    💧 {spec['stage_num'].replace('STAGE ', 'Stage ')} — {spec['name'].upper()[:18]}
                </span>
                <span class="aq-status-pill">
                    ⏱ Operating Hours: {op_hours:.1f} hrs
                </span>
                <span class="aq-status-pill">
                    ⚙ Mode: {sim_mode.replace(' Simulation', '')}
                </span>
                <span class="aq-status-pill">
                    🤖 AI Engine: MTNN Active
                </span>
            </div>
        </div>
    """)


# ==================================================
# SIDEBAR LIVE FILTER HUD
# ==================================================

def render_live_filter_hud(prediction: Dict[str, Any]):
    """Renders the 'LIVE FILTER PROGNOSIS HUD' sidebar widget."""
    fault     = prediction["fault"]
    rul       = float(prediction["rul_days"])
    anomaly   = prediction["anomaly"]
    status    = fault["status"]
    conf      = fault["confidence"] * 100.0
    anom_prob = anomaly["probability"] * 100.0
    s_col     = STATUS_NORMAL if status == "Normal" else STATUS_DEGRADING if status == "Degrading" else STATUS_CLOGGED

    _render_html(f"""
        <div class="hud-card">
            <div class="hud-header">
                ⚡ LIVE FILTER PROGNOSIS HUD
                <span class="hud-active-dot">
                    <span class="live-dot"></span> ACTIVE
                </span>
            </div>
            <div style="font-size:1.55rem; font-weight:800; color:{s_col}; margin-bottom:2px;">
                {status}
            </div>
            <div style="font-size:0.95rem; font-weight:700; color:{s_col}; margin-bottom:8px;">
                ~{rul:.0f}d RUL
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#94a3b8;">
                <span>Confidence: <strong style="color:#e2e8f0;">{conf:.1f}%</strong></span>
                <span>Anomaly: <strong style="color:#e2e8f0;">{anom_prob:.1f}%</strong></span>
            </div>
        </div>
    """, sidebar=True)


# ==================================================
# SENSOR MONITORING CARDS
# ==================================================

def render_sensor_monitoring_cards(reading: Dict[str, Any],
                                   history_df: Optional[pd.DataFrame] = None):
    """Renders 4 frosted sensor cards matching the screenshot layout."""
    p_diff    = float(reading.get("pressure_diff", 0.0))
    flow      = float(reading.get("flow_rate", 0.0))
    turbidity = float(reading.get("turbidity", 0.0))
    temp      = float(reading.get("temperature", 0.0))

    if history_df is not None and not history_df.empty:
        p_hist   = history_df["pressure"].tolist()
        f_hist   = history_df["flow"].tolist()
        t_hist   = history_df["turbidity"].tolist()
        tmp_hist = history_df["temperature"].tolist()
    else:
        p_hist   = [p_diff   * r for r in [0.96, 1.02, 0.98, 1.01, 1.0]]
        f_hist   = [flow      * r for r in [1.02, 0.97, 1.01, 0.99, 1.0]]
        t_hist   = [turbidity * r for r in [0.94, 1.06, 0.99, 1.02, 1.0]]
        tmp_hist = [temp + d for d in [-0.2, 0.15, -0.1, 0.05, 0.0]]

    p_lbl, p_cls     = _sensor_status_label("pressure",    p_diff)
    f_lbl, f_cls     = _sensor_status_label("flow",        flow)
    t_lbl, t_cls     = _sensor_status_label("turbidity",   turbidity)
    tmp_lbl, tmp_cls = _sensor_status_label("temperature", temp)

    sensors = [
        ("DIFFERENTIAL PRESSURE", "💨", f"{p_diff:.2f}", "kPa",  _sparkline_svg(p_hist, "#38bdf8"),   p_lbl, p_cls),
        ("WATER FLOW RATE",       "🌊", f"{flow:.2f}",   "L/min", _sparkline_svg(f_hist, "#0066FF"),   f_lbl, f_cls),
        ("WATER TURBIDITY",       "🧪", f"{turbidity:.2f}", "NTU", _sparkline_svg(t_hist, "#f59e0b"),  t_lbl, t_cls),
        ("TEMPERATURE",           "🌡️", f"{temp:.2f}",  "°C",   _sparkline_svg(tmp_hist, "#10b981"),  tmp_lbl, tmp_cls),
    ]

    cols = st.columns(4)
    for col, (label, icon, val, unit, spark, status_lbl, status_cls) in zip(cols, sensors):
        with col:
            _render_html(f"""
                <div class="sensor-card">
                    <div class="sensor-eyebrow">
                        <span>{label}</span>
                        <span style="font-size:1.1rem;">{icon}</span>
                    </div>
                    <div>
                        <span class="sensor-value">{val}</span>
                        <span class="sensor-unit">{unit}</span>
                    </div>
                    <div style="margin:8px 0 2px 0;">{spark}</div>
                    <div><span class="sensor-status-pill {status_cls}">
                        ● {status_lbl}
                    </span></div>
                </div>
            """)


# ==================================================
# AI PREDICTION SECTION (Neural Network Prognostics)
# ==================================================

def render_ai_prediction_section(prediction: Dict[str, Any],
                                  reading: Dict[str, Any]):
    """Renders the 3-column AI prediction row (+ optional cleaning 4th card)."""
    fault   = prediction["fault"]
    rul     = float(prediction["rul_days"])
    anomaly = prediction["anomaly"]
    cleaning = prediction.get("cleaning")

    status  = fault["status"]
    conf    = fault["confidence"] * 100.0
    s_col   = STATUS_NORMAL if status == "Normal" else STATUS_DEGRADING if status == "Degrading" else STATUS_CLOGGED

    rul_pct = (min(max(rul, 0), 180) / 180) * 100
    rul_col = STATUS_NORMAL if rul > 40 else STATUS_DEGRADING if rul > 15 else STATUS_CLOGGED
    arc     = _arc_gauge_svg(rul_pct, rul_col)

    is_anom  = anomaly["detected"]
    anom_pct = anomaly["probability"] * 100.0
    anom_col = STATUS_CLOGGED if is_anom else STATUS_NORMAL
    anom_lbl = "Anomaly Detected!" if is_anom else "No Anomaly"

    num_cols = 4 if cleaning else 3
    cols = st.columns(num_cols)

    # Card 1 – Filter Health State
    with cols[0]:
        _render_html(f"""
            <div class="pred-card">
                <div class="pred-eyebrow">Filter Health State</div>
                <div class="pred-value" style="color:{s_col};">{status}</div>
                <div class="pred-sub">Confidence: {conf:.1f}%</div>
                <div class="conf-bar-bg">
                    <div style="background:{s_col};width:{conf:.1f}%;height:100%;border-radius:9999px;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;color:#64748b;margin-top:6px;">
                    <span>Norm: {fault['probabilities']['Normal']*100:.0f}%</span>
                    <span>Deg: {fault['probabilities']['Degrading']*100:.0f}%</span>
                    <span>Clog: {fault['probabilities']['Clogged']*100:.0f}%</span>
                </div>
            </div>
        """)

    # Card 2 – Remaining Useful Life (RUL)
    with cols[1]:
        _render_html(f"""
            <div class="pred-card">
                <div class="pred-eyebrow">Remaining Useful Life (RUL)</div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div class="pred-value" style="color:#FFFFFF;">
                            {rul:.0f}
                            <span style="font-size:1rem;font-weight:400;color:#94a3b8;">days</span>
                        </div>
                        <div class="pred-sub">Until filter replacement</div>
                    </div>
                    <div>{arc}</div>
                </div>
                <div style="font-size:0.72rem;color:#64748b;border-top:1px solid rgba(255,255,255,0.07);
                            padding-top:8px;margin-top:10px;">
                    Cycle remaining: <strong style="color:#FFFFFF;">{rul_pct:.0f}%</strong>
                </div>
            </div>
        """)

    # Card 3 – Anomaly Detection Probability
    with cols[2]:
        _render_html(f"""
            <div class="pred-card">
                <div class="pred-eyebrow">Anomaly Detection Probability</div>
                <div class="pred-value" style="color:{anom_col};">
                    {anom_pct:.1f}<span style="font-size:1rem;font-weight:400;color:#94a3b8;">%</span>
                </div>
                <div class="pred-sub">{anom_lbl}</div>
                <div style="font-size:0.72rem;color:#64748b;border-top:1px solid rgba(255,255,255,0.07);
                            padding-top:8px;margin-top:14px;">
                    MTNN Sigmoid Sentinel · Threshold 50%
                </div>
            </div>
        """)

    # Card 4 – Cleaning Verification (only if cleaning event active)
    if cleaning and len(cols) == 4:
        c_status = cleaning["status"]
        c_col    = STATUS_NORMAL if c_status == "Successful" else STATUS_DEGRADING if c_status == "Partial" else STATUS_CLOGGED
        c_conf   = cleaning["probabilities"].get(c_status, 1.0) * 100.0
        pre_p    = float(reading.get("pre_pressure", 0.0))
        post_p   = float(reading.get("post_pressure", 0.0))
        with cols[3]:
            _render_html(f"""
                <div class="pred-card">
                    <div class="pred-eyebrow">Cleaning Verification</div>
                    <div class="pred-value" style="color:{c_col};">{c_status}</div>
                    <div class="pred-sub">Recovery: {c_conf:.1f}%</div>
                    <div style="font-size:0.72rem;color:#64748b;border-top:1px solid rgba(255,255,255,0.07);
                                padding-top:8px;margin-top:14px;">
                        Pre ΔP: <strong>{pre_p:.2f}</strong> → Post ΔP: <strong>{post_p:.2f}</strong> bar
                    </div>
                </div>
            """)


# ==================================================
# MULTI-SENSOR TREND CHART
# ==================================================

def create_digital_trend_chart(history_df: pd.DataFrame,
                                view_metric: str = "All Sensors") -> go.Figure:
    fig = go.Figure()

    TRACES = [
        ("All Sensors", "Differential Pressure", "pressure",    "#38bdf8", "bar"),
        ("All Sensors", "Flow Rate",              "flow",        "#0066FF", "L/min"),
        ("All Sensors", "Turbidity",              "turbidity",   "#f59e0b", "NTU"),
        ("All Sensors", "Temperature",            "temperature", "#10b981", "°C"),
    ]

    for group, name, col, color, unit in TRACES:
        show = (view_metric == "All Sensors") or (view_metric == name)
        if show:
            fill = "tozeroy" if view_metric == name else "none"
            fig.add_trace(go.Scatter(
                x=history_df["step"],
                y=history_df[col],
                mode="lines",
                name=f"{name} ({unit})",
                line=dict(shape="spline", color=color, width=2.0),
                fill=fill,
                fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.07)"
            ))

    fig.update_layout(
        title=dict(text=f"Telemetry Chrono-Graph · {view_metric}",
                   font=dict(size=13, color="#FFFFFF")),
        xaxis=dict(title="Step", gridcolor="rgba(255,255,255,0.07)",
                   tickfont=dict(size=10, color="#94a3b8"), showline=False),
        yaxis=dict(title="Value", gridcolor="rgba(255,255,255,0.07)",
                   tickfont=dict(size=10, color="#94a3b8"), showline=False),
        plot_bgcolor="rgba(0,0,0,0.2)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=44, b=16),
        height=310,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11, color="#cbd5e1")),
        hovermode="x unified"
    )
    return fig


# ==================================================
# FILTER HEALTH CARDS (3-column)
# ==================================================

def render_filter_health_cards(simulator, predictor, sim_step: int):
    """Renders the three filter stage health cards."""
    cols = st.columns(3)
    for col, stage_key in zip(cols, ["sediment", "carbon", "ro"]):
        spec  = FILTER_SPECS[stage_key]
        s_rd  = simulator.get_automatic_reading(stage_key, sim_step)
        s_pr  = predictor.predict(s_rd)
        fault = s_pr["fault"]
        rul   = float(s_pr["rul_days"])
        rul_pct = (min(max(rul, 0), 180) / 180) * 100
        s_col = STATUS_NORMAL if fault["status"] == "Normal" else STATUS_DEGRADING if fault["status"] == "Degrading" else STATUS_CLOGGED

        with col:
            _render_html(f"""
                <div class="digital-glass-panel">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span style="font-size:0.68rem;font-weight:700;color:#94a3b8;
                                     text-transform:uppercase;letter-spacing:1.2px;">{spec['stage_num']}</span>
                        <span style="font-size:0.76rem;font-weight:700;color:{s_col};">● {fault['status']}</span>
                    </div>
                    <div style="font-size:1.15rem;font-weight:800;color:#FFFFFF;margin-bottom:3px;">{spec['name']}</div>
                    <div style="font-size:0.76rem;color:#94a3b8;margin-bottom:10px;">
                        {spec['pore']} · {spec['material']}
                    </div>
                    <div class="conf-bar-bg">
                        <div style="background:{s_col};width:{rul_pct:.0f}%;height:100%;border-radius:9999px;"></div>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.74rem;color:#94a3b8;
                                margin-top:8px;border-top:1px solid rgba(255,255,255,0.08);padding-top:8px;">
                        <span>RUL: <strong style="color:#FFFFFF;">~{rul:.0f}d</strong></span>
                        <span>Conf: <strong style="color:#FFFFFF;">{fault['confidence']*100:.0f}%</strong></span>
                    </div>
                </div>
            """)


# ==================================================
# ALERTS PANEL
# ==================================================

def render_alerts_panel(prediction: Dict[str, Any], reading: Dict[str, Any]):
    fault   = prediction["fault"]
    rul     = float(prediction["rul_days"])
    anomaly = prediction["anomaly"]
    p_diff  = float(reading.get("pressure_diff", 0.0))

    alerts = []
    if fault["status"] == "Clogged":
        alerts.append(("🔴", "danger", "Filter Clogging Detected",
                        f"ΔP elevated to {p_diff:.2f} bar. Schedule cartridge replacement immediately."))
    elif fault["status"] == "Degrading":
        alerts.append(("🟠", "warning", "Cartridge Degradation in Progress",
                        f"Pore fouling identified. Estimated {rul:.0f} days remaining."))
    if anomaly["detected"]:
        alerts.append(("⚡", "danger", "Sensor Anomaly Flagged",
                        f"Neural anomaly score: {anomaly['probability']*100:.1f}%. Check transducer probes."))
    if rul <= 15 and fault["status"] != "Clogged":
        alerts.append(("⏳", "warning", "Low RUL Warning",
                        f"RUL below 15 days (~{rul:.1f}d). Procure replacement cartridge."))
    if not alerts:
        alerts.append(("🟢", "optimal", "All Telemetry Channels Nominal",
                        "Operating parameters within baseline design criteria. MTNN prognostics clear."))

    for icon, kind, title, desc in alerts:
        if kind == "danger":
            accent = "#ef4444"; bg = "rgba(239,68,68,0.07)"
        elif kind == "warning":
            accent = "#f59e0b"; bg = "rgba(245,158,11,0.07)"
        else:
            accent = "#10b981"; bg = "rgba(16,185,129,0.07)"
        _render_html(f"""
            <div class="alert-item" style="background:{bg};border-left:3px solid {accent};">
                <div class="alert-title"><span>{icon}</span> {title}</div>
                <div class="alert-desc">{desc}</div>
            </div>
        """)


# ==================================================
# EXPLAINABLE AI (SHAP)
# ==================================================

def render_explainable_shap_panel(base_dir: Path):
    _render_html("""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    border-radius:14px;padding:14px 18px;margin-bottom:18px;">
            <div style="font-size:0.86rem;color:#38bdf8;font-weight:600;">
                🧠 SHAP helps explain how input sensor measurements influence
                the AI model's clogged-filter prediction.
            </div>
            <div style="font-size:0.78rem;color:#94a3b8;margin-top:6px;line-height:1.5;">
                Features with high positive SHAP values (rising differential pressure,
                dropping flow rate) accelerate the 'Clogged' transition,
                while stable baseline flow reinforces the 'Normal' classification.
            </div>
        </div>
    """)

    c1, c2 = st.columns(2)
    imp = base_dir / "reports" / "shap_feature_importance.png"
    smr = base_dir / "reports" / "shap_summary.png"
    with c1:
        st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#cbd5e1;"
                    "text-transform:uppercase;margin-bottom:6px;'>Feature Importance</div>",
                    unsafe_allow_html=True)
        if imp.exists():
            st.image(str(imp), width="stretch")
        else:
            st.info("shap_feature_importance.png not found in reports/")
    with c2:
        st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#cbd5e1;"
                    "text-transform:uppercase;margin-bottom:6px;'>SHAP Summary Plot</div>",
                    unsafe_allow_html=True)
        if smr.exists():
            st.image(str(smr), width="stretch")
        else:
            st.info("shap_summary.png not found in reports/")


# ==================================================
# SIDEBAR STATUS BOTTOM
# ==================================================

def render_sidebar_status_bottom():
    _render_html(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    border-radius:12px;padding:12px 14px;margin-top:16px;font-size:0.74rem;">
            <div style="font-weight:700;color:rgba(255,255,255,0.55);text-transform:uppercase;
                        letter-spacing:0.8px;margin-bottom:6px;">System Status</div>
            <div style="color:#94a3b8;line-height:1.65;">
                • System Link: <strong style="color:{STATUS_NORMAL};">ONLINE</strong><br>
                • Virtual IoT: <strong style="color:{STATUS_NORMAL};">CONNECTED (ESP32)</strong><br>
                • AI Model: <strong style="color:{STATUS_NORMAL};">ACTIVE (MTNN PyTorch)</strong>
            </div>
        </div>
    """, sidebar=True)


# ==================================================
# BACKWARD-COMPAT ALIAS (keep app.py import working)
# ==================================================

def render_digital_hero_banner(simulation_mode, selected_filter, running,
                                sim_step, operating_hours, purifier_id="AQG-PRO-2026-X1"):
    """Kept for backward compatibility – delegates to render_aquaguard_header."""
    pass  # Header is now rendered directly in app.py
