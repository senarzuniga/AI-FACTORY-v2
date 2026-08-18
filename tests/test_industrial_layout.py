from __future__ import annotations

import base64
import sys

import cognitive_os.industrial_layout as industrial_layout_module
from cognitive_os import IndustrialLayoutInterpreter
from cognitive_os.layout_import_framework import LayoutImportFramework
from cognitive_os.system import CognitiveOperatingSystem


def test_layout_interpreter_produces_factory_graph_and_analysis() -> None:
    interpreter = IndustrialLayoutInterpreter()
    result = interpreter.interpret(
        {
            "layout_name": "sample-production-line",
            "source_format": "json",
            "entities": [
                {
                    "id": "machine-01",
                    "label": "CNC Machine 01",
                    "layer": "MACHINES",
                    "type": "block",
                    "center": [10, 10],
                    "bounds": [8, 8, 12, 12],
                },
                {
                    "id": "conveyor-01",
                    "label": "Main Conveyor",
                    "layer": "FLOW",
                    "type": "polyline",
                    "points": [[12, 10], [22, 10]],
                },
                {
                    "id": "buffer-01",
                    "label": "WIP Buffer",
                    "layer": "WIP",
                    "type": "circle",
                    "center": [24, 10],
                    "bounds": [22, 8, 26, 12],
                },
                {
                    "id": "warehouse-01",
                    "label": "Raw Warehouse",
                    "layer": "STORAGE",
                    "type": "block",
                    "center": [40, 10],
                    "bounds": [36, 6, 44, 14],
                },
                {
                    "id": "route-01",
                    "label": "AMR Route A",
                    "layer": "ROUTES",
                    "type": "line",
                    "points": [[5, 5], [45, 5]],
                },
                {
                    "id": "safety-01",
                    "label": "Safety Zone",
                    "layer": "SAFETY",
                    "type": "hatch",
                    "center": [10, 30],
                    "bounds": [0, 20, 20, 40],
                },
            ],
        }
    )

    kinds = {node["kind"] for node in result["factory_graph"]["nodes"]}

    assert result["factory_graph"]["node_count"] == 6
    assert result["factory_graph"]["edge_count"] > 0
    assert {"machine", "conveyor", "buffer", "warehouse", "amr_route", "safety_zone"}.issubset(kinds)
    assert result["digital_twin"]["nodes"] == 6
    assert result["simulation"]["production_capacity"] > 0
    assert result["engineering_analysis"]["layout_quality"]["status"] in {"good", "excellent", "acceptable"}
    assert result["plant_state_report"]["state_status"] in {"good", "excellent", "acceptable", "needs_improvement"}
    assert "kpi_snapshot" in result["plant_state_report"]
    assert result["operational_summary"]["equipment"]
    assert result["operational_summary"]["processes"]
    assert result["operational_summary"]["processes"][0]["basis"] in {"explicit_label", "inferred_from_equipment_sequence"}
    assert result["operational_summary"]["measurements"]["wip_area_square_units"] > 0
    assert result["operational_summary"]["flows"]["management_policy"]
    assert result["operational_summary"]["amr_assessment"]["decision"]
    consulting = result["operational_summary"]["consulting_report"]
    assert {item["domain"] for item in consulting["proposals"]} >= {"oee", "scrap", "maintenance", "intralogistics", "safety", "amr"}
    assert all(item["baseline"] and item["target"] and item["actions"] and item["kpis"] for item in consulting["proposals"])
    assert {scenario["id"] for scenario in consulting["scenarios"]} == {"A", "B", "C"}
    assert consulting["evidence_refs"]
    assert "Executive Engineering Report" in result["executive_report"]
    assert result["object_evidence"]
    assert result["trace"]["import"] is not None


