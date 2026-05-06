"""
DELIVERY AGENT
Publica en Teams Community con control de permisos via Context Layer.
"""

from __future__ import annotations

from typing import Any, Dict, List


class DeliveryAgent:
    """Publica contenido en los destinos correctos segun contexto y tipo."""

    async def publish(
        self, content: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        destinations: List[str] = self._resolve_destinations(
            content.get("type", "generic"), context
        )

        results = [
            {
                "destination": dest,
                "status": "published",
                "url": self._generate_url(dest, content),
            }
            for dest in destinations
        ]

        return {
            "published": True,
            "destinations": results,
            "requires_external_share": context.get("permissions", {}).get(
                "can_share_external", False
            ),
        }

    def _resolve_destinations(self, content_type: str, context: Dict[str, Any]) -> List[str]:
        client = context.get("client", "client")
        mapping: Dict[str, List[str]] = {
            "proposal": [
                f"teams_community://client_{client}/04_DELIVERABLES/Proposals",
                "teams://channel=deliverables",
            ],
            "report": [f"teams_community://client_{client}/02_ANALYSIS/Reports"],
            "presentation": [
                f"teams_community://client_{client}/04_DELIVERABLES/Presentations"
            ],
        }
        return mapping.get(content_type, [f"teams_community://client_{client}/04_DELIVERABLES"])

    def _generate_url(self, destination: str, content: Dict[str, Any]) -> str:  # noqa: ARG002
        path = destination.replace("teams_community://", "").replace("teams://", "teams/")
        return f"https://teams.live.com/l/community/FEA5JSTpd_3FAKh9gI/{path}"
