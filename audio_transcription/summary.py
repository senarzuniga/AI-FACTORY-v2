"""Professional PM summaries grounded only in recognized transcript text."""

from __future__ import annotations

import logging
import os
import re
from typing import Any

LOGGER = logging.getLogger(__name__)

NOT_IDENTIFIED = "No identificado en la conversación"
REQUIRED_HEADINGS = (
    "RESUMEN EJECUTIVO",
    "CAPÍTULOS / TEMAS",
    "PUNTOS CLAVE",
    "ANÁLISIS GENERAL",
    "DECISIONES",
    "PLAN DE ACCIÓN",
    "RIESGOS Y BLOQUEOS",
    "PRÓXIMOS PASOS",
)

SYSTEM_PROMPT = """\
Eres un project manager senior. Genera un resumen profesional en español usando
EXCLUSIVAMENTE hechos presentes en la transcripción. No inventes, completes ni
deduzcas responsables, fechas, decisiones, compromisos, riesgos o estados.
Cuando un dato no conste, escribe exactamente: "No identificado en la conversación".

Usa exactamente estos encabezados, en este orden:
RESUMEN EJECUTIVO
CAPÍTULOS / TEMAS
PUNTOS CLAVE
ANÁLISIS GENERAL
DECISIONES
PLAN DE ACCIÓN
RIESGOS Y BLOQUEOS
PRÓXIMOS PASOS

En PLAN DE ACCIÓN, cada elemento debe incluir Acción, Responsable, Fecha y Estado.
Devuelve solo el resumen, sin preámbulos ni bloques Markdown.
"""


def _sentences(transcript: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", transcript.strip())
        if sentence.strip()
    ]


def _bullet_lines(items: list[str]) -> str:
    if not items:
        return f"- {NOT_IDENTIFIED}"
    return "\n".join(f"- {item}" for item in items)


def _matching_sentences(sentences: list[str], keywords: tuple[str, ...], limit: int = 5) -> list[str]:
    matches = []
    for sentence in sentences:
        normalized = sentence.casefold()
        if any(keyword in normalized for keyword in keywords):
            matches.append(sentence)
        if len(matches) == limit:
            break
    return matches


def generate_local_pm_summary(transcript: str) -> str:
    """Build an extractive summary without introducing facts absent from the transcript."""

    sentences = _sentences(transcript)
    if not sentences:
        raise ValueError("No se puede generar un resumen sin texto de transcripción.")

    decisions = _matching_sentences(
        sentences,
        ("decid", "acord", "aprob", "se opt", "resolved", "agreed", "approved"),
    )
    actions = _matching_sentences(
        sentences,
        (
            "hay que",
            "debe",
            "deberá",
            "vamos a",
            "acción",
            "tarea",
            "pendiente",
            "próximo paso",
            "will ",
            "must ",
            "action",
            "todo",
        ),
    )
    risks = _matching_sentences(
        sentences,
        ("riesgo", "bloque", "imped", "problema", "dependen", "retras", "risk", "block", "issue"),
    )
    executive = " ".join(sentences[:3])
    topics = [f"Tema {index}: {sentence}" for index, sentence in enumerate(sentences[:5], start=1)]
    key_points = sentences[:7]
    analysis = " ".join(sentences[:5])

    if actions:
        action_plan = "\n\n".join(
            (
                f"- Acción: {action}\n"
                f"  Responsable: {NOT_IDENTIFIED}\n"
                f"  Fecha: {NOT_IDENTIFIED}\n"
                f"  Estado: {NOT_IDENTIFIED}"
            )
            for action in actions
        )
    else:
        action_plan = (
            f"- Acción: {NOT_IDENTIFIED}\n"
            f"  Responsable: {NOT_IDENTIFIED}\n"
            f"  Fecha: {NOT_IDENTIFIED}\n"
            f"  Estado: {NOT_IDENTIFIED}"
        )

    return "\n\n".join(
        (
            f"RESUMEN EJECUTIVO\n{executive}",
            f"CAPÍTULOS / TEMAS\n{_bullet_lines(topics)}",
            f"PUNTOS CLAVE\n{_bullet_lines(key_points)}",
            f"ANÁLISIS GENERAL\n{analysis}",
            f"DECISIONES\n{_bullet_lines(decisions)}",
            f"PLAN DE ACCIÓN\n{action_plan}",
            f"RIESGOS Y BLOQUEOS\n{_bullet_lines(risks)}",
            f"PRÓXIMOS PASOS\n{_bullet_lines(actions)}",
        )
    )


def _is_structured_summary(summary: str) -> bool:
    return bool(summary.strip()) and all(heading in summary for heading in REQUIRED_HEADINGS)


def generate_pm_summary(transcript: str, openai_client: Any | None = None) -> str:
    """Prefer OpenAI when configured, otherwise use the grounded local extractor."""

    if not transcript.strip():
        raise ValueError("No se puede generar un resumen sin texto de transcripción.")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key and openai_client is None:
        return generate_local_pm_summary(transcript)

    try:
        from openai import OpenAI, OpenAIError
    except ImportError as exc:
        raise RuntimeError(
            "OPENAI_API_KEY está configurada, pero el SDK 'openai' no está instalado."
        ) from exc

    if openai_client is None:
        openai_client = OpenAI(api_key=api_key)

    try:
        response = openai_client.chat.completions.create(
            model=os.getenv("AUDIO_TRANSCRIPTION_SUMMARY_MODEL", "gpt-4o-mini"),
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"TRANSCRIPCIÓN:\n{transcript}"},
            ],
        )
        summary = str(response.choices[0].message.content or "").strip()
    except OpenAIError as exc:
        LOGGER.warning("OpenAI no pudo generar el resumen; se usa extracción local: %s", exc)
        return generate_local_pm_summary(transcript)

    if not _is_structured_summary(summary):
        LOGGER.warning("OpenAI devolvió un resumen incompleto; se usa extracción local.")
        return generate_local_pm_summary(transcript)
    return summary
