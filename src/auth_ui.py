"""
Authentication UI module for AquaGuard.
Designed with the 'Let's Get Digital' frosted glass theme:
- Azure-to-obsidian gradient background.
- Iconic chamfered glass card with bold typography and electric blue #0066FF button.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional
from src.database import (
    authenticate_user,
    create_user,
    init_db
)


def render_auth_page():
    """Render AquaGuard's split-screen login and sign-up experience."""
    init_db()

    st.markdown("""
        <style>
        .stApp {
            background:
                radial-gradient(ellipse at 12% 20%, rgba(0,102,255,.32), transparent 42%),
                radial-gradient(ellipse at 88% 12%, rgba(56,189,248,.20), transparent 38%),
                linear-gradient(135deg,#06152d 0%,#07101f 55%,#020711 100%) !important;
            color:#f8fbff !important;
        }
        .stMainBlockContainer, section.main > div.block-container {
            max-width: 1480px !important;
            padding: 2.2rem 2.4rem 2rem !important;
        }
        .auth-left-panel {
            min-height: 690px;
            height: 100%;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(56,161,255,.55);
            border-radius: 28px;
            padding: 42px 42px 34px;
            background:
                radial-gradient(circle at 78% 42%,rgba(0,153,255,.30),transparent 36%),
                linear-gradient(145deg,rgba(3,37,82,.94),rgba(4,20,45,.96) 62%,rgba(2,12,29,.98));
            box-shadow: 0 24px 70px rgba(0,0,0,.36),inset 0 1px 0 rgba(255,255,255,.12);
        }
        .auth-brand {display:flex;align-items:center;gap:18px;margin-bottom:54px;}
        .auth-brand-mark {
            width:64px;height:72px;display:flex;align-items:center;justify-content:center;
            font-size:3.4rem;filter:drop-shadow(0 0 18px rgba(0,174,255,.85));
        }
        .auth-brand-name {
            font-size:2.65rem;font-weight:850;letter-spacing:-1.4px;line-height:1;
            color:#fff;text-shadow:0 5px 22px rgba(0,0,0,.3);
        }
        .auth-brand-sub {
            margin-top:9px;color:#b9d9ff;font-size:.82rem;font-weight:750;
            letter-spacing:5px;text-transform:uppercase;
        }
        .auth-kicker {
            color:#78c9ff;font-size:.76rem;font-weight:800;letter-spacing:2.3px;
            text-transform:uppercase;margin-bottom:14px;
        }
        .auth-left-title {
            color:#fff;font-size:clamp(2.4rem,4vw,3.5rem);font-weight:850;
            line-height:1.06;letter-spacing:-1.8px;margin:0 0 18px;
        }
        .auth-left-title span {color:#36c8ff;}
        .auth-left-copy {
            max-width:520px;color:#c5d7ed;font-size:1.02rem;line-height:1.7;
            margin-bottom:30px;
        }
        .auth-feature {
            display:flex;align-items:center;gap:15px;margin:19px 0;
            position:relative;z-index:2;
        }
        .auth-feature-icon {
            width:46px;height:46px;flex:0 0 46px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;font-size:1.25rem;
            background:linear-gradient(145deg,rgba(0,137,255,.42),rgba(30,210,255,.12));
            border:1px solid rgba(87,190,255,.4);box-shadow:0 6px 20px rgba(0,110,255,.18);
        }
        .auth-feature-title {font-weight:750;color:#f4f8ff;font-size:.95rem;}
        .auth-feature-copy {color:#a9c0dc;font-size:.79rem;margin-top:3px;}
        .auth-purifier-art {
            position:absolute;right:25px;top:220px;width:220px;height:350px;
            opacity:.88;pointer-events:none;filter:drop-shadow(0 18px 35px rgba(0,140,255,.3));
        }
        .auth-purifier-body {
            position:absolute;left:43px;top:25px;width:135px;height:275px;border-radius:27px 27px 20px 20px;
            background:linear-gradient(100deg,#c6eaff 0%,#f7fbff 18%,#5e9bc9 38%,#102b4d 54%,#e4f5ff 78%,#7bb7e8 100%);
            border:2px solid rgba(255,255,255,.7);box-shadow:inset 0 0 18px rgba(255,255,255,.7),0 20px 35px rgba(0,0,0,.45);
        }
        .auth-purifier-screen {
            position:absolute;left:61px;top:48px;width:99px;height:92px;border-radius:12px;
            background:linear-gradient(145deg,#06172d,#0b3c70);border:1px solid #6bd6ff;
            box-shadow:0 0 20px rgba(0,177,255,.6);display:flex;align-items:center;justify-content:center;
            color:#36d8ff;font-size:2rem;
        }
        .auth-purifier-spout {
            position:absolute;left:88px;top:157px;width:48px;height:55px;border-radius:0 0 13px 13px;
            border:5px solid #d9efff;border-top:0;background:linear-gradient(90deg,#173b5c,#8bd3ff,#173b5c);
        }
        .auth-purifier-base {
            position:absolute;left:27px;top:296px;width:166px;height:18px;border-radius:50%;
            background:radial-gradient(ellipse,rgba(39,210,255,.85),rgba(0,95,255,.05) 68%);
            box-shadow:0 0 30px rgba(0,175,255,.7);
        }
        .auth-orbit {
            position:absolute;left:0;top:115px;width:220px;height:190px;border:2px solid rgba(44,197,255,.38);
            border-radius:50%;transform:rotate(-23deg);box-shadow:0 0 24px rgba(0,155,255,.18);
        }
        .auth-bottom-note {
            position:absolute;left:42px;right:42px;bottom:28px;padding:14px 18px;
            border-radius:13px;border:1px solid rgba(76,175,255,.28);
            background:rgba(0,112,210,.12);color:#8edfff;font-style:italic;font-weight:700;
        }
        .auth-right-panel {
            min-height:690px;height:100%;padding:40px 34px 30px;
            border:1px solid rgba(112,184,255,.34);border-radius:28px;
            background:linear-gradient(145deg,rgba(255,255,255,.105),rgba(255,255,255,.035));
            box-shadow:0 24px 70px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.14);
            backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
        }
        .auth-right-eyebrow {
            text-align:center;color:#9bcfff;font-size:.72rem;font-weight:800;
            letter-spacing:2.5px;text-transform:uppercase;margin:8px 0 12px;
        }
        .auth-right-title {
            text-align:center;color:#fff;font-size:2rem;font-weight:820;
            letter-spacing:-.7px;margin:0 0 10px;
        }
        .auth-right-copy {
            text-align:center;color:#b4c7df;font-size:.86rem;margin-bottom:24px;
        }
        div[data-testid="stRadio"] > label {display:none !important;}
        div[data-testid="stRadio"] div[role="radiogroup"] {
            display:flex !important;gap:0 !important;padding:5px !important;
            border-radius:999px !important;background:rgba(3,17,39,.78) !important;
            border:1px solid rgba(111,178,255,.3) !important;
            margin:0 auto 28px !important;width:100% !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            flex:1 !important;justify-content:center !important;text-align:center !important;
            border-radius:999px !important;padding:10px 12px !important;
            color:#c7d8ee !important;font-weight:750 !important;
            border:0 !important;background:transparent !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            color:#fff !important;background:linear-gradient(100deg,#0877ff,#00a8ff) !important;
            box-shadow:0 5px 18px rgba(0,119,255,.35) !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {display:none !important;}
        .auth-right-panel label {color:#e8f2ff !important;font-weight:650 !important;}
        .auth-right-panel input {
            background:rgba(3,18,42,.72) !important;border:1px solid rgba(105,171,245,.32) !important;
            border-radius:11px !important;color:#fff !important;
        }
        .auth-right-panel input:focus {border-color:#159cff !important;box-shadow:0 0 0 2px rgba(21,156,255,.14) !important;}
        .auth-right-panel button[kind="primaryFormSubmit"],
        .auth-right-panel button[kind="primary"] {
            background:linear-gradient(100deg,#0877ff,#009dff) !important;
            color:#fff !important;border:0 !important;border-radius:11px !important;
            min-height:48px !important;font-weight:800 !important;
            box-shadow:0 9px 24px rgba(0,112,255,.28) !important;
        }
        .auth-right-panel div[data-testid="stForm"] {
            border:0 !important;padding:0 !important;background:transparent !important;
        }
        .auth-demo-note {
            color:#a9c2df;font-size:.78rem;line-height:1.5;
            padding:12px 14px;border:1px dashed rgba(125,185,255,.28);
            border-radius:11px;background:rgba(0,12,30,.28);
        }
        @media(max-width:1050px) {
            .auth-left-panel,.auth-right-panel {min-height:auto;}
            .auth-purifier-art {opacity:.24;right:0;top:190px;}
            .auth-bottom-note {position:relative;left:auto;right:auto;bottom:auto;margin-top:28px;}
            .auth-left-panel {padding:30px 26px;}
            .auth-right-panel {padding:30px 24px;}
        }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1.12, 0.88], gap="large", vertical_alignment="center")

    with left_col:
        st.markdown("""
            <div class="auth-left-panel">
                <div class="auth-brand">
                    <div class="auth-brand-mark">💧</div>
                    <div>
                        <div class="auth-brand-name">AquaGuard</div>
                        <div class="auth-brand-sub">Digital AI Studio</div>
                    </div>
                </div>
                <div class="auth-kicker">Intelligent water purifier diagnostics</div>
                <h1 class="auth-left-title">Smart Monitoring.<br>Healthier <span>Water.</span></h1>
                <div class="auth-left-copy">
                    AI-powered filter failure prediction and predictive maintenance
                    for domestic water purifiers.
                </div>
                <div class="auth-feature">
                    <div class="auth-feature-icon">⌁</div>
                    <div><div class="auth-feature-title">Real-time Monitoring</div>
                    <div class="auth-feature-copy">Track filter health with live sensor data</div></div>
                </div>
                <div class="auth-feature">
                    <div class="auth-feature-icon">◈</div>
                    <div><div class="auth-feature-title">Predictive Analytics</div>
                    <div class="auth-feature-copy">Know when maintenance may be needed</div></div>
                </div>
                <div class="auth-feature">
                    <div class="auth-feature-icon">✓</div>
                    <div><div class="auth-feature-title">Explainable AI</div>
                    <div class="auth-feature-copy">Understand the reasons behind predictions</div></div>
                </div>
                <div class="auth-feature">
                    <div class="auth-feature-icon">💧</div>
                    <div><div class="auth-feature-title">Cleaner &amp; Healthier Water</div>
                    <div class="auth-feature-copy">Support informed purifier maintenance</div></div>
                </div>
                <div class="auth-purifier-art">
                    <div class="auth-orbit"></div><div class="auth-purifier-body"></div>
                    <div class="auth-purifier-screen">💧</div><div class="auth-purifier-spout"></div>
                    <div class="auth-purifier-base"></div>
                </div>
                <div class="auth-bottom-note">✦ &nbsp; Intelligent care for every drop.</div>
            </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
            <div class="auth-right-panel">
                <div class="auth-right-eyebrow">Welcome to AquaGuard</div>
                <div class="auth-right-title">Access Your Dashboard</div>
                <div class="auth-right-copy">Sign in to continue or create a new operator account.</div>
            </div>
        """, unsafe_allow_html=True)

        auth_mode = st.radio(
            "Account access",
            ["Login", "Sign Up"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode_toggle"
        )

        # Form controls sit in the same right-side glass panel area.
        st.markdown('<div class="auth-right-panel" style="min-height:0;margin-top:-1.1rem;padding-top:0;border-top:0;border-radius:0 0 28px 28px;">', unsafe_allow_html=True)

        if auth_mode == "Login":
            with st.form("login_form", clear_on_submit=False):
                login_identifier = st.text_input(
                    "Username or Email",
                    placeholder="Enter your username or email",
                    key="login_user_input"
                )
                login_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_pwd_input"
                )
                submit_login = st.form_submit_button("Sign In", use_container_width=True)

            if submit_login:
                if not login_identifier or not login_password:
                    st.error("Please provide both username/email and password.")
                else:
                    success, user_info, msg = authenticate_user(login_identifier, login_password)
                    if success and user_info:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_info
                        st.success("Welcome to AquaGuard.")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {msg}")

            with st.expander("Demo access"):
                st.markdown("""
                    <div class="auth-demo-note">
                        <strong>Demo administrator credentials</strong><br>
                        Username: <code>admin</code><br>
                        Password: <code>Aquaguard@2026</code>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Use demo account", use_container_width=True):
                    success, user_info, msg = authenticate_user("admin", "Aquaguard@2026")
                    if success and user_info:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_info
                        st.rerun()
                    else:
                        st.error(msg)

        else:
            with st.form("signup_form", clear_on_submit=False):
                reg_name = st.text_input(
                    "Full Name",
                    placeholder="Your full name",
                    key="signup_name"
                )
                reg_username = st.text_input(
                    "Username",
                    placeholder="Choose a username (3–30 characters)",
                    key="signup_username"
                )
                reg_email = st.text_input(
                    "Email Address",
                    placeholder="you@example.com",
                    key="signup_email"
                )
                reg_pwd = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a password (minimum 6 characters)",
                    key="signup_pwd"
                )
                reg_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="signup_confirm"
                )
                submit_signup = st.form_submit_button("Create Account", use_container_width=True)

            if submit_signup:
                if not reg_username or not reg_email or not reg_pwd:
                    st.error("Please fill in all mandatory fields.")
                elif reg_pwd != reg_confirm:
                    st.error("Passwords do not match.")
                else:
                    success, msg = create_user(
                        username=reg_username,
                        email=reg_email,
                        password=reg_pwd,
                        full_name=reg_name,
                        role="operator"
                    )
                    if success:
                        st.success("Account created successfully. Switch to Login to continue.")
                        st.session_state["auth_mode_toggle"] = "Login"
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)

