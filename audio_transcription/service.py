"""Service layer for the standalone audio transcription workflow."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from audio_transcription.engine import AudioTranscriptionEngine
from audio_transcription.summary import generate_pm_summary

SUPPORTED_FORMATS = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
    ".mp4": "video/mp4",
}

LANGUAGE_OPTIONS = ["auto", "es", "en", "fr", "it", "de", "pt", "other"]


def _human_size(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(size_bytes)
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024.0
        index += 1
    if index == 0:
        return f"{int(size)} {units[index]}"
    return f"{size:.2f} {units[index]}"


@dataclass
class TranscriptionJob:
    job_id: str
    audio_path: Path
    language: str = "auto"
    model: str = "small"
    duration: float | None = None
    segments: list[dict[str, Any]] = field(default_factory=list)
    status: str = "pending"
    errors: list[str] = field(default_factory=list)
    output_dir: Path | None = None
    engine: AudioTranscriptionEngine = field(default_factory=AudioTranscriptionEngine)

    def detect_language(self) -> str:
        return self.language if self.language != "auto" else "auto"

    def update_segment_timestamps(self) -> None:
        if not self.segments:
            return
        offset = 0.0
        for segment in self.segments:
            start = float(segment.get("start", offset))
            end = float(segment.get("end", start + 1.0))
            if end <= start:
                end = start + 1.0
            segment["start"] = start
            segment["end"] = end
            offset = end


@dataclass
class ProcessingChunk:
    chunk_index: int
    start: float
    end: float
    source_path: Path


def validate_audio_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return {"is_valid": False, "error_code": "missing_file", "message": "El archivo no existe."}
    if not path.is_file():
        return {"is_valid": False, "error_code": "not_a_file", "message": "La ruta no apunta a un archivo válido."}
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        return {"is_valid": False, "error_code": "unsupported_format", "message": f"Formato no soportado: {suffix or 'sin extensión'}"}
    try:
        if not path.stat().st_size:
            return {"is_valid": False, "error_code": "empty_file", "message": "El archivo está vacío."}
    except OSError:
        return {"is_valid": False, "error_code": "unreadable_file", "message": "No se puede leer el archivo."}

    try:
        path.read_bytes()[:1]
    except OSError:
        return {"is_valid": False, "error_code": "unreadable_file", "message": "No se puede leer el archivo."}

    return {
        "is_valid": True,
        "error_code": None,
        "message": "Archivo válido.",
        "name": path.name,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "size_human": _human_size(path.stat().st_size),
        "format": suffix.lstrip("."),
        "mime_type": SUPPORTED_FORMATS[suffix],
        "duration": None,
    }


class AudioTranscriptionService:
    def __init__(self, base_dir: str | Path | None = None, summary_client: Any | None = None) -> None:
        root = Path(base_dir) if base_dir else Path(__file__).resolve().parents[1]
        self.base_dir = root / "audio_transcription"
        self.upload_dir = self.base_dir / "uploads"
        self.processing_dir = self.base_dir / "processing"
        self.output_dir = self.base_dir / "output"
        self.logs_dir = self.base_dir / "logs"
        for directory in (self.upload_dir, self.processing_dir, self.output_dir, self.logs_dir):
            directory.mkdir(parents=True, exist_ok=True)
        self.engine = AudioTranscriptionEngine()
        self.summary_client = summary_client

    def create_job(self, audio_path: str | Path, language: str = "auto", model_name: str = "small") -> TranscriptionJob:
        path = Path(audio_path).expanduser().resolve()
        info = validate_audio_file(path)
        if not info["is_valid"]:
            raise ValueError(info["message"])
        job_id = f"job-{uuid4().hex[:8]}"
        duration = self.engine.detect_duration(path)
        job = TranscriptionJob(
            job_id=job_id,
            audio_path=path,
            language=language,
            model=model_name,
            duration=duration,
            output_dir=self.output_dir / job_id,
            engine=self.engine,
        )
        job.output_dir.mkdir(parents=True, exist_ok=True)
        return job

    def chunk_audio_for_processing(self, duration_seconds: float | int, chunk_seconds: int = 1800) -> list[dict[str, float | int]]:
        total = max(float(duration_seconds), 0.0)
        chunk = max(int(chunk_seconds), 1)
        if total <= 0:
            return []

        chunk_count = int(math.ceil(total / chunk))
        chunks: list[dict[str, float | int]] = []
        for index in range(chunk_count):
            start = index * chunk
            end = min(start + chunk, total)
            if end > start:
                chunks.append({"index": index, "start": float(start), "end": float(end)})

        return chunks

    def transcribe_job(self, job: TranscriptionJob) -> TranscriptionJob:
        job.status = "running"
        result = self.engine.transcribe(job.audio_path, language=job.language, model_name=job.model)
        job.duration = result.get("duration") or job.duration
        job.language = result.get("language") or job.language
        job.model = result.get("model") or job.model
        if not result.get("segments"):
            error = str(result.get("error") or "Whisper no emitió texto de transcripción.")
            job.errors.append(error)
            job.status = "failed"
            return job
        job.segments = [
            {
                "start": float(segment.get("start", 0.0)),
                "end": float(segment.get("end", 0.0)),
                "text": str(segment.get("text", "")).strip(),
            }
            for segment in result.get("segments", [])
        ]
        job.update_segment_timestamps()
        job.status = "completed"
        return job

    def _segment_to_srt(self, index: int, segment: dict[str, Any]) -> str:
        start = float(segment.get("start", 0.0))
        end = float(segment.get("end", start + 1.0))
        return (
            f"{index}\n"
            f"{self._format_timestamp(start)} --> {self._format_timestamp(end)}\n"
            f"{segment.get('text', '').strip()}\n\n"
        )

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        total_milliseconds = int(round(seconds * 1000.0))
        hours, remainder = divmod(total_milliseconds, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        secs, millis = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_vtt_timestamp(self, seconds: float) -> str:
        total_milliseconds = int(round(seconds * 1000.0))
        hours, remainder = divmod(total_milliseconds, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        secs, millis = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def persist_outputs(self, job: TranscriptionJob) -> dict[str, Path]:
        transcript_text = "\n\n".join(
            segment.get("text", "").strip()
            for segment in job.segments
            if segment.get("text", "").strip()
        )
        if not transcript_text:
            error = job.errors[-1] if job.errors else "La transcripción no contiene texto real."
            raise ValueError(error)

        job.output_dir.mkdir(parents=True, exist_ok=True)
        txt_path = job.output_dir / f"{job.audio_path.stem}_transcripcion.txt"
        summary_path = job.output_dir / f"{job.audio_path.stem}_resumen_pm.txt"
        srt_path = job.output_dir / f"{job.audio_path.stem}.srt"
        vtt_path = job.output_dir / f"{job.audio_path.stem}.vtt"
        json_path = job.output_dir / f"{job.audio_path.stem}.json"

        summary_text = generate_pm_summary(transcript_text, openai_client=self.summary_client)
        txt_path.write_text(transcript_text, encoding="utf-8")
        summary_path.write_text(summary_text, encoding="utf-8")

        srt_lines: list[str] = []
        for index, segment in enumerate(job.segments, start=1):
            srt_lines.append(self._segment_to_srt(index, segment))
        srt_path.write_text("".join(srt_lines), encoding="utf-8")

        vtt_lines = ["WEBVTT", "", *[
            f"{index}\n{self._format_vtt_timestamp(float(segment.get('start', 0.0)))} --> {self._format_vtt_timestamp(float(segment.get('end', 0.0)))}\n{segment.get('text', '').strip()}\n"
            for index, segment in enumerate(job.segments, start=1)
        ]]
        vtt_path.write_text("\n".join(vtt_lines), encoding="utf-8")

        json_payload = {
            "audio_file": str(job.audio_path),
            "duration": job.duration,
            "language": job.language,
            "model": job.model,
            "segments": job.segments,
            "start": min((float(segment.get("start", 0.0)) for segment in job.segments), default=0.0),
            "end": max((float(segment.get("end", 0.0)) for segment in job.segments), default=0.0),
            "text": transcript_text,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "txt": txt_path,
            "summary": summary_path,
            "srt": srt_path,
            "vtt": vtt_path,
            "json": json_path,
        }
