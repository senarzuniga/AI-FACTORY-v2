"""Action Engine V2: centralized intelligent action planning and prioritization."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class ActionPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    PLANNED = 1


class ActionCategory(Enum):
    LEAD_WORK = "lead_work"
    REQUEST_PROCESSING = "request_processing"
    OFFER_CREATION = "offer_creation"
    NEGOTIATION = "negotiation"
    QUOTE_SENDING = "quote_sending"
    CONTRACT_SIGNING = "contract_signing"
    ORDER_PROCESSING = "order_processing"
    PROJECT_CREATION = "project_creation"
    PROJECT_MANAGEMENT = "project_management"
    DELIVERY_COORDINATION = "delivery_coordination"
    INSTALLATION_PLANNING = "installation_planning"
    COMMISSIONING = "commissioning"
    WARRANTY_MANAGEMENT = "warranty_management"
    AFTERSALES_SUPPORT = "aftersales_support"
    LOYALTY_ACTION = "loyalty_action"
    CROSS_SELLING = "cross_selling"
    RENEWAL = "renewal"
    UPGRADE = "upgrade"


class ActionRole(Enum):
    ADMIN = "administracion"
    PROJECT_MANAGER = "gestion_proyecto"
    ENGINEERING = "ingenieria"
    AFTERSALES = "postventa"
    SALES = "comercial"
    MANAGEMENT = "gerencia"
    QUALITY = "calidad"
    LOGISTICS = "logistica"


@dataclass
class Action:
    id: str
    title: str
    description: str
    category: ActionCategory
    priority: ActionPriority
    role: ActionRole
    score: float
    created_at: datetime
    due_date: Optional[datetime]
    source: str
    context_data: Dict[str, Any]
    status: str = "pending"
    assigned_to: Optional[str] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_time_minutes: int = 60
    tags: List[str] = field(default_factory=list)


class ActionPool:
    def __init__(self) -> None:
        self.actions: Dict[str, Action] = {}
        self.role_assignments: Dict[ActionRole, List[str]] = defaultdict(list)

    def add_action(self, action: Action) -> str:
        self.actions[action.id] = action
        self.role_assignments[action.role].append(action.id)
        return action.id

    def get_pending_actions(
        self,
        role: Optional[ActionRole] = None,
        category: Optional[ActionCategory] = None,
        limit: int = 100,
    ) -> List[Action]:
        pending = [a for a in self.actions.values() if a.status == "pending"]
        if role:
            pending = [a for a in pending if a.role == role]
        if category:
            pending = [a for a in pending if a.category == category]
        pending.sort(key=lambda x: x.score, reverse=True)
        return pending[:limit]

    def get_actions_by_priority(self, min_priority: ActionPriority) -> List[Action]:
        return [
            a
            for a in self.actions.values()
            if a.status == "pending" and a.priority.value >= min_priority.value
        ]

    def update_action_status(self, action_id: str, status: str, assigned_to: Optional[str] = None) -> bool:
        action = self.actions.get(action_id)
        if not action:
            return False
        action.status = status
        if assigned_to:
            action.assigned_to = assigned_to
        if status == "completed":
            action.completed_at = datetime.now()
        return True

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self.actions)
        pending = len([a for a in self.actions.values() if a.status == "pending"])
        completed = len([a for a in self.actions.values() if a.status == "completed"])

        by_role: Dict[str, int] = {}
        for role in ActionRole:
            c = len([a for a in self.actions.values() if a.role == role and a.status == "pending"])
            if c:
                by_role[role.value] = c

        by_priority: Dict[str, int] = {}
        for p in ActionPriority:
            c = len([a for a in self.actions.values() if a.priority == p and a.status == "pending"])
            if c:
                by_priority[p.name] = c

        return {
            "total_actions": total,
            "pending": pending,
            "completed": completed,
            "completion_rate": round(completed / total * 100, 1) if total else 0.0,
            "by_role": by_role,
            "by_priority": by_priority,
        }


class ActionGenerator:
    def __init__(self, action_pool: ActionPool) -> None:
        self.action_pool = action_pool
        self.counter = 0

    def _generate_action_id(self) -> str:
        self.counter += 1
        return f"ACT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.counter:04d}"

    @staticmethod
    def _score(urgency: int, importance: int, business_impact: float, customer_value: float) -> float:
        normalized_impact = min(float(business_impact) / 100000.0, 1.0)
        score = (urgency * 0.4 + importance * 0.4 + ((normalized_impact + customer_value) / 2.0) * 20 * 0.2)
        return min(float(score), 100.0)

    def generate_actions_from_request(self, request_data: Dict[str, Any], company_info: Dict[str, Any]) -> List[Action]:
        company = request_data.get("company_name") or company_info.get("name") or "cliente"
        actions: List[Action] = [
            Action(
                id=self._generate_action_id(),
                title="Procesar nueva solicitud de cliente",
                description=f"Procesar solicitud de {company}",
                category=ActionCategory.REQUEST_PROCESSING,
                priority=ActionPriority.CRITICAL,
                role=ActionRole.SALES,
                score=self._score(100, 90, 50000, 0.5),
                created_at=datetime.now(),
                due_date=datetime.now() + timedelta(hours=24),
                source="request_management_agent",
                context_data=request_data,
                tags=["nueva_solicitud", "urgente"],
            ),
            Action(
                id=self._generate_action_id(),
                title="Investigacion de empresa",
                description=f"Analizar {company}: web, mercado y contexto comercial",
                category=ActionCategory.LEAD_WORK,
                priority=ActionPriority.HIGH,
                role=ActionRole.SALES,
                score=self._score(70, 80, 25000, 0.3),
                created_at=datetime.now(),
                due_date=datetime.now() + timedelta(days=2),
                source="request_management_agent",
                context_data={"company_info": company_info},
                tags=["investigacion", "lead"],
            ),
        ]

        if request_data.get("requirements"):
            actions.append(
                Action(
                    id=self._generate_action_id(),
                    title="Evaluacion tecnica requerida",
                    description="Evaluar factibilidad tecnica de la solicitud",
                    category=ActionCategory.OFFER_CREATION,
                    priority=ActionPriority.HIGH,
                    role=ActionRole.ENGINEERING,
                    score=self._score(80, 85, 30000, 0.4),
                    created_at=datetime.now(),
                    due_date=datetime.now() + timedelta(days=3),
                    source="request_management_agent",
                    context_data={"requirements": request_data.get("requirements")},
                    tags=["evaluacion_tecnica"],
                )
            )

        return actions

    def generate_actions_from_opportunity(self, opportunity: Dict[str, Any], customer: Dict[str, Any]) -> List[Action]:
        return [
            Action(
                id=self._generate_action_id(),
                title=f"Oportunidad de {opportunity.get('product', 'cross-selling')}",
                description=f"Activar oportunidad para {customer.get('name', 'cliente')}",
                category=ActionCategory.CROSS_SELLING,
                priority=ActionPriority.MEDIUM,
                role=ActionRole.SALES,
                score=self._score(50, 70, float(opportunity.get('potential_value', 0)), float(customer.get('lifetime_value', 0.5))),
                created_at=datetime.now(),
                due_date=datetime.now() + timedelta(days=7),
                source="cross_selling_agent",
                context_data={"opportunity": opportunity, "customer": customer},
                tags=["cross_selling", "oportunidad"],
            )
        ]


class ActionOrchestrator:
    def __init__(self, action_pool: ActionPool, action_generator: ActionGenerator) -> None:
        self.pool = action_pool
        self.generator = action_generator

    async def process_and_generate_actions(self, event_type: str, event_data: Dict[str, Any]) -> List[Action]:
        generated: List[Action] = []

        if event_type == "new_request":
            generated = self.generator.generate_actions_from_request(
                event_data.get("request", {}),
                event_data.get("company_info", {}),
            )
        elif event_type == "opportunity_detected":
            generated = self.generator.generate_actions_from_opportunity(
                event_data.get("opportunity", {}),
                event_data.get("customer", {}),
            )

        for action in generated:
            self.pool.add_action(action)

        return generated

    def get_actions_dashboard(self) -> Dict[str, Any]:
        dashboard: Dict[str, Any] = {}
        for role in ActionRole:
            pending = self.pool.get_pending_actions(role=role)
            dashboard[role.value] = {
                "total_pending": len(pending),
                "critical": len([a for a in pending if a.priority == ActionPriority.CRITICAL]),
                "high": len([a for a in pending if a.priority == ActionPriority.HIGH]),
                "actions": [
                    {
                        "id": a.id,
                        "title": a.title,
                        "priority": a.priority.name,
                        "score": a.score,
                        "due_date": a.due_date.isoformat() if a.due_date else None,
                    }
                    for a in pending[:10]
                ],
            }

        dashboard["statistics"] = self.pool.get_statistics()
        return dashboard