def test_connection_search_uses_bounded_spatial_candidates(monkeypatch) -> None:
    interpreter = IndustrialLayoutInterpreter()
    entities = [
        interpreter._build_entity(
            {
                "id": f"machine-{index}",
                "label": f"Machine {index}",
                "layer": "MACHINES",
                "type": "block",
                "center": [index % 100, index // 100],
            },
            index,
        )
        for index in range(5_000)
    ]
    distance_calls = 0
    original_distance = industrial_layout_module._distance

    def counted_distance(a, b):
        nonlocal distance_calls
        distance_calls += 1
        return original_distance(a, b)

    monkeypatch.setattr(industrial_layout_module, "_distance", counted_distance)
    connections = interpreter._build_connections(entities)

    assert connections
    assert distance_calls < len(entities) * 200


def test_dxf_source_path_streams_entities_and_honors_limit(tmp_path, monkeypatch) -> None:
    source_path = tmp_path / "large-layout.dxf"
    records = ["0", "SECTION", "2", "HEADER", "0", "TEXT", "1", "Ignore Header", "0", "ENDSEC"]
    records.extend(["0", "SECTION", "2", "ENTITIES"])
    for index in range(25):
        records.extend(["0", "TEXT", "8", "MACHINES", "1", f"Machine {index}", "10", str(index), "20", "0"])
    records.extend(["0", "ENDSEC", "0", "EOF"])
    source_path.write_text("\n".join(records), encoding="utf-8")

    def fail_read_text(*args, **kwargs):
        raise AssertionError("DXF source_path must be streamed instead of read_text")

    monkeypatch.setattr(type(source_path), "read_text", fail_read_text)
    imported = LayoutImportFramework().import_layout(
        {
            "source_format": "dxf",
            "source_path": str(source_path),
            "layout_name": "streamed-layout",
            "max_entities": 10,
        }
    )

    assert len(imported.model.entities) == 10
    assert imported.model.entities[0].label == "Machine 0"
    assert imported.model.metadata["streaming"] is True
    assert imported.model.metadata["truncated"] is True


def test_dxf_provider_limits_vertices_per_entity(tmp_path) -> None:
    source_path = tmp_path / "dense-polyline.dxf"
    records = ["0", "SECTION", "2", "ENTITIES", "0", "LWPOLYLINE", "8", "FLOW"]
    for index in range(1_000):
        records.extend(["10", str(index), "20", str(index)])
    records.extend(["0", "ENDSEC", "0", "EOF"])
    source_path.write_text("\n".join(records), encoding="utf-8")

    imported = LayoutImportFramework().import_layout(
        {
            "source_format": "dxf",
            "source_path": str(source_path),
            "max_group_values": 32,
        }
    )

    assert len(imported.model.entities) == 1
    assert len(imported.model.entities[0].points) == 32
    assert imported.model.metadata["group_value_limit"] == 32


def test_industrial_intelligence_parser_uses_layout_interpreter() -> None:
    system = CognitiveOperatingSystem()
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
            "CNC 01",
            "10",
            "10",
            "20",
            "10",
            "0",
            "INSERT",
            "8",
            "MACHINES",
            "2",
            "Palletizer",
            "10",
            "18",
            "20",
            "10",
            "0",
            "LINE",
            "8",
            "FLOW",
            "10",
            "12",
            "20",
            "10",
            "11",
            "22",
            "21",
            "10",
            "0",
            "CIRCLE",
            "8",
            "WIP",
            "10",
            "26",
            "20",
            "10",
            "40",
            "2",
            "0",
            "ENDSEC",
            "0",
            "EOF",
        ]
    )

    result = system.industrial_intelligence.execute_component(
        "dxf-intelligence-parser",
        {"source": dxf_text, "source_format": "dxf", "layout_name": "sample-dxf"},
    )

    assert result["parsed_entities"] >= 3
    assert result["factory_graph"]["node_count"] >= 3
    assert result["knowledge_graph"]["fact_count"] >= 3
    assert result["digital_twin"]["nodes"] >= 3
    assert result["simulation"]["production_capacity"] > 0
    assert "plant_state_report" in result
    assert result["version_info"]["revision"]["revision_id"].startswith("rev-")


def test_dwg_parser_accepts_base64_source_with_oda_converter(tmp_path) -> None:
    converter_script = tmp_path / "fake_oda_converter.py"
    converter_script.write_text(
        """
from pathlib import Path
import sys

output_dir = Path(sys.argv[2])
source_name = sys.argv[7]
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / f\"{Path(source_name).stem}.dxf\").write_text(\"\\n\".join([
    \"0\",
    \"SECTION\",
    \"2\",
    \"ENTITIES\",
    \"0\",
    \"TEXT\",
    \"8\",
    \"MACHINES\",
    \"1\",
    \"Robot Cell 01\",
    \"10\",
    \"14\",
    \"20\",
    \"9\",
    \"0\",
    \"ENDSEC\",
    \"0\",
    \"EOF\",
]), encoding=\"utf-8\")
""".strip(),
        encoding="utf-8",
    )

    system = CognitiveOperatingSystem()
    result = system.industrial_intelligence.execute_component(
        "dwg-intelligence-parser",
        {
            "source_format": "dwg",
            "layout_name": "sample-dwg",
            "source_filename": "sample-dwg.dwg",
            "source": "dwg-file:sample-dwg.dwg",
            "source_bytes_b64": base64.b64encode(b"fake-dwg-binary").decode("ascii"),
            "dwg_oda_command": [sys.executable, str(converter_script)],
        },
    )

    assert result["parsed_entities"] >= 1
    assert result["factory_graph"]["node_count"] >= 1
    assert result["version_info"]["revision"]["revision_id"].startswith("rev-")
