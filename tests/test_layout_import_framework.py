from __future__ import annotations

import base64
import sys

from cognitive_os.layout_import_framework import BaseLayoutProvider, IntermediateGeometryModel, LayoutImportFramework


class _FailingDWGProvider(BaseLayoutProvider):
    provider_id = "dwg-failing"
    supported_formats = ("dwg",)
    priority = 1

    def import_layout(self, source_format: str, payload: dict):
        raise RuntimeError("intentional failure")


class _FallbackDWGProvider(BaseLayoutProvider):
    provider_id = "dwg-fallback"
    supported_formats = ("dwg",)
    priority = 2

    def can_handle(self, source_format: str, payload: dict) -> bool:
        return source_format == "dwg" and bool(payload.get("dxf_intermediary"))

    def import_layout(self, source_format: str, payload: dict) -> IntermediateGeometryModel:
        return LayoutImportFramework().import_layout(
            {
                "source_format": "dxf",
                "source": payload["dxf_intermediary"],
                "layout_name": payload.get("layout_name", "fallback-layout"),
            }
        ).model


def test_universal_import_framework_dwg_failover() -> None:
    framework = LayoutImportFramework()
    framework.register_provider(_FailingDWGProvider())
    framework.register_provider(_FallbackDWGProvider())

    payload = {
        "source_format": "dwg",
        "layout_name": "dwg-failover-layout",
        "dxf_intermediary": "\n".join(
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
                "M-01",
                "10",
                "10",
                "20",
                "10",
                "0",
                "ENDSEC",
                "0",
                "EOF",
            ]
        ),
    }

    result = framework.import_layout(payload)

    assert result.selected_provider in {"dwg-fallback", "dwg-dxf-intermediary"}
    assert any(attempt.provider_id == "dwg-failing" and attempt.status == "failed" for attempt in result.attempts)
    assert result.model.entities


def test_universal_import_framework_dwg_oda_file_conversion(tmp_path) -> None:
    converter_script = tmp_path / "fake_oda_converter.py"
    converter_script.write_text(
        """
from pathlib import Path
import sys

input_dir = Path(sys.argv[1])
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
    \"M-02\",
    \"10\",
    \"12\",
    \"20\",
    \"8\",
    \"0\",
    \"ENDSEC\",
    \"0\",
    \"EOF\",
]), encoding=\"utf-8\")
""".strip(),
        encoding="utf-8",
    )

    framework = LayoutImportFramework()
    result = framework.import_layout(
        {
            "source_format": "dwg",
            "layout_name": "converted-layout",
            "source_filename": "converted-layout.dwg",
            "source_bytes_b64": base64.b64encode(b"fake-dwg-binary").decode("ascii"),
            "dwg_oda_command": [sys.executable, str(converter_script)],
        }
    )

    assert result.selected_provider == "dwg-oda"
    assert len(result.model.entities) >= 1
