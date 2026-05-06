"""
GENERATION AGENT
Crea informes, propuestas y presentaciones.
Se pueden tener multiples instancias para doble generacion.
"""

from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict


class GenerationAgent:
    """Genera contenido segun la intencion. Admite multiples instancias (dual generation)."""

    def __init__(self, agent_id: str = "generator_1", style: str = "professional") -> None:
        self.agent_id = agent_id
        self.style = style

    async def create(
        self, insights: Dict[str, Any], intent: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        dispatch: Dict[str, Callable[..., Coroutine]] = {
            "generate_proposal": self._generate_proposal,
            "generate_report": self._generate_report,
            "generate_presentation": self._generate_presentation,
        }
        handler = dispatch.get(intent, self._generate_generic)
        return await handler(insights, context)

    async def _generate_proposal(
        self, insights: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "type": "proposal",
            "content": f"Propuesta comercial generada para {context.get('client', 'cliente')}.",
            "style": self.style,
            "tables": [],
            "recommendations": insights.get("opportunities", []),
            "sources": insights.get("insights", []),
            "metadata": {"client": context.get("client")},
        }

    async def _generate_report(
        self, insights: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "type": "report",
            "content": f"Informe generado para {context.get('client', 'cliente')}.",
            "format": "markdown",
            "insights": insights.get("insights", []),
            "sources": insights.get("insights", []),
            "metadata": {"client": context.get("client")},
        }

    async def _generate_presentation(
        self, insights: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "type": "presentation",
            "slides": [],
            "design": self.style,
            "sources": insights.get("insights", []),
            "metadata": {"client": context.get("client")},
        }

    async def _generate_generic(
        self, insights: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "type": "generic",
            "content": f"Contenido generado para {context.get('client', 'cliente')}.",
            "sources": insights.get("insights", []),
            "metadata": {"client": context.get("client")},
        }
