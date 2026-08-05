"""Universal pluggable CAD import framework for industrial layouts.

This module decouples source format ingestion from the downstream interpretation
pipeline. Importers emit a vendor-independent intermediate geometry model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
from typing import Any, Protocol


def _hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:12]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_format(raw: str | None) -> str:
    if not raw:
        return "json"
    lowered = raw.strip().lower().lstrip(".")
    aliases = {
        "pdf vector": "pdf_vector",
        "pdf-vector": "pdf_vector",
    }
    return aliases.get(lowered, lowered)


@dataclass(slots=True)
class IntermediateGeometryEntity:
    id: str
    primitive: str
    layer: str
    label: str
    points: list[tuple[float, float]]
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IntermediateGeometryModel:
    model_id: str
    source_format: str
    source_name: str
    entities: list[IntermediateGeometryEntity]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "source_format": self.source_format,
            "source_name": self.source_name,
            "entities": [asdict(item) for item in self.entities],
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ImportAttempt:
    provider_id: str
    status: str
    detail: str


@dataclass(slots=True)
class ImportResult:
    model: IntermediateGeometryModel
    attempts: list[ImportAttempt]
    selected_provider: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model.to_dict(),
            "attempts": [asdict(item) for item in self.attempts],
            "selected_provider": self.selected_provider,
        }


class LayoutProvider(Protocol):
    provider_id: str
    supported_formats: tuple[str, ...]
    priority: int

    def can_handle(self, source_format: str, payload: dict[str, Any]) -> bool:
        ...

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        ...


class BaseLayoutProvider:
    provider_id = "base"
    supported_formats: tuple[str, ...] = tuple()
    priority = 100

    def can_handle(self, source_format: str, payload: dict[str, Any]) -> bool:
        return source_format in self.supported_formats

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        raise NotImplementedError


def _payload_text(payload: dict[str, Any]) -> str:
    source = payload.get("source")
    if isinstance(source, str):
        return source
    if isinstance(source, (bytes, bytearray)):
        return source.decode("utf-8", errors="ignore")
    text = payload.get("text")
    if isinstance(text, str):
        return text
    source_path = payload.get("source_path")
    if source_path:
        path = Path(str(source_path))
        if path.exists():
            return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def _entity_points(entity: dict[str, Any]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for key in ("points", "vertices"):
        raw = entity.get(key)
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    points.append((_safe_float(item.get("x")), _safe_float(item.get("y"))))
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    points.append((_safe_float(item[0]), _safe_float(item[1])))
    for key in ("start", "end", "center", "position"):
        raw = entity.get(key)
        if isinstance(raw, dict):
            points.append((_safe_float(raw.get("x")), _safe_float(raw.get("y"))))
        elif isinstance(raw, (list, tuple)) and len(raw) >= 2:
            points.append((_safe_float(raw[0]), _safe_float(raw[1])))
    if not points:
        points.append((0.0, 0.0))
    return points


class JSONLayoutProvider(BaseLayoutProvider):
    provider_id = "json-layout"
    supported_formats = ("json",)
    priority = 10

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        entities: list[dict[str, Any]] = []
        if isinstance(payload.get("entities"), list):
            entities = [item for item in payload["entities"] if isinstance(item, dict)]
        else:
            text = _payload_text(payload)
            if text:
                decoded = json.loads(text)
                if isinstance(decoded, dict) and isinstance(decoded.get("entities"), list):
                    entities = [item for item in decoded["entities"] if isinstance(item, dict)]
                elif isinstance(decoded, list):
                    entities = [item for item in decoded if isinstance(item, dict)]

        normalized = [
            IntermediateGeometryEntity(
                id=str(item.get("id") or f"json-{idx}-{_hash(json.dumps(item, sort_keys=True, default=str))}"),
                primitive=str(item.get("type") or item.get("primitive") or "entity").lower(),
                layer=str(item.get("layer") or "default"),
                label=str(item.get("label") or item.get("name") or item.get("type") or "entity"),
                points=_entity_points(item),
                properties=dict(item),
            )
            for idx, item in enumerate(entities)
        ]
        source_name = str(payload.get("layout_name") or payload.get("name") or "layout-json")
        return IntermediateGeometryModel(
            model_id=f"igm-{_hash(source_name + str(len(normalized)))}",
            source_format="json",
            source_name=source_name,
            entities=normalized,
            metadata={"provider": self.provider_id},
        )


class DXFLayoutProvider(BaseLayoutProvider):
    provider_id = "dxf-native"
    supported_formats = ("dxf",)
    priority = 10

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        text = _payload_text(payload)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        pairs: list[tuple[str, str]] = []
        index = 0
        while index + 1 < len(lines):
            pairs.append((lines[index], lines[index + 1]))
            index += 2

        entities: list[IntermediateGeometryEntity] = []
        current_type: str | None = None
        current: dict[str, list[str]] = {}
        for code, value in pairs:
            if code == "0":
                if current_type is not None:
                    entities.append(self._entity_from_record(current_type, current, len(entities)))
                current_type = value.upper()
                current = {}
                continue
            current.setdefault(code, []).append(value)
        if current_type is not None:
            entities.append(self._entity_from_record(current_type, current, len(entities)))

        source_name = str(payload.get("layout_name") or payload.get("name") or "layout-dxf")
        return IntermediateGeometryModel(
            model_id=f"igm-{_hash(source_name + str(len(entities)))}",
            source_format="dxf",
            source_name=source_name,
            entities=entities,
            metadata={"provider": self.provider_id},
        )

    def _entity_from_record(
        self,
        entity_type: str,
        fields: dict[str, list[str]],
        index: int,
    ) -> IntermediateGeometryEntity:
        layer = fields.get("8", ["default"])[0]
        label = fields.get("1", [""])[0] or fields.get("2", [""])[0] or entity_type
        points: list[tuple[float, float]] = []
        xs = fields.get("10", [])
        ys = fields.get("20", [])
        for idx, x_val in enumerate(xs):
            y_val = ys[idx] if idx < len(ys) else ys[-1] if ys else "0"
            points.append((_safe_float(x_val), _safe_float(y_val)))
        x2s = fields.get("11", [])
        y2s = fields.get("21", [])
        for idx, x_val in enumerate(x2s):
            y_val = y2s[idx] if idx < len(y2s) else y2s[-1] if y2s else "0"
            points.append((_safe_float(x_val), _safe_float(y_val)))
        if not points:
            points.append((0.0, 0.0))

        entity_id = f"dxf-{index}-{_hash(f'{entity_type}|{layer}|{label}|{points[0]}')}"
        return IntermediateGeometryEntity(
            id=entity_id,
            primitive=entity_type.lower(),
            layer=layer,
            label=label,
            points=points,
            properties={"dxf_fields": fields},
        )


class ExternalCommandProvider(BaseLayoutProvider):
    """Generic converter provider for non-native formats."""

    command_config_key = ""
    output_format = "json"

    def can_handle(self, source_format: str, payload: dict[str, Any]) -> bool:
        if source_format not in self.supported_formats:
            return False
        command = payload.get(self.command_config_key)
        if not command:
            return False
        return self._command_available(command)

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        command = payload.get(self.command_config_key)
        if not command:
            raise ValueError(f"missing converter command for provider {self.provider_id}")

        completed = self._run_command(command)
        output_text = completed.stdout.strip()
        if not output_text:
            raise ValueError(f"provider {self.provider_id} returned empty output")

        converted_payload = dict(payload)
        converted_payload["source"] = output_text
        if self.output_format == "dxf":
            return DXFLayoutProvider().import_layout("dxf", converted_payload)
        return JSONLayoutProvider().import_layout("json", converted_payload)

    def _command_available(self, command: Any) -> bool:
        if isinstance(command, str):
            parts = shlex.split(command)
            executable = parts[0] if parts else ""
        elif isinstance(command, (list, tuple)) and command:
            executable = str(command[0])
        else:
            return False
        if Path(executable).exists():
            return True
        return shutil.which(executable) is not None

    def _run_command(self, command: Any) -> subprocess.CompletedProcess[str]:
        if isinstance(command, str):
            return subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
        return subprocess.run(list(command), check=True, capture_output=True, text=True, shell=False)


class DWGOdaProvider(ExternalCommandProvider):
    provider_id = "dwg-oda"
    supported_formats = ("dwg",)
    priority = 10
    command_config_key = "dwg_oda_command"
    output_format = "dxf"


class DWGRealDwgProvider(ExternalCommandProvider):
    provider_id = "dwg-realdwg"
    supported_formats = ("dwg",)
    priority = 20
    command_config_key = "dwg_realdwg_command"
    output_format = "dxf"


class DWGLibreDwgProvider(ExternalCommandProvider):
    provider_id = "dwg-libredwg"
    supported_formats = ("dwg",)
    priority = 30
    command_config_key = "dwg_libredwg_command"
    output_format = "dxf"


class DWGExternalProvider(ExternalCommandProvider):
    provider_id = "dwg-external"
    supported_formats = ("dwg",)
    priority = 40
    command_config_key = "dwg_external_command"
    output_format = "dxf"


class DWGDXFIntermediaryProvider(BaseLayoutProvider):
    provider_id = "dwg-dxf-intermediary"
    supported_formats = ("dwg",)
    priority = 50

    def can_handle(self, source_format: str, payload: dict[str, Any]) -> bool:
        if source_format != "dwg":
            return False
        if isinstance(payload.get("dxf_intermediary"), str) and payload.get("dxf_intermediary", "").strip():
            return True
        intermediary_path = payload.get("dxf_intermediary_path")
        if intermediary_path and Path(str(intermediary_path)).exists():
            return True
        return False

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        text = payload.get("dxf_intermediary")
        if not text:
            text = Path(str(payload["dxf_intermediary_path"])).read_text(encoding="utf-8", errors="ignore")
        dxf_payload = dict(payload)
        dxf_payload["source"] = text
        return DXFLayoutProvider().import_layout("dxf", dxf_payload)


class GenericExternalFormatProvider(ExternalCommandProvider):
    def __init__(self, provider_id: str, source_format: str, command_key: str, priority: int = 60) -> None:
        self.provider_id = provider_id
        self.supported_formats = (source_format,)
        self.command_config_key = command_key
        self.priority = priority
        self.output_format = "json"


class LayoutImportFramework:
    """Registry-driven import framework with discovery and failover."""

    def __init__(self) -> None:
        self._providers: list[LayoutProvider] = []
        self._register_defaults()

    def register_provider(self, provider: LayoutProvider) -> None:
        self._providers.append(provider)
        self._providers.sort(key=lambda item: item.priority)

    def import_layout(self, payload: dict[str, Any]) -> ImportResult:
        source_format = self._detect_format(payload)
        attempts: list[ImportAttempt] = []

        candidates = [
            provider
            for provider in self._providers
            if provider.can_handle(source_format, payload)
        ]
        if not candidates:
            raise ValueError(f"no provider available for source format '{source_format}'")

        for provider in candidates:
            try:
                model = provider.import_layout(source_format, payload)
                attempts.append(ImportAttempt(provider_id=provider.provider_id, status="success", detail="imported"))
                model.metadata = {
                    **model.metadata,
                    "source_format": source_format,
                    "provider_attempts": [asdict(item) for item in attempts],
                }
                return ImportResult(model=model, attempts=attempts, selected_provider=provider.provider_id)
            except Exception as exc:  # pragma: no cover - safety fallback path
                attempts.append(ImportAttempt(provider_id=provider.provider_id, status="failed", detail=str(exc)))

        details = " | ".join(f"{item.provider_id}:{item.detail}" for item in attempts)
        raise RuntimeError(f"all providers failed for format '{source_format}': {details}")

    def discover_available_providers(self, payload: dict[str, Any]) -> list[str]:
        source_format = self._detect_format(payload)
        return [provider.provider_id for provider in self._providers if provider.can_handle(source_format, payload)]

    def _detect_format(self, payload: dict[str, Any]) -> str:
        explicit = _normalize_format(str(payload.get("source_format") or payload.get("format") or ""))
        if explicit and explicit != "json":
            return explicit

        source_path = payload.get("source_path")
        if source_path:
            suffix = Path(str(source_path)).suffix.lstrip(".")
            if suffix:
                return _normalize_format(suffix)

        text = _payload_text(payload)
        if text.startswith("{") or text.startswith("["):
            return "json"
        if "SECTION" in text or "ENTITIES" in text or re.search(r"^0\s*$", text, flags=re.MULTILINE):
            return "dxf"
        return explicit or "json"

    def _register_defaults(self) -> None:
        self.register_provider(JSONLayoutProvider())
        self.register_provider(DXFLayoutProvider())

        self.register_provider(DWGOdaProvider())
        self.register_provider(DWGRealDwgProvider())
        self.register_provider(DWGLibreDwgProvider())
        self.register_provider(DWGExternalProvider())
        self.register_provider(DWGDXFIntermediaryProvider())

        self.register_provider(GenericExternalFormatProvider("dgn-external", "dgn", "dgn_converter_command"))
        self.register_provider(GenericExternalFormatProvider("ifc-external", "ifc", "ifc_converter_command"))
        self.register_provider(GenericExternalFormatProvider("step-external", "step", "step_converter_command"))
        self.register_provider(GenericExternalFormatProvider("svg-external", "svg", "svg_converter_command"))
        self.register_provider(GenericExternalFormatProvider("pdf-vector-external", "pdf_vector", "pdf_vector_converter_command"))


def import_layout_universal(payload: dict[str, Any]) -> dict[str, Any]:
    return LayoutImportFramework().import_layout(payload).to_dict()
