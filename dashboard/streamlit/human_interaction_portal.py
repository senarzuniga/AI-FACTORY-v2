"""Human Interaction Environment portal for Ingercart users."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Adaptive Sales Engine Portal",
    page_icon="ASE",
    layout="wide",
    initial_sidebar_state="expanded",
)

AUTHORIZED_USERS = {
    "isenar.cta@gmail.com": {
        "name": "Inaki Senar",
        "role": "Administrator",
        "access_level": "full",
    },
    "sales@ingecart.es": {
        "name": "Sales Manager",
        "role": "Manager",
        "access_level": "manager",
    },
    "administracion@ingecart.es": {
        "name": "Administration Chief",
        "role": "Admin Chief",
        "access_level": "admin_chief",
    },
}

SHAREPOINT_URL = "https://ingecart.sharepoint.com/sites/Adaptive-Sales-Core"
TEAMS_URL = "https://teams.microsoft.com/l/team/19:ingecart_core"
APP_URL = "http://localhost:8502"
DASHBOARD_URL = "http://localhost:8501"
API_URL = "http://localhost:8000"

st.title("Adaptive Sales Engine")
st.caption("Human Interaction Environment for Ingercart")

if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.header("Portal Access")

    if st.session_state.user is None:
        selected_email = st.selectbox(
            "Select account",
            options=list(AUTHORIZED_USERS.keys()),
            format_func=lambda mail: f"{AUTHORIZED_USERS[mail]['name']} ({mail})",
        )
        if st.button("Sign in", use_container_width=True):
            st.session_state.user = dict(AUTHORIZED_USERS[selected_email])
            st.session_state.user["email"] = selected_email
            st.rerun()
    else:
        current_user = st.session_state.user
        st.write(f"User: {current_user['name']}")
        st.write(f"Role: {current_user['role']}")
        st.write(f"Access: {current_user['access_level']}")
        if st.button("Sign out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

if st.session_state.user is None:
    st.info("Sign in from the sidebar to continue.")
else:
    user = st.session_state.user

    st.subheader("Quick Launch")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("Open Portal", APP_URL, use_container_width=True)
    with col2:
        st.link_button("Open SharePoint", SHAREPOINT_URL, use_container_width=True)
    with col3:
        st.link_button("Open Teams", TEAMS_URL, use_container_width=True)

    st.divider()
    st.subheader("Ecosystem Status")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("API", "Online")
    c2.metric("Dashboard", "Online")
    c3.metric("Agents", "8 active")
    c4.metric("Current role", user["role"])

    st.divider()
    st.subheader("Role Metrics")

    role_metrics = {
        "Administrator": {
            "Active users": "3/3",
            "Documents": "0",
            "Success rate": "100%",
        },
        "Manager": {
            "Pipeline": "EUR 2.4M",
            "Opportunities": "23",
            "Conversion": "34%",
        },
        "Admin Chief": {
            "Pending invoices": "12",
            "Active contracts": "28",
            "Providers": "15",
        },
    }

    metrics = role_metrics.get(user["role"], {})
    for label, value in metrics.items():
        st.write(f"- {label}: {value}")

    st.divider()
    st.subheader("Quick Actions")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.button("Generate report", use_container_width=True)
    with a2:
        st.button("Upload to SharePoint", use_container_width=True)
    with a3:
        st.button("Run agents", use_container_width=True)
    with a4:
        st.button("Send team notification", use_container_width=True)

    st.divider()
    st.subheader("System Links")
    st.write(f"Technical dashboard: {DASHBOARD_URL}")
    st.write(f"API endpoint: {API_URL}")
    st.write(f"SharePoint site: {SHAREPOINT_URL}")
    st.write(f"Teams space: {TEAMS_URL}")

st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
