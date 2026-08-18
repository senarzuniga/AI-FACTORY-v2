from __future__ import annotations

import io
import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.routes.hub_api import app  # noqa: E402
from api.routes import cognitive_os_api  # noqa: E402


client = TestClient(app)


def test_mission_control_status_contract() -> None:
    response = client.get("/api/cognitive-os/mission-control/status")
    assert response.status_code == 200
    payload = response.json()
    assert {"active_missions", "blocked_missions", "pending_quality_gates", "knowledge_gaps", "next_actions", "why_working_on_this", "what_will_it_do_next", "no_idle"} <= payload.keys()


def test_layout_workbench_direct_dxf_upload_returns_compact_result() -> None:
    dxf_text = "\n".join(
        [
            "0",
            "SECTION",
            "2",
            "ENTITIES",
            "0",
            "TEXT",
            "8",
            "MACHINES",
            "1",
            "CNC 77",
            "10",
            "10",
            "20",
            "10",
            "0",
            "ENDSEC",
            "0",
            "EOF",
        ]
    )

    response = client.post(
        "/api/cognitive-os/layout-workbench/upload/dxf",
        data={"layout_name": "direct-upload-layout"},
        files={"file": ("direct-upload-layout.dxf", io.BytesIO(dxf_text.encode("utf-8")), "application/dxf")},
    )

    assert response.status_code == 200
    payload = response.json()
    result = payload["result"]
    assert result["parsed_entities"] >= 1
    assert "layout_result" not in result
    assert result["factory_graph"]["node_count"] >= 1
    assert result["factory_graph"]["nodes"]
    assert "plant_state_report" in result
    assert "operational_summary" in result


def test_layout_workbench_chunked_dxf_job_completes() -> None:
    dxf_text = "\n".join(
        [
            "0",
            "SECTION",
            "2",
            "ENTITIES",
            "0",
            "TEXT",
            "8",
            "MACHINES",
            "1",
            "Chunk Cell 01",
            "10",
            "12",
            "20",
            "9",
            "0",
            "ENDSEC",
            "0",
            "EOF",
        ]
    ).encode("utf-8")

    init_response = client.post(
        "/api/cognitive-os/layout-workbench/upload/dxf/chunk/init",
        data={
            "filename": "chunk-upload-layout.dxf",
            "layout_name": "chunk-upload-layout",
            "total_size": len(dxf_text),
        },
    )
    assert init_response.status_code == 200
    upload_id = init_response.json()["upload_id"]

    append_response = client.post(
        "/api/cognitive-os/layout-workbench/upload/dxf/chunk/append",
        data={
            "upload_id": upload_id,
            "chunk_index": 0,
            "total_chunks": 1,
        },
        files={"file": ("chunk-upload-layout.part0", io.BytesIO(dxf_text), "application/octet-stream")},
    )
    assert append_response.status_code == 200

    complete_response = client.post(
        "/api/cognitive-os/layout-workbench/upload/dxf/chunk/complete",
        data={"upload_id": upload_id},
    )
    assert complete_response.status_code == 200
    job_id = complete_response.json()["job_id"]

    deadline = time.time() + 10
    final_payload: dict | None = None
    while time.time() < deadline:
        job_response = client.get(f"/api/cognitive-os/layout-workbench/upload/dxf/job/{job_id}")
        assert job_response.status_code == 200
        final_payload = job_response.json()
        if final_payload["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)

    assert final_payload is not None
    assert final_payload["status"] == "completed"
    assert final_payload["result"]["result"]["parsed_entities"] >= 1


def test_layout_workbench_demo_uses_server_file_without_upload(tmp_path, monkeypatch) -> None:
    demo_path = tmp_path / "Plan Projet Cognac.dxf"
    demo_path.write_text(
        "\n".join(
            [
                "0", "SECTION", "2", "ENTITIES", "0", "TEXT", "8", "MACHINES",
                "1", "Demo Cell 01", "10", "12", "20", "9", "0", "ENDSEC", "0", "EOF",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cognitive_os_api, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(cognitive_os_api, "DEMO_DXF_PATH", demo_path)
    cognitive_os_api.DEMO_DXF_JOB_CACHE.clear()

    response = client.post("/api/cognitive-os/layout-workbench/demo/analyze")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source_filename"] == demo_path.name
    assert payload["cached"] is False

    deadline = time.time() + 10
    final_payload: dict | None = None
    while time.time() < deadline:
        job_response = client.get(f"/api/cognitive-os/layout-workbench/upload/dxf/job/{payload['job_id']}")
        assert job_response.status_code == 200
        final_payload = job_response.json()
        if final_payload["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)

    assert final_payload is not None
    assert final_payload["status"] == "completed"
    assert final_payload["result"]["result"]["parsed_entities"] >= 1
    assert demo_path.exists()

    cached_response = client.post("/api/cognitive-os/layout-workbench/demo/analyze")
    assert cached_response.status_code == 200
    assert cached_response.json()["job_id"] == payload["job_id"]
    assert cached_response.json()["cached"] is True
