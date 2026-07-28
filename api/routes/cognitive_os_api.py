"""Reusable API surface for AI-FACTORY Cognitive Operating System."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from cognitive_os import CognitiveOSSDK, CognitiveOperatingSystem


class GenericPayload(BaseModel):
    payload: dict[str, Any]


class MissionUpsertRequest(BaseModel):
    id: str
    title: str
    objective: str
    status: str = "draft"
    objectives: list[dict[str, Any]] = Field(default_factory=list)
    strategic_alignment: dict[str, Any] = Field(default_factory=dict)
    value: dict[str, Any] = Field(default_factory=dict)
    hypothesis_portfolio_ids: list[str] = Field(default_factory=list)
    scoring_matrix: dict[str, Any] = Field(default_factory=dict)
    work_packages: list[dict[str, Any]] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    kpis: list[dict[str, Any]] = Field(default_factory=list)
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    lessons_learned: list[str] = Field(default_factory=list)
    mission_state: str = "initialized"
    mission_history: list[dict[str, Any]] = Field(default_factory=list)
    mission_evolution: list[dict[str, Any]] = Field(default_factory=list)
    mission_score: float = 0.0
    mission_roi: float = 0.0
    mission_confidence: float = 0.0
    mission_traceability: dict[str, Any] = Field(default_factory=dict)
    mission_knowledge_assets: list[dict[str, Any]] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ModelSelectionResponse(BaseModel):
    hypotheses: list[dict[str, Any]]
    selected: dict[str, Any]
    production_ready: bool


class RunRequest(BaseModel):
    max_cycles: int = Field(default=100, ge=1, le=1000)


_system = CognitiveOperatingSystem()
_sdk = CognitiveOSSDK(_system)
REPO_ROOT = Path(__file__).resolve().parents[2]

LAYOUT_PLATFORM = {
    "id": "industrial-layout-workbench",
    "name": "Industrial Layout Intelligence Workbench",
    "contract_version": "v1",
    "metadata": {
        "owner": "AI-FACTORY",
        "target_integration": ["ING_DIGHUB"],
        "ui": "/dashboard/layout_workbench.html",
        "api_status": "/api/cognitive-os/layout-workbench/status",
    },
}

LAYOUT_CAPABILITIES = [
    {
        "id": "layout-analysis-workbench",
        "description": "Industrial layout analysis UI and orchestration endpoint.",
        "interfaces": ["/dashboard/layout_workbench.html", "/api/cognitive-os/layout-workbench/status"],
        "dependencies": ["mission-manager-core", "knowledge-core-apis"],
    },
    {
        "id": "factory-graph-readiness",
        "description": "Factory graph readiness and dependency tracking for layout engineering.",
        "interfaces": ["/api/cognitive-os/layout-workbench/dependency-map"],
        "dependencies": ["layout-analysis-workbench"],
    },
]

LAYOUT_MISSION = {
    "id": "LAYOUT-M-001",
    "title": "Industrial Layout Analysis Workbench",
    "objective": "Expose and operationalize layout analysis as a reusable mission for ING_DIGHUB integration.",
    "status": "planned",
    "mission_state": "initialized",
    "dependencies": [],
    "capabilities": ["layout-analysis-workbench", "factory-graph-readiness"],
    "deliverables": [
        "dashboard/layout_workbench.html",
        "LAYOUT_WORKBENCH_STATUS.html",
        "api/cognitive-os/layout-workbench/*",
    ],
    "tags": ["layout", "factory", "workbench", "digital_twin", "under_development"],
    "objectives": [
        {
            "id": "obj-layout-1",
            "statement": "Analyze current plant",
            "owner": "mission-manager",
            "priority": 1,
        },
        {
            "id": "obj-layout-2",
            "statement": "Create AMR proposal",
            "owner": "mission-manager",
            "priority": 2,
        },
        {
            "id": "obj-layout-3",
            "statement": "Generate Executive Report",
            "owner": "mission-manager",
            "priority": 2,
        },
    ],
}


def _load_layout_status_file() -> dict[str, Any]:
    status_file = REPO_ROOT / "data" / "layout_workbench_status.json"
    if not status_file.exists():
        return {}
    try:
        return json.loads(status_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _ensure_layout_workbench_registration() -> None:
    _sdk.register_platform(LAYOUT_PLATFORM)
    for capability in LAYOUT_CAPABILITIES:
        _sdk.upsert_capability(capability)
    _sdk.upsert_mission(LAYOUT_MISSION)

router = APIRouter(prefix="/api/cognitive-os", tags=["cognitive-os"])
_ensure_layout_workbench_registration()


@router.get("/health")
async def health() -> dict[str, Any]:
    _ensure_layout_workbench_registration()
    return {
        "status": "ok",
        "service": "ai-factory-cognitive-os",
        "governance": "enabled",
        "business_modules": "excluded",
    }


@router.post("/agents/register")
async def register_agent(request: GenericPayload) -> dict[str, str]:
    _sdk.register_agent(request.payload)
    return {"status": "registered"}


@router.post("/platforms/register")
async def register_platform(request: GenericPayload) -> dict[str, str]:
    _sdk.register_platform(request.payload)
    return {"status": "registered"}


@router.post("/capabilities/upsert")
async def upsert_capability(request: GenericPayload) -> dict[str, str]:
    _sdk.upsert_capability(request.payload)
    return {"status": "upserted"}


@router.post("/missions/upsert")
async def upsert_mission(request: MissionUpsertRequest) -> dict[str, str]:
    _sdk.upsert_mission(request.model_dump())
    return {"status": "upserted"}


@router.post("/hypotheses/submit")
async def submit_hypothesis(request: GenericPayload) -> dict[str, str]:
    _sdk.submit_hypothesis(request.payload)
    return {"status": "submitted"}


@router.post("/knowledge/evidence")
async def ingest_evidence(request: GenericPayload) -> dict[str, str]:
    _sdk.ingest_evidence(request.payload)
    return {"status": "ingested"}


@router.post("/knowledge/truth")
async def assert_truth(request: GenericPayload) -> dict[str, Any]:
    return _sdk.assert_truth(request.payload)


@router.post("/autonomous/run")
async def run_autonomous(request: RunRequest) -> dict[str, Any]:
    return _sdk.run_autonomous(max_cycles=request.max_cycles)


@router.post("/mission-model/evaluate", response_model=ModelSelectionResponse)
async def evaluate_mission_model() -> ModelSelectionResponse:
    return ModelSelectionResponse(**_sdk.evaluate_mission_model())


@router.get("/mission-model/production-ready")
async def mission_model_production_ready() -> dict[str, bool]:
    return {"production_ready": _sdk.mission_model_production_ready()}


@router.get("/state")
async def export_state() -> dict[str, Any]:
    return _sdk.export_state()


@router.post("/layout-workbench/register")
async def register_layout_workbench() -> dict[str, Any]:
    _ensure_layout_workbench_registration()
    state = _sdk.export_state()
    platform_ids = {item.get("id") for item in state.get("platforms", [])}
    capability_ids = {item.get("id") for item in state.get("capabilities", [])}
    mission_ids = {item.get("id") for item in state.get("missions", [])}
    return {
        "status": "registered",
        "platform_registered": "industrial-layout-workbench" in platform_ids,
        "capabilities_registered": all(
            capability["id"] in capability_ids for capability in LAYOUT_CAPABILITIES
        ),
        "mission_registered": "LAYOUT-M-001" in mission_ids,
    }


@router.get("/layout-workbench/dependency-map")
async def layout_workbench_dependency_map() -> dict[str, Any]:
    status_data = _load_layout_status_file()
    dependency_map = status_data.get("dependency_map")
    if dependency_map:
        return {
            "source": "data/layout_workbench_status.json",
            "dependency_map": dependency_map,
        }
    return {
        "source": "fallback",
        "dependency_map": {
            "ui": ["dashboard/layout_workbench.html"],
            "api": ["api/routes/cognitive_os_api.py"],
            "mission_manager": ["cognitive_os/mission_core.py"],
            "registries": ["cognitive_os/registries.py"],
            "spec": ["specs/factory_intelligence_workbench.md"],
        },
    }


@router.get("/layout-workbench/status")
async def layout_workbench_status() -> dict[str, Any]:
    _ensure_layout_workbench_registration()
    state = _sdk.export_state()
    status_data = _load_layout_status_file()

    platforms = state.get("platforms", [])
    capabilities = state.get("capabilities", [])
    missions = state.get("missions", [])

    platform_ids = {item.get("id") for item in platforms}
    capability_ids = {item.get("id") for item in capabilities}
    mission_ids = {item.get("id") for item in missions}

    maturity = status_data.get("maturity", {})
    if not maturity:
        maturity = {
            "DWG parser": {"status": "missing", "percent": 0},
            "DXF parser": {"status": "missing", "percent": 0},
            "Geometry Engine": {"status": "partial", "percent": 35},
            "Factory Graph": {"status": "partial", "percent": 45},
            "Knowledge Graph": {"status": "partial", "percent": 55},
            "Simulation": {"status": "partial", "percent": 40},
            "Mission Manager": {"status": "implemented", "percent": 80},
            "Digital Twin": {"status": "under_development", "percent": 35},
            "Engineering Optimizer": {"status": "partial", "percent": 45},
        }

    return {
        "workbench": "industrial-layout-intelligence",
        "registration": {
            "platform_registry": "industrial-layout-workbench" in platform_ids,
            "capability_registry": all(
                capability["id"] in capability_ids for capability in LAYOUT_CAPABILITIES
            ),
            "mission_manager": "LAYOUT-M-001" in mission_ids,
        },
        "ui": {
            "path": "dashboard/layout_workbench.html",
            "route": "http://localhost:8080/dashboard/layout_workbench.html",
        },
        "maturity": maturity,
        "implementation_percent": status_data.get("implementation_percent", 42),
        "pending_functionality": status_data.get("pending_functionality", []),
        "recommended_next_missions": status_data.get("recommended_next_missions", []),
        "under_development": True,
    }


@router.get("/layout-workbench/missions")
async def layout_workbench_missions() -> dict[str, Any]:
    _ensure_layout_workbench_registration()
    state = _sdk.export_state()
    missions = [
        mission
        for mission in state.get("missions", [])
        if "layout" in mission.get("id", "").lower()
        or "layout" in " ".join(mission.get("tags", [])).lower()
        or "layout" in mission.get("title", "").lower()
    ]
    return {"missions": missions, "count": len(missions)}
