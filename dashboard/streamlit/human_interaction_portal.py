"""Human Interaction Environment portal for Ingercart users."""

from __future__ import annotations

from datetime import datetime
import json
import socket
from pathlib import Path
from urllib.parse import urlparse

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

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "collaborative_hub.json"


def _load_urls() -> tuple[str, str]:
    default_community = "https://teams.live.com/l/community/FEA5JSTpd_3FAKh9gI"
    default_teams = "https://teams.live.com/l/community/FEA5JSTpd_3FAKh9gI"
    if not CONFIG_PATH.exists():
        return default_community, default_teams

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        urls = data.get("urls", {})
        community_url = urls.get("teams_community") or urls.get("sharepoint") or default_community
        return community_url, urls.get("teams", default_teams)
    except (OSError, ValueError, TypeError):
        return default_community, default_teams


def _save_community_url(new_url: str) -> None:
    data: dict[str, object] = {}
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            data = {}

    urls = data.get("urls") if isinstance(data.get("urls"), dict) else {}
    urls["teams_community"] = new_url
    urls["teams"] = new_url
    data["urls"] = urls
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _validate_community_url(url: str) -> tuple[bool, str]:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return False, "URL invalida. Usa formato https://teams.live.com/l/community/<id>."
        socket.gethostbyname(parsed.netloc)
    except OSError:
        return False, "DNS no resuelve este dominio. Comprueba la URL de la comunidad de Teams."
    return True, "Dominio resolviendo correctamente."


COMMUNITY_URL, TEAMS_URL = _load_urls()
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

    st.subheader("Teams Community Connection")
    sp_col1, sp_col2 = st.columns([3, 1])
    with sp_col1:
        community_input = st.text_input(
            "Teams Community URL",
            value=COMMUNITY_URL,
            help="URL de la comunidad de Teams usada como espacio comun de archivos.",
        )
    with sp_col2:
        st.write("")
        st.write("")
        if st.button("Validate URL", use_container_width=True):
            valid, message = _validate_community_url(community_input)
            if valid:
                st.success(message)
            else:
                st.error(message)

    config_col1, config_col2 = st.columns([1, 2])
    with config_col1:
        if st.button("Save Community URL", use_container_width=True):
            _save_community_url(community_input)
            COMMUNITY_URL = community_input
            st.success("Teams Community URL saved in config/collaborative_hub.json")
    with config_col2:
        st.caption("Tip: usa la URL exacta de la comunidad de Teams (teams.live.com).")

    st.subheader("Quick Launch")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("Open Portal", APP_URL, use_container_width=True)
    with col2:
        st.link_button("Open Teams Community", COMMUNITY_URL, use_container_width=True)
    with col3:
        st.link_button("Open Dashboard", DASHBOARD_URL, use_container_width=True)

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
        st.button("Upload to Teams Community", use_container_width=True)
    with a3:
        st.button("Run agents", use_container_width=True)
    with a4:
        st.button("Send team notification", use_container_width=True)

    st.divider()
    st.subheader("System Links")
    st.write(f"Technical dashboard: {DASHBOARD_URL}")
    st.write(f"API endpoint: {API_URL}")
    st.write(f"Teams Community: {COMMUNITY_URL}")
    st.write(f"Teams URL: {TEAMS_URL}")

st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
