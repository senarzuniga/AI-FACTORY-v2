from __future__ import annotations

import base64
import sys

from cognitive_os import IndustrialLayoutInterpreter
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
    assert "Executive Engineering Report" in result["executive_report"]
    assert result["object_evidence"]
    assert result["trace"]["import"] is not None


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
