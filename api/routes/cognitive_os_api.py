"""Reusable API surface for AI-FACTORY Cognitive Operating System."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from fastapi import File, Form, UploadFile
from fastapi import HTTPException
from pydantic import BaseModel, Field

from cognitive_os import CognitiveOSSDK, CognitiveOperatingSystem
from cognitive_os.layout_import_framework import LayoutImportFramework
from cognitive_os.layout_versioning import LayoutVersionStore


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


class IndustrialComponentExecuteRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class AHDERunRequest(BaseModel):
    mission_id: str = "M010"
    uncertainty: str
    context: dict[str, Any] = Field(default_factory=dict)


class LayoutRevisionCompareRequest(BaseModel):
    layout_name: str
    revision_a: str
    revision_b: str


_system = CognitiveOperatingSystem()
_sdk = CognitiveOSSDK(_system)
_layout_import_framework = LayoutImportFramework()
_layout_version_store = LayoutVersionStore()
REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_DXF_UPLOAD_BYTES = 60 * 1024 * 1024
MAX_DXF_CHUNK_TOTAL_BYTES = 700 * 1024 * 1024
DXF_CHUNK_UPLOADS: dict[str, dict[str, Any]] = {}


def _prune_stale_chunk_uploads(max_age_seconds: int = 7200) -> None:
    now = time.time()
    stale_ids = [
        upload_id
        for upload_id, entry in DXF_CHUNK_UPLOADS.items()
        if now - float(entry.get("updated_at", now)) > max_age_seconds
    ]
    for upload_id in stale_ids:
        entry = DXF_CHUNK_UPLOADS.pop(upload_id, None)
        if not entry:
            continue
        temp_path = Path(str(entry.get("temp_path", "")))
        temp_dir = temp_path.parent
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        if temp_dir.exists():
            temp_dir.rmdir()

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


@router.get("/industrial-intelligence/status")
async def industrial_intelligence_status() -> dict[str, Any]:
    return {
        "mission_id": "M010",
        "ahde_policy": "enabled",
        "health": _sdk.industrial_intelligence_status(),
    }


@router.get("/industrial-intelligence/components")
async def industrial_intelligence_components() -> dict[str, Any]:
    components = _sdk.industrial_intelligence_components()
    return {
        "mission_id": "M010",
        "count": len(components),
        "components": components,
    }


@router.get("/industrial-intelligence/components/{component_id}")
async def industrial_intelligence_component(component_id: str) -> dict[str, Any]:
    return _sdk.industrial_intelligence_component(component_id)


@router.post("/industrial-intelligence/components/{component_id}/execute")
async def industrial_intelligence_execute(
    component_id: str,
    request: IndustrialComponentExecuteRequest,
) -> dict[str, Any]:
    result = _sdk.industrial_intelligence_execute(component_id, request.payload)
    return {
        "mission_id": "M010",
        "component_id": component_id,
        "result": result,
    }


@router.post("/industrial-intelligence/ahde/decide")
async def industrial_intelligence_ahde_decide(request: AHDERunRequest) -> dict[str, Any]:
    return _sdk.industrial_intelligence_ahde(
        mission_id=request.mission_id,
        uncertainty=request.uncertainty,
        context=request.context,
    )


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


@router.post("/layout-workbench/import/discover-providers")
async def layout_import_discover_providers(request: GenericPayload) -> dict[str, Any]:
    providers = _layout_import_framework.discover_available_providers(request.payload)
    return {
        "providers": providers,
        "count": len(providers),
    }


@router.post("/layout-workbench/upload/dxf")
async def layout_workbench_upload_dxf(
    file: UploadFile = File(...),
    layout_name: str | None = Form(default=None),
) -> dict[str, Any]:
    suffix = Path(file.filename or "layout.dxf").suffix or ".dxf"
    temp_dir = Path(tempfile.mkdtemp(prefix="layout-upload-dxf-"))
    temp_path = temp_dir / f"source{suffix}"

    bytes_written = 0
    with temp_path.open("wb") as handle:
        while True:
            chunk = await file.read(4 * 1024 * 1024)
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > MAX_DXF_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        f"DXF file too large ({bytes_written} bytes). "
                        f"Maximum supported upload size is {MAX_DXF_UPLOAD_BYTES} bytes. "
                        "Reduce/export simplified DXF before upload."
                    ),
                )
            handle.write(chunk)

    payload = {
        "source_format": "dxf",
        "layout_name": layout_name or Path(file.filename or "layout.dxf").stem,
        "source_path": str(temp_path),
        "source_filename": file.filename or temp_path.name,
        "source_size": temp_path.stat().st_size,
        "revision_note": "uploaded DXF from layout workbench",
        "compact_response": True,
    }
    result = _sdk.industrial_intelligence_execute("dxf-intelligence-parser", payload)
    return {
        "mission_id": "M010",
        "component_id": "dxf-intelligence-parser",
        "result": result,
    }


@router.post("/layout-workbench/upload/dxf/chunk/init")
async def layout_workbench_upload_dxf_chunk_init(
    filename: str = Form(...),
    layout_name: str | None = Form(default=None),
    total_size: int = Form(default=0),
) -> dict[str, Any]:
    _prune_stale_chunk_uploads()
    if total_size > MAX_DXF_CHUNK_TOTAL_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"DXF file too large ({total_size} bytes). "
                f"Maximum supported chunked upload size is {MAX_DXF_CHUNK_TOTAL_BYTES} bytes."
            ),
        )

    suffix = Path(filename).suffix or ".dxf"
    temp_dir = Path(tempfile.mkdtemp(prefix="layout-upload-dxf-chunk-"))
    temp_path = temp_dir / f"source{suffix}"
    temp_path.touch()

    upload_id = f"dxf-{uuid4()}"
    DXF_CHUNK_UPLOADS[upload_id] = {
        "temp_path": str(temp_path),
        "layout_name": layout_name or Path(filename).stem,
        "source_filename": filename,
        "total_size": int(total_size),
        "bytes_written": 0,
        "updated_at": time.time(),
    }
    return {
        "upload_id": upload_id,
        "chunk_size": 4 * 1024 * 1024,
        "max_total_size": MAX_DXF_CHUNK_TOTAL_BYTES,
    }


@router.post("/layout-workbench/upload/dxf/chunk/append")
async def layout_workbench_upload_dxf_chunk_append(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    entry = DXF_CHUNK_UPLOADS.get(upload_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Unknown upload_id for DXF chunk upload")

    temp_path = Path(str(entry["temp_path"]))
    chunk_data = await file.read()
    next_size = int(entry.get("bytes_written", 0)) + len(chunk_data)
    if next_size > MAX_DXF_CHUNK_TOTAL_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"DXF file too large ({next_size} bytes). "
                f"Maximum supported chunked upload size is {MAX_DXF_CHUNK_TOTAL_BYTES} bytes."
            ),
        )

    with temp_path.open("ab") as handle:
        handle.write(chunk_data)

    entry["bytes_written"] = next_size
    entry["updated_at"] = time.time()
    return {
        "upload_id": upload_id,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
        "bytes_written": next_size,
    }


@router.post("/layout-workbench/upload/dxf/chunk/complete")
async def layout_workbench_upload_dxf_chunk_complete(upload_id: str = Form(...)) -> dict[str, Any]:
    entry = DXF_CHUNK_UPLOADS.get(upload_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Unknown upload_id for DXF chunk upload")

    temp_path = Path(str(entry["temp_path"]))
    if not temp_path.exists() or temp_path.stat().st_size <= 0:
        raise HTTPException(status_code=400, detail="No DXF data received for chunked upload")

    payload = {
        "source_format": "dxf",
        "layout_name": entry.get("layout_name") or temp_path.stem,
        "source_path": str(temp_path),
        "source_filename": entry.get("source_filename") or temp_path.name,
        "source_size": temp_path.stat().st_size,
        "revision_note": "uploaded DXF from layout workbench (chunked)",
        "compact_response": True,
    }
    result = _sdk.industrial_intelligence_execute("dxf-intelligence-parser", payload)

    DXF_CHUNK_UPLOADS.pop(upload_id, None)
    temp_dir = temp_path.parent
    temp_path.unlink(missing_ok=True)
    try:
        temp_dir.rmdir()
    except OSError:
        pass

    return {
        "mission_id": "M010",
        "component_id": "dxf-intelligence-parser",
        "result": result,
    }


@router.post("/layout-workbench/plant-state/analyze")
async def layout_workbench_plant_state_analyze(request: IndustrialComponentExecuteRequest) -> dict[str, Any]:
    result = _sdk.industrial_intelligence_execute("dxf-intelligence-parser", request.payload)
    return {
        "mission_id": "M010",
        "component_id": "dxf-intelligence-parser",
        "layout_name": result.get("layout_name"),
        "plant_state_report": result.get("plant_state_report", {}),
        "simulation": result.get("simulation", {}),
        "engineering_analysis": result.get("engineering_analysis", {}),
    }


@router.get("/layout-workbench/versioning/{layout_name}")
async def layout_versioning_history(layout_name: str) -> dict[str, Any]:
    return _layout_version_store.list_history(layout_name)


@router.post("/layout-workbench/versioning/compare")
async def layout_versioning_compare(request: LayoutRevisionCompareRequest) -> dict[str, Any]:
    return _layout_version_store.compare_revisions(
        layout_name=request.layout_name,
        revision_a=request.revision_a,
        revision_b=request.revision_b,
    )


@router.post("/continuous-improvement/refresh")
async def continuous_improvement_refresh(request: GenericPayload) -> dict[str, Any]:
    return _system.continuous_improvement.refresh(
        state=_sdk.export_state(),
        mission_event=request.payload,
    )
