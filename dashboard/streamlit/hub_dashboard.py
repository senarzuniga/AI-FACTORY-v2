"""Technical dashboard for collaborative hub operations."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Collaborative Hub Dashboard",
    page_icon="CH",
    layout="wide",
)

st.title("Collaborative Hub Dashboard")
st.caption("Technical operations panel for AI-FACTORY-v2")

left, right = st.columns(2)

with left:
    st.subheader("Service Endpoints")
    st.write("API: http://localhost:8000")
    st.write("Health: http://localhost:8000/hub/status")
    st.write("Human Portal: http://localhost:8502")

with right:
    st.subheader("System Status")
    st.metric("Agents online", "8")
    st.metric("API status", "Online")
    st.metric("Last refresh", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

st.divider()
st.subheader("Runbook")
st.markdown(
    """
1. Start API using start-collaborative-hub.ps1.
2. Start this dashboard and the human portal.
3. Validate /hub/status before user traffic.
4. Publish approved outputs to SharePoint deliverables folder.
"""
)