def render_user_sidebar(in_sidebar=False):
    """Render the signed-in operator panel in the page's top-right corner."""
    user = st.session_state.get("user", {})
    username = user.get("username", "Operator")
    full_name = user.get("full_name") or username
    role = user.get("role", "operator").capitalize()
    last_login = user.get("last_login", datetime.now().strftime("%Y-%m-%d %H:%M"))

    if in_sidebar:
        target = st.sidebar
        target.markdown(f"""
            <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.18);
                        border-radius:14px;padding:10px 12px;margin:6px 0;backdrop-filter:blur(14px);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="font-weight:700;font-size:0.9rem;color:#fff;">{full_name}</span>
                    <span style="background:#0066FF;color:#fff;padding:2px 8px;border-radius:999px;
                                 font-size:0.65rem;font-weight:700;text-transform:uppercase;">{role}</span>
                </div>
                <div style="font-size:0.75rem;color:#94a3b8;">@{username}</div>
                <div style="font-size:0.68rem;color:#64748b;margin-top:4px;">Last Login: {last_login}</div>
            </div>
        """, unsafe_allow_html=True)
        if target.button("Sign Out", use_container_width=True, key="sidebar_sign_out"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["running"] = False
            st.rerun()
        return

    spacer, operator_col = st.columns([5.2, 2.1], vertical_alignment="center")
    with operator_col:
        st.markdown(f"""
            <div style="background:rgba(12,28,52,0.78);border:1px solid rgba(125,180,255,0.24);
                        border-radius:14px;padding:9px 12px 7px 12px;margin:0 0 5px 0;
                        backdrop-filter:blur(16px);">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
                    <span style="font-weight:750;font-size:0.88rem;color:#fff;">{full_name}</span>
                    <span style="background:#0066FF;color:#fff;padding:2px 8px;border-radius:999px;
                                 font-size:0.62rem;font-weight:700;text-transform:uppercase;">{role}</span>
                </div>
                <div style="font-size:0.72rem;color:#94a3b8;margin-top:3px;">
                    @{username} <span style="color:#64748b;">· Last login: {last_login}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="top_operator_sign_out"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["running"] = False
            st.rerun()
