"""FastAPI Action Dashboard endpoints for Action Engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.action_engine import ActionPool, ActionPriority, ActionRole


class ActionResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    role: str
    category: str
    score: float
    due_date: Optional[str]
    status: str
    tags: List[str]


class DashboardResponse(BaseModel):
    role_dashboard: Dict[str, Dict[str, Any]]
    statistics: Dict[str, Any]
    recommended_actions: List[ActionResponse]
    generated_at: str


def create_action_router(action_pool: ActionPool) -> APIRouter:
    router = APIRouter(prefix="/api/actions", tags=["actions"])

    @router.get("/dashboard/{role}", response_model=DashboardResponse)
    async def get_role_dashboard(role: str) -> DashboardResponse:
        try:
            role_enum = next(r for r in ActionRole if r.value == role)
        except StopIteration as exc:
            raise HTTPException(status_code=400, detail=f"Rol invalido: {role}") from exc

        pending_actions = action_pool.get_pending_actions(role=role_enum)

        dashboard = {
            "role_dashboard": {
                role: {
                    "total_pending": len(pending_actions),
                    "critical": len([a for a in pending_actions if a.priority.value >= 4]),
                    "high": len([a for a in pending_actions if a.priority.value == 4]),
                    "actions": [
                        {
                            "id": a.id,
                            "title": a.title,
                            "priority": a.priority.name,
                            "score": a.score,
                            "due_date": a.due_date.isoformat() if a.due_date else None,
                        }
                        for a in pending_actions[:20]
                    ],
                }
            },
            "statistics": action_pool.get_statistics(),
            "recommended_actions": [
                ActionResponse(
                    id=a.id,
                    title=a.title,
                    description=a.description,
                    priority=a.priority.name,
                    role=a.role.value,
                    category=a.category.value,
                    score=a.score,
                    due_date=a.due_date.isoformat() if a.due_date else None,
                    status=a.status,
                    tags=a.tags,
                )
                for a in pending_actions[:10]
            ],
            "generated_at": datetime.now().isoformat(),
        }
        return DashboardResponse(**dashboard)

    @router.post("/actions/{action_id}/complete")
    async def complete_action(action_id: str, assigned_to: Optional[str] = None) -> Dict[str, str]:
        success = action_pool.update_action_status(action_id, "completed", assigned_to)
        if not success:
            raise HTTPException(status_code=404, detail=f"Accion no encontrada: {action_id}")
        return {"status": "success", "action_id": action_id}

    @router.get("/actions/pending/priority/{min_priority}")
    async def get_actions_by_priority(min_priority: int) -> List[Dict[str, Any]]:
        priority_map = {
            1: ActionPriority.PLANNED,
            2: ActionPriority.LOW,
            3: ActionPriority.MEDIUM,
            4: ActionPriority.HIGH,
            5: ActionPriority.CRITICAL,
        }
        selected = priority_map.get(min_priority, ActionPriority.MEDIUM)
        actions = action_pool.get_actions_by_priority(selected)
        return [
            {
                "id": a.id,
                "title": a.title,
                "priority": a.priority.name,
                "role": a.role.value,
                "due_date": a.due_date.isoformat() if a.due_date else None,
            }
            for a in actions
        ]

    return router
