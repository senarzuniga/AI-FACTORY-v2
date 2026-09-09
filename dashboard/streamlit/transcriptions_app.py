"""Simple transcription intake panel for AI-FACTORY-v2 collaborative hub."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Transcripciones",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_ROOT = Path(__file__).resolve().parents[2]

st.title("Transcripciones")
st.caption("Panel de entrada para transcripción y resumen operativo")

with st.sidebar:
    st.header("Acciones")
    st.button("Iniciar nueva transcripción", use_container_width=True)
    st.button("Cargar archivo", use_container_width=True)
    st.button("Exportar resumen", use_container_width=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Entrada")
    source = st.radio("Origen", ["Texto manual", "Archivo de audio", "Grabación en directo"], horizontal=True)
    if source == "Texto manual":
        transcript = st.text_area(
            "Pega la transcripción o la nota de reunión",
            height=240,
            value=(
                "Reunión de seguimiento\n"
                "- Objetivo: confirmar entregables del sprint\n"
                "- Decisión: priorizar integración del panel de transcripciones\n"
                "- Siguiente paso: validar accesos y cronograma\n"
            ),
        )
    else:
        st.file_uploader("Sube el archivo de audio o vídeo", type=["mp3", "wav", "mp4", "m4a", "webm"])
        transcript = st.text_area("Texto disponible", height=180, value="Se espera carga del contenido multimedia.")

with col2:
    st.subheader("Estado")
    st.metric("Estado", "Disponible")
    st.metric("Archivo", "Sin carga")
    st.metric("Última revisión", "No ejecutada")
    st.write(f"Ruta del repositorio: {APP_ROOT}")

st.divider()

st.subheader("Resumen automático")
summary_tab, actions_tab = st.tabs(["Resumen", "Acciones"])

with summary_tab:
    st.markdown(
        """
        ### Resultado sugerido
        - Confirmar alcance del caso de negocio.
        - Identificar acuerdos, riesgos y fechas pendientes.
        - Generar un resumen con decisiones operativas y responsables.
        """
    )
    st.code(transcript[:1200] if transcript else "Sin contenido disponible.")

with actions_tab:
    st.write("1. Validar diversidad de voces o texto.")
    st.write("2. Extraer decisiones clave y responsables.")
    st.write("3. Preparar entregable final para el flujo operativo.")
    st.write("4. Enlazar con el panel general del ecosistema.")
