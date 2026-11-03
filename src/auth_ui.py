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
    """Renders the Login and Sign-Up portal matching the uploaded 'Let's Get Digital' theme."""
    init_db()

    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at 15% 5%, rgba(0, 102, 255, 0.45) 0%, transparent 45%),
                        radial-gradient(circle at 85% 15%, rgba(56, 189, 248, 0.3) 0%, transparent 40%),
                        linear-gradient(180deg, #0e1c36 0%, #070e1c 40%, #03060d 100%) !important;
            color: #FFFFFF !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif !important;
        }

        @keyframes floatLogo {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
            100% { transform: translateY(0px); }
        }

        @keyframes subtleGlow {
            0% { box-shadow: 0 0 0 0 rgba(0, 102, 255, 0.4); }
            70% { box-shadow: 0 0 0 16px rgba(0, 102, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 102, 255, 0); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Iconic Chamfered Frosted Glass Card */
        .digital-auth-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.14) 0%, rgba(255, 255, 255, 0.03) 100%);
            border-radius: 32px 75px 32px 32px;
            padding: 40px 36px;
            border: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.55), inset 0 1px 1px rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
            position: relative;
            overflow: hidden;
            margin-top: 1.5rem;
            margin-bottom: 2rem;
        }

        .auth-eyebrow {
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2.2px;
            color: rgba(255, 255, 255, 0.75);
            margin-bottom: 12px;
            text-align: center;
        }

        .auth-hero-title {
            text-align: center;
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -1px;
            color: #FFFFFF;
            line-height: 1.08;
            margin: 0 0 14px 0;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        }

        .auth-subhead {
            text-align: center;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: rgba(255, 255, 255, 0.85);
            margin-bottom: 20px;
        }

        .auth-badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #FFFFFF;
            padding: 5px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .demo-helper-box {
            background: rgba(0, 0, 0, 0.3);
            border: 1px dashed rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 12px 16px;
            margin-top: 14px;
            font-size: 0.82rem;
            color: #cbd5e1;
        }

        div.stButton > button {
            background: #0066FF !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.2px !important;
            box-shadow: 0 8px 24px rgba(0, 102, 255, 0.45) !important;
            transition: all 0.25s ease !important;
        }

        div.stButton > button:hover {
            background: #1a75ff !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(0, 102, 255, 0.65) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_l, col_center, col_r = st.columns([1, 1.45, 1])

    with col_center:
        st.markdown("""
            <div class="digital-auth-card">
                <div class="auth-eyebrow">CREATIVE AI LAB &bull; DIGITAL PORTAL</div>
                <h1 class="auth-hero-title">Let's get digital</h1>
                <div class="auth-subhead">AQUAGUARD AI WATER PURIFIER MONITORING & DIAGNOSTICS</div>
                <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-bottom: 24px;">
                    <span class="auth-badge-pill">Virtual IoT Stream</span>
                    <span class="auth-badge-pill">Multi-Task MTNN</span>
                    <span class="auth-badge-pill">Neural Sentinel</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Sign In", "Create Operator Profile"])

        with tab_login:
            st.caption("Authenticate with registered credentials to launch the digital monitoring cockpit.")

            with st.form("login_form", clear_on_submit=False):
                login_identifier = st.text_input(
                    "Username or Email",
                    placeholder="e.g. admin or operator@aquaguard.io",
                    key="login_user_input"
                )
                login_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter operator password",
                    key="login_pwd_input"
                )
                submit_login = st.form_submit_button("Launch Digital Cockpit", use_container_width=True)

            if submit_login:
                if not login_identifier or not login_password:
                    st.error("Please provide both username/email and password.")
                else:
                    success, user_info, msg = authenticate_user(login_identifier, login_password)
                    if success and user_info:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_info
                        st.success(f"Authenticated: {user_info.get('full_name') or user_info.get('username')}")
                        st.rerun()
                    else:
                        st.error(f"Authentication Failed: {msg}")

            with st.expander("Instant Evaluation Credentials"):
                st.markdown("""
                    <div class="demo-helper-box">
                        <strong>Pre-configured Demo Administrator:</strong><br>
                        • <strong>Username:</strong> <code>admin</code><br>
                        • <strong>Password:</strong> <code>Aquaguard@2026</code><br>
                        <small>Click below to authenticate instantly.</small>
                    </div>
                """, unsafe_allow_html=True)
                st.write("")
                if st.button("One-Click Demo Sign In", use_container_width=True):
                    success, user_info, msg = authenticate_user("admin", "Aquaguard@2026")
                    if success and user_info:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_info
                        st.rerun()

        with tab_signup:
            st.caption("Register a new operator profile in the AquaGuard SQLite database.")

            with st.form("signup_form", clear_on_submit=False):
                reg_name = st.text_input(
                    "Full Name",
                    placeholder="e.g. Dr. Alex Morgan",
                    key="signup_name"
                )
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    reg_username = st.text_input(
                        "Username",
                        placeholder="Letters, digits, _ (3-30 chars)",
                        key="signup_username"
                    )
                with col_u2:
                    reg_email = st.text_input(
                        "Email Address",
                        placeholder="operator@plant.io",
                        key="signup_email"
                    )

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    reg_pwd = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Min 6 characters",
                        key="signup_pwd"
                    )
                with col_p2:
                    reg_confirm = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Re-enter password",
                        key="signup_confirm"
                    )

                submit_signup = st.form_submit_button("Register & Save to Database", use_container_width=True)

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
                        st.success(f"{msg}")
                        st.info("Switch to the 'Sign In' tab to enter the dashboard.")
                    else:
                        st.error(f"{msg}")


def render_user_sidebar():
    """Renders the operator profile badge and logout button in the sidebar."""
    user = st.session_state.get("user", {})
    username = user.get("username", "Operator")
    full_name = user.get("full_name") or username
    role = user.get("role", "operator").capitalize()
    last_login = user.get("last_login", datetime.now().strftime("%Y-%m-%d %H:%M"))

    st.sidebar.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 14px; padding: 12px 14px; margin-bottom: 14px; backdrop-filter: blur(14px);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-weight: 700; font-size: 0.95rem; color: #FFFFFF;">{full_name}</span>
                <span style="background: #0066FF; color: #FFFFFF; padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase;">{role}</span>
            </div>
            <div style="font-size: 0.78rem; color: #94a3b8; margin-bottom: 6px;">@{username}</div>
            <div style="font-size: 0.72rem; color: #10b981; display: flex; align-items: center; gap: 5px;">
                <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:#10b981; box-shadow:0 0 6px #10b981;"></span> Telemetry Connected
            </div>
            <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px;">Last Login: {last_login}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Sign Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.session_state["running"] = False
        st.rerun()

    st.sidebar.divider()
