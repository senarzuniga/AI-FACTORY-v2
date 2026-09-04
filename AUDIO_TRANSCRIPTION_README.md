# AUDIO TRANSCRIPTION

## Objetivo

Aplicación aislada para cargar un archivo de audio y generar transcripción con timestamps en formato TXT, SRT, VTT y JSON. La aplicación no integra Knowledge Hub, Enterprise Memory, Mission Manager, Evidence Runtime ni ningún sistema de automatización adicional.

## Arquitectura

- `audio_transcription/engine.py`: motor de transcripción local con estrategia whisper-first.
- `audio_transcription/service.py`: validación, chunking, segmentación y generación de salidas.
- `api/routes/audio_transcription_api.py`: API HTTP para upload y transcripción.
- `dashboard/streamlit/audio_transcription_app.py`: interfaz Streamlit del usuario.
- `audio_transcription/uploads/`: archivos de entrada.
- `audio_transcription/processing/`: trabajo temporal.
- `audio_transcription/output/`: resultados generados.
- `audio_transcription/logs/`: trazas de ejecución.

## Formatos soportados

- MP3
- WAV
- M4A
- AAC
- FLAC
- OGG
- MP4 con audio

## Instalación

1. Crear entorno virtual.
2. Instalar requisitos del repositorio.
3. Confirmar que `ffmpeg` y `ffprobe` están disponibles en PATH.
4. Ejecutar la app desde Streamlit o usar la API de FastAPI.

## Dependencias

- Python 3.11+
- `fastapi`
- `streamlit`
- `ffmpeg` / `ffprobe` (si está disponible, se reutiliza)
- `openai-whisper` (opcional, si está instalada)

## Modelos disponibles

- `tiny`
- `base`
- `small`
- `medium`
- `large`

## Configuración

El servicio usa un directorio local para todos los artefactos generados:

```text
audio_transcription/
  uploads/
  processing/
  output/
  logs/
```

No se envía información a servicios externos ni se persiste en repositorios de conocimiento.

## Uso

### API

```bash
curl -X POST http://localhost:8000/api/audio-transcription/transcribe \
  -F "file=@sample.mp3" \
  -F "language=auto" \
  -F "model_name=tiny"
```

### Streamlit

```bash
streamlit run dashboard/streamlit/audio_transcription_app.py
```

## Procesamiento de archivos largos

El servicio prepara chunks por periodos de 1800 segundos por defecto para audios largos. La lógica conserva orden temporal y reconstruye el transcript en una salida final coherente. Para pruebas largas, se puede validar con un archivo de 2 horas.

## Cómo transcribir un audio de 2 horas

1. Subir el archivo de 2 horas en la interfaz.
2. Seleccionar `auto` o idioma manual.
3. Elegir un modelo adecuado (`base`, `small`, `medium` o `large`).
4. Pulsar `START TRANSCRIPTION`.
5. Esperar a que se generen los archivos `TXT`, `SRT`, `VTT` y `JSON`.
6. Descargar o abrir cada salida desde la vista de resultados.

## Ubicación de resultados

Los resultados se almacenan en `audio_transcription/output/<job_id>/`.

## Troubleshooting

- Si falta `ffmpeg`, la aplicación sigue funcionando con comprobaciones básicas, pero la calidad de metadatos dura- ción puede limitarse.
- Si el archivo no tiene extensión soportada, se rechaza antes de procesar.
- Si un bloque falla, la aplicación conserva la estructura del job y no destruye la transcripción parcial.
- Si no está instalado `whisper`, el servicio usa un fallback local determinista sin integrar otros sistemas.
