"""Standalone audio transcription application for IS_BACKOFFICE-style workflows.

This module is intentionally isolated: it only handles file validation, audio
transcription, and output generation. It never writes into knowledge hubs,
enterprise memory, mission managers, or AI Factory coordination layers.
"""

from audio_transcription.service import AudioTranscriptionService, TranscriptionJob, validate_audio_file
from audio_transcription.summary import generate_local_pm_summary, generate_pm_summary

__all__ = [
    "AudioTranscriptionService",
    "TranscriptionJob",
    "generate_local_pm_summary",
    "generate_pm_summary",
    "validate_audio_file",
]
