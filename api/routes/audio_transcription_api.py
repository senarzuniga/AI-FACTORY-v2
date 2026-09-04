"""HTTP routes for the isolated audio transcription app."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from audio_transcription.service import AudioTranscriptionService, validate_audio_file

router = APIRouter(prefix="/api/audio-transcription", tags=["audio-transcription"])
SERVICE = AudioTranscriptionService()


@router.get("/status")
def status() -> dict[str, object]:
    return {
        "status": "ready",
        "supported_formats": ["mp3", "wav", "m4a", "aac", "flac", "ogg", "mp4"],
        "storage_root": str(SERVICE.base_dir),
    }


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    model_name: str = Form("small"),
) -> dict[str, object]:
    if file.filename is None or not file.filename.strip():
        raise HTTPException(status_code=400, detail="No se recibió un nombre de archivo válido.")

    file_path = SERVICE.upload_dir / Path(file.filename).name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    file_path.write_bytes(content)

    validation = validate_audio_file(file_path)
    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail=validation["message"])

    job = SERVICE.create_job(file_path, language=language, model_name=model_name)
    job = SERVICE.transcribe_job(job)
    if job.status == "failed":
        raise HTTPException(status_code=500, detail="; ".join(job.errors) or "La transcripción ha fallado.")

    outputs = SERVICE.persist_outputs(job)
    return {
        "job_id": job.job_id,
        "status": job.status,
        "audio_file": str(job.audio_path),
        "duration": job.duration,
        "language": job.language,
        "model": job.model,
        "segments": job.segments,
        "output_files": {key: str(path) for key, path in outputs.items()},
    }


@router.get("/job/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    for job_dir in SERVICE.output_dir.iterdir():
        if job_dir.is_dir() and job_dir.name.startswith(f"job-{job_id}"):
            return {"job_id": job_id, "status": "ready", "output_dir": str(job_dir)}
    return {"job_id": job_id, "status": "unknown"}
