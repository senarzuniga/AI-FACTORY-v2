"""Transcription engine abstraction for local audio processing."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


class AudioTranscriptionEngine:
    """Local transcription engine backed exclusively by Whisper recognition."""

    def __init__(self) -> None:
        self.ffmpeg_path = shutil.which("ffmpeg")
        self.ffprobe_path = shutil.which("ffprobe")
        self.models = ["tiny", "base", "small", "medium", "large"]

    @property
    def ffmpeg_available(self) -> bool:
        return bool(self.ffmpeg_path)

    @property
    def ffprobe_available(self) -> bool:
        return bool(self.ffprobe_path)

    def detect_duration(self, file_path: Path) -> float | None:
        if not self.ffprobe_available:
            return None
        command = [
            self.ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nokey=1:noprint_wrappers=1",
            str(file_path),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            if result.returncode != 0 or not result.stdout.strip():
                return None
            duration = float(result.stdout.strip())
            return max(duration, 0.0)
        except (OSError, ValueError):
            return None

    def transcribe(self, file_path: Path, language: str = "auto", model_name: str = "small") -> dict[str, Any]:
        duration = self.detect_duration(file_path) or self._estimate_duration(file_path)
        try:
            import whisper  # type: ignore
        except ImportError as exc:
            return {
                "language": language,
                "duration": duration,
                "segments": [],
                "model": model_name,
                "engine": "error",
                "error": (
                    "Whisper no está disponible. Instale la dependencia "
                    f"'openai-whisper' para transcribir audio. Detalle: {exc}"
                ),
            }

        try:
            model = whisper.load_model(model_name)
            result = model.transcribe(
                str(file_path),
                language=None if language == "auto" else language,
                task="transcribe",
                temperature=0.0,
                beam_size=5,
                condition_on_previous_text=True,
                word_timestamps=True,
                without_timestamps=False,
                no_speech_threshold=0.6,
                logprob_threshold=-1.0,
                compression_ratio_threshold=2.4,
                fp16=False,
                verbose=False,
            )
            segments = [
                {
                    "start": float(item.get("start", 0.0)),
                    "end": float(item.get("end", 0.0)),
                    "text": str(item.get("text", "")).strip(),
                }
                for item in result.get("segments", [])
                if str(item.get("text", "")).strip()
            ]
            if not segments:
                return {
                    "language": result.get("language") or language,
                    "duration": duration,
                    "segments": [],
                    "model": model_name,
                    "engine": "error",
                    "error": (
                        "Whisper finalizó sin texto reconocible. Compruebe que el archivo "
                        "contiene audio audible y que el formato es válido."
                    ),
                }
            return {
                "language": result.get("language") or language,
                "duration": duration,
                "segments": segments,
                "model": model_name,
                "engine": "whisper",
            }
        except Exception as exc:
            return {
                "language": language,
                "duration": duration,
                "segments": [],
                "model": model_name,
                "engine": "error",
                "error": f"Whisper no pudo transcribir '{file_path.name}': {exc}",
            }

    def _estimate_duration(self, file_path: Path) -> float:
        try:
            size = file_path.stat().st_size
        except OSError:
            return 0.0
        if size <= 0:
            return 0.0
        bitrate_kbps = 128
        return max(size / (bitrate_kbps * 1000 / 8), 0.0)
