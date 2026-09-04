from __future__ import annotations

import json
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

from audio_transcription.engine import AudioTranscriptionEngine
from audio_transcription.service import AudioTranscriptionService, TranscriptionJob, validate_audio_file
from audio_transcription.summary import REQUIRED_HEADINGS


@pytest.fixture
def service(tmp_path: Path) -> AudioTranscriptionService:
    return AudioTranscriptionService(base_dir=tmp_path)


def _write_audio(path: Path, content: bytes = b"RIFF....") -> None:
    path.write_bytes(content)


def test_validate_audio_file_accepts_supported_formats() -> None:
    file_path = Path("tmp-example.mp3")
    file_path.write_bytes(b"fake-mp3")
    try:
        info = validate_audio_file(file_path)
        assert info["is_valid"] is True
        assert info["format"] == "mp3"
    finally:
        file_path.unlink(missing_ok=True)


def test_validate_audio_file_rejects_missing_or_invalid_format(tmp_path: Path) -> None:
    missing = tmp_path / "missing.wav"
    invalid = tmp_path / "bad.txt"
    invalid.write_text("not audio", encoding="utf-8")

    missing_info = validate_audio_file(missing)
    assert missing_info["is_valid"] is False
    assert missing_info["error_code"] == "missing_file"

    invalid_info = validate_audio_file(invalid)
    assert invalid_info["is_valid"] is False
    assert invalid_info["error_code"] == "unsupported_format"


def test_audio_transcription_job_generates_real_transcript_and_pm_summary(
    service: AudioTranscriptionService,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"fake-wav")

    job = service.create_job(audio_path, language="es")
    assert isinstance(job, TranscriptionJob)
    assert job.audio_path.name == "sample.wav"
    assert job.model == "small"

    detected = job.detect_language()
    assert detected in {"auto", "es"}

    job.segments = [
        {"start": 0.0, "end": 1.0, "text": "hola mundo"},
        {"start": 1.0, "end": 2.0, "text": "Se acordó revisar el alcance."},
    ]
    job.language = "es"
    job.duration = 2.0

    outputs = service.persist_outputs(job)
    assert outputs["txt"].name == "sample_transcripcion.txt"
    assert outputs["summary"].name == "sample_resumen_pm.txt"
    assert all(path.exists() for path in outputs.values())
    assert sorted(path.name for path in job.output_dir.glob("*.txt")) == [
        "sample_resumen_pm.txt",
        "sample_transcripcion.txt",
    ]

    txt_text = outputs["txt"].read_text(encoding="utf-8")
    assert "hola mundo" in txt_text
    assert "segment 1" not in txt_text.casefold()

    summary_text = outputs["summary"].read_text(encoding="utf-8")
    assert summary_text.strip()
    assert all(heading in summary_text for heading in REQUIRED_HEADINGS)
    assert "Se acordó revisar el alcance." in summary_text

    json_payload = json.loads(outputs["json"].read_text(encoding="utf-8"))
    assert json_payload["language"] == "es"
    assert len(json_payload["segments"]) == 2


def test_service_split_long_audio_into_chunks(service: AudioTranscriptionService) -> None:
    chunks = service.chunk_audio_for_processing(duration_seconds=7200, chunk_seconds=1800)
    assert len(chunks) == 4
    assert chunks[0]["start"] == 0
    assert chunks[-1]["end"] == 7200
    assert all(chunk["end"] > chunk["start"] for chunk in chunks)
    assert service.chunk_audio_for_processing(duration_seconds=0, chunk_seconds=1800) == []


def test_service_preserves_concrete_engine_error(
    service: AudioTranscriptionService,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audio_path = tmp_path / "broken.wav"
    audio_path.write_bytes(b"fake-wav")

    job = service.create_job(audio_path, language="auto")
    engine_error = "Whisper no pudo decodificar el flujo de audio: datos corruptos"
    monkeypatch.setattr(
        service.engine,
        "transcribe",
        lambda *_args, **_kwargs: {
            "language": "auto",
            "duration": 1.0,
            "segments": [],
            "model": "small",
            "engine": "error",
            "error": engine_error,
        },
    )
    job = service.transcribe_job(job)

    assert job.status == "failed"
    assert job.errors == [engine_error]
    assert job.segments == []


def test_missing_whisper_returns_explicit_error_without_synthetic_text(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "sample.m4a"
    audio_path.write_bytes(b"fake-m4a")
    engine = AudioTranscriptionEngine()

    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "whisper":
            raise ImportError("whisper unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    result = engine.transcribe(audio_path, language="es")

    assert result["engine"] == "error"
    assert result["segments"] == []
    assert "openai-whisper" in result["error"]
    assert "whisper unavailable" in result["error"]
    assert "segment 1" not in json.dumps(result).casefold()


def test_engine_uses_deterministic_whisper_options_and_auto_language(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake-wav")
    captured: dict[str, object] = {}

    class FakeModel:
        def transcribe(self, path: str, **kwargs: object) -> dict[str, object]:
            captured["path"] = path
            captured.update(kwargs)
            return {
                "language": "es",
                "segments": [{"start": 0.0, "end": 1.5, "text": "Texto reconocido real."}],
            }

    fake_whisper = SimpleNamespace(load_model=lambda name: captured.setdefault("model", name) and FakeModel())
    monkeypatch.setitem(sys.modules, "whisper", fake_whisper)
    engine = AudioTranscriptionEngine()
    monkeypatch.setattr(engine, "detect_duration", lambda _path: 1.5)

    result = engine.transcribe(audio_path)

    assert result["engine"] == "whisper"
    assert result["model"] == "small"
    assert result["segments"][0]["text"] == "Texto reconocido real."
    assert captured["model"] == "small"
    assert captured["language"] is None
    assert captured["temperature"] == 0.0
    assert captured["word_timestamps"] is True
    assert captured["without_timestamps"] is False
    assert "segment 1" not in json.dumps(result).casefold()
