"""
ANALYSIS AGENT
Convierte datos estructurados en insights.
Detecta problemas y oportunidades.
"""

from __future__ import annotations

from typing import Any, Dict, List


class AnalysisAgent:
    """Transforma datos en insights accionables."""

    async def process(self, data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Analiza datos segun la intencion detectada."""
        insights: List[str] = []
        problems: List[str] = []
        opportunities: List[str] = []

        sources = data.get("sources", [])
        if sources:
            insights.append(f"Datos cargados desde {len(sources)} fuente(s).")

        return {
            "intent": intent,
            "insights": insights,
            "problems": problems,
            "opportunities": opportunities,
            "metrics": {},
            "source_count": len(sources),
        }
