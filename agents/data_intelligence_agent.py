"""
DATA INTELLIGENCE AGENT
Solo accede a datos y los estructura.
NO analiza - solo prepara.
"""

from __future__ import annotations

from typing import Any, Dict, List


class DataIntelligenceAgent:
    """Accede a fuentes de datos segun contexto y las estructura."""

    supported_formats: List[str] = ["excel", "csv", "json", "sharepoint"]

    async def fetch(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Accede a fuentes de datos permitidas y retorna datos estructurados."""
        allowed_sources = [
            src
            for src in context.get("data_sources", [])
        ]
        return {
            "data": "structured_data",
            "sources": allowed_sources,
            "client": context.get("client"),
            "fetched_by": "data_intelligence_agent",
        }
