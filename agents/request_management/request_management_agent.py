"""Request Management Agent enhanced with Action Engine integration."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import aiohttp
except Exception:  # pragma: no cover - optional dependency fallback
    aiohttp = None

try:
    from agents.action_engine import ActionGenerator, ActionOrchestrator, ActionPool

    ACTION_ENGINE_AVAILABLE = True
except Exception:
    ACTION_ENGINE_AVAILABLE = False


class RequestType(Enum):
    OFFER_CREATION = "offer_creation"
    ENGINEERING_EVALUATION = "engineering_evaluation"
    ADMIN_EMAIL = "admin_email"
    AFTERSALES_EMAIL = "aftersales_email"


class RequestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Request:
    id: str
    type: RequestType
    source_text: str
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    company_info: Dict[str, Any] = field(default_factory=dict)
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    result: Any = None
    generated_actions: List[Dict[str, Any]] = field(default_factory=list)


class RequestManagementAgent:
    def __init__(self, supabase_url: str, supabase_key: str, sales_engine_url: str) -> None:
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.sales_engine_url = sales_engine_url
        self.requests_pool: List[Request] = []
        self.engineering_email = "andrea.tapia@estudiantat.upc.edu"
        self.session: Any = None

        self.action_orchestrator = None
        if ACTION_ENGINE_AVAILABLE:
            pool = ActionPool()
            generator = ActionGenerator(pool)
            self.action_orchestrator = ActionOrchestrator(pool, generator)

    async def initialize(self) -> None:
        if not self.session and aiohttp is not None:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def process_request(self, input_text: str, input_file: Optional[str] = None) -> Request:
        full_text = await self._extract_text(input_text, input_file)
        request_type = await self._classify_request(full_text)
        extracted_data = await self._extract_structured_data(full_text)
        company_info = await self._enrich_company_info(extracted_data.get("company_name"))

        request = Request(
            id=f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=request_type,
            source_text=full_text,
            extracted_data=extracted_data,
            company_info=company_info,
        )

        self.requests_pool.append(request)
        await self._process_by_type(request)

        if self.action_orchestrator:
            actions = await self.action_orchestrator.process_and_generate_actions(
                "new_request",
                {"request": extracted_data, "company_info": company_info},
            )
            request.generated_actions = [
                {
                    "id": a.id,
                    "title": a.title,
                    "priority": a.priority.name,
                    "role": a.role.value,
                }
                for a in actions
            ]

        return request

    async def get_requests_pool(self, status: Optional[RequestStatus] = None) -> List[Request]:
        if status:
            return [r for r in self.requests_pool if r.status == status]
        return self.requests_pool

    async def get_action_dashboard(self) -> Dict[str, Any]:
        if self.action_orchestrator:
            return self.action_orchestrator.get_actions_dashboard()
        return {"error": "Action Engine no disponible"}

    async def _extract_text(self, text: str, file_path: Optional[str]) -> str:
        _ = file_path
        return text

    async def _classify_request(self, text: str) -> RequestType:
        t = text.lower()
        if any(w in t for w in ["oferta", "presupuesto", "cotizacion", "cotización"]):
            return RequestType.OFFER_CREATION
        if any(w in t for w in ["ingenieria", "ingeniería", "tecnico", "técnico", "instalacion", "instalación"]):
            return RequestType.ENGINEERING_EVALUATION
        if any(w in t for w in ["administracion", "administración", "factura", "pago"]):
            return RequestType.ADMIN_EMAIL
        if any(w in t for w in ["postventa", "garantia", "garantía", "soporte"]):
            return RequestType.AFTERSALES_EMAIL
        return RequestType.OFFER_CREATION

    async def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "company_name": None,
            "contact_person": None,
            "email": None,
            "phone": None,
            "product_interest": [],
            "budget": None,
            "deadline": None,
            "requirements": [],
        }

        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        if email_match:
            data["email"] = email_match.group(0)

        patterns = [
            r"empresa[:,\s]+([A-Z][\w\s\.-]+)",
            r"empresa\s*:\s*([A-Z][\w\s\.-]+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                data["company_name"] = m.group(1).strip()
                break

        return data

    async def _enrich_company_info(self, company_name: Optional[str]) -> Dict[str, Any]:
        if not company_name:
            return {}
        return {
            "name": company_name,
            "industry": None,
            "size": None,
            "website": None,
            "market_segments": [],
        }

    async def _process_by_type(self, request: Request) -> None:
        request.status = RequestStatus.PROCESSING

        if request.type == RequestType.OFFER_CREATION:
            request.result = {
                "offer_data": {
                    "customer_name": request.extracted_data.get("company_name"),
                    "contact_email": request.extracted_data.get("email"),
                    "source": "request_management_agent",
                },
                "status": "ready_for_creation",
            }
        elif request.type == RequestType.ENGINEERING_EVALUATION:
            request.result = {
                "email_sent_to": self.engineering_email,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            request.result = {
                "email_sent": True,
                "timestamp": datetime.now().isoformat(),
            }

        request.status = RequestStatus.COMPLETED
        request.processed_at = datetime.now()
