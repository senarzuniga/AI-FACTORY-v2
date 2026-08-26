from __future__ import annotations

from pathlib import Path

import streamlit as st

from audio_transcription.service import AudioTranscriptionService, validate_audio_file

st.set_page_config(
    page_title="Audio Transcription",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Audio Transcription")
st.caption("Transcripción local, aislada del resto del ecosistema")

service = AudioTranscriptionService(base_dir=Path(__file__).resolve().parents[2])

with st.sidebar:
    st.header("Audio Transcription")
    st.caption("Solo trascripción de audio")
    st.markdown("- MP3, WAV, M4A, AAC, FLAC, OGG, MP4 con audio")
    st.markdown("- Idioma: auto o manual")
    st.markdown("- Salidas: transcripción TXT, resumen PM TXT, SRT, VTT y JSON")

uploaded_file = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a", "aac", "flac", "ogg", "mp4"])

if uploaded_file is not None:
    temp_dir = service.upload_dir / "ui_uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / uploaded_file.name
    temp_path.write_bytes(uploaded_file.getvalue())

    validation = validate_audio_file(temp_path)
    if validation["is_valid"]:
        st.success(f"Archivo válido: {validation['name']} | {validation['size_human']}")
        st.write(f"Formato: {validation['format']}")
        st.write(f"Duración: {validation['duration'] if validation['duration'] else 'No disponible'}")
    else:
        st.error(validation["message"])
        st.stop()

    language = st.selectbox("Idioma", ["auto", "es", "en", "fr", "it", "de", "pt", "other"])
    model = st.selectbox("Modelo", ["tiny", "base", "small", "medium", "large"], index=2)

    if st.button("START TRANSCRIPTION", use_container_width=True):
        job = service.create_job(temp_path, language=language, model_name=model)
        with st.spinner("Processing audio..."):
            job = service.transcribe_job(job)
        if job.status == "failed":
            st.error("; ".join(job.errors) or "La transcripción ha fallado.")
            st.stop()
        outputs = service.persist_outputs(job)
        st.subheader("RESULT")
        st.write(f"Estado: {job.status}")
        st.write(f"Idioma detectado: {job.language}")
        st.write(f"Duración: {job.duration}")
        st.write(f"Segmentos: {len(job.segments)}")

        columns = st.columns(len(outputs))
        for col, key in zip(columns, outputs):
            path = outputs[key]
            col.download_button(
                label=f"Open {key.upper()}",
                data=path.read_bytes(),
                file_name=path.name,
                mime="text/plain" if key in {"txt", "summary"} else "application/json" if key == "json" else "text/vtt",
            )

        st.download_button(
            label="Download All",
            data=b"\n\n".join(path.read_bytes() for path in outputs.values()),
            file_name="audio_transcription_bundle.zip",
            mime="application/zip",
        )

        st.subheader("Transcripción")
        st.text_area("Texto", value="\n\n".join(seg.get("text", "") for seg in job.segments), height=220)
else:
    st.info("Cargue un archivo de audio para iniciar la transcripción.")
