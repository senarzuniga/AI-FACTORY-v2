"""Universal pluggable CAD import framework for industrial layouts.

This module decouples source format ingestion from the downstream interpretation
pipeline. Importers emit a vendor-independent intermediate geometry model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import base64
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
from typing import Any, Iterator, Protocol


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


def _payload_bytes(payload: dict[str, Any]) -> bytes:
    source = payload.get("source")
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)

    for key in ("source_bytes", "source_bytes_b64", "source_base64"):
        raw = payload.get(key)
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw)
        if isinstance(raw, str) and raw.strip():
            try:
                return base64.b64decode(raw)
            except Exception:
                continue
    return b""


def _payload_line_pairs(payload: dict[str, Any]) -> Iterator[tuple[str, str]]:
    source_path = payload.get("source_path")
    if source_path:
        path = Path(str(source_path))
        if path.is_file():
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                while True:
                    code = handle.readline()
                    if not code:
                        return
                    value = handle.readline()
                    if not value:
                        return
                    yield code.strip(), value.strip()
            return

    lines = iter(_payload_text(payload).splitlines())
    while True:
        try:
            code = next(lines)
            value = next(lines)
        except StopIteration:
            return
        yield code.strip(), value.strip()


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
    relevant_group_codes = frozenset({"1", "2", "8", "10", "20", "11", "21"})

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        max_entities = max(1, int(payload.get("max_entities") or 100_000))
        max_group_values = max(1, int(payload.get("max_group_values") or 256))
        entities: list[IntermediateGeometryEntity] = []
        in_entities_section = False
        awaiting_section_name = False
        truncated = False
        current_type: str | None = None
        current: dict[str, list[str]] = {}
        for code, value in _payload_line_pairs(payload):
            if code == "0":
                if in_entities_section and current_type is not None:
                    entities.append(self._entity_from_record(current_type, current, len(entities)))
                    if len(entities) >= max_entities:
                        truncated = True
                        break

                record_type = value.upper()
                current_type = None
                current = {}
                if record_type == "SECTION":
                    awaiting_section_name = True
                elif record_type == "ENDSEC":
                    in_entities_section = False
                    awaiting_section_name = False
                elif in_entities_section:
                    current_type = record_type
                continue
            if awaiting_section_name and code == "2":
                in_entities_section = value.upper() == "ENTITIES"
                awaiting_section_name = False
                continue
            if in_entities_section and current_type is not None and code in self.relevant_group_codes:
                values = current.setdefault(code, [])
                if len(values) < max_group_values:
                    values.append(value)
        if not truncated and in_entities_section and current_type is not None and len(entities) < max_entities:
            entities.append(self._entity_from_record(current_type, current, len(entities)))

        source_name = str(payload.get("layout_name") or payload.get("name") or "layout-dxf")
        return IntermediateGeometryModel(
            model_id=f"igm-{_hash(source_name + str(len(entities)))}",
            source_format="dxf",
            source_name=source_name,
            entities=entities,
            metadata={
                "provider": self.provider_id,
                "streaming": bool(payload.get("source_path")),
                "entity_limit": max_entities,
                "group_value_limit": max_group_values,
                "truncated": truncated,
            },
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
            properties={},
        )


class ExternalCommandProvider(BaseLayoutProvider):
    """Generic converter provider for non-native formats."""

    command_config_key = ""
    output_format = "json"
    command_env_keys: tuple[str, ...] = tuple()
    command_candidates: tuple[str, ...] = tuple()

    def can_handle(self, source_format: str, payload: dict[str, Any]) -> bool:
        if source_format not in self.supported_formats:
            return False
        return self._resolve_command(payload) is not None

    def import_layout(self, source_format: str, payload: dict[str, Any]) -> IntermediateGeometryModel:
        command = self._resolve_command(payload)
        if not command:
            raise ValueError(f"missing converter command for provider {self.provider_id}")

        output_text = self._convert_payload(command, source_format, payload).strip()
        if not output_text:
            raise ValueError(f"provider {self.provider_id} returned empty output")

        converted_payload = dict(payload)
        converted_payload["source"] = output_text
        if self.output_format == "dxf":
            return DXFLayoutProvider().import_layout("dxf", converted_payload)
        return JSONLayoutProvider().import_layout("json", converted_payload)

    def _resolve_command(self, payload: dict[str, Any]) -> Any | None:
        command = payload.get(self.command_config_key)
        if command and self._command_available(command):
            return command

        for env_key in self.command_env_keys:
            env_command = os.environ.get(env_key)
            if env_command and self._command_available(env_command):
                return env_command

        for candidate in self.command_candidates:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved

        for discovered in self._discover_install_paths():
            if self._command_available(discovered):
                return discovered
        return None

    def _discover_install_paths(self) -> list[str]:
        return []

    def _convert_payload(self, command: Any, source_format: str, payload: dict[str, Any]) -> str:
        completed = self._run_command(command)
        return completed.stdout.strip()

    def _materialize_source_file(self, payload: dict[str, Any], suffix: str) -> Path:
        source_path = payload.get("source_path")
        if source_path:
            path = Path(str(source_path))
            if path.exists():
                return path

        source_bytes = _payload_bytes(payload)
        if not source_bytes:
            raise ValueError(f"provider {self.provider_id} requires source_path or source_bytes_b64 for {suffix} conversion")

        source_name = str(payload.get("source_filename") or payload.get("layout_name") or f"layout{suffix}")
        extension = Path(source_name).suffix or suffix
        temp_dir = Path(tempfile.mkdtemp(prefix=f"{self.provider_id}-src-"))
        temp_path = temp_dir / f"source{extension}"
        temp_path.write_bytes(source_bytes)
        return temp_path

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
    command_env_keys = ("DWG_ODA_COMMAND", "ODA_FILE_CONVERTER")
    command_candidates = ("ODAFileConverter", "TeighaFileConverter")
    output_format = "dxf"

    def _discover_install_paths(self) -> list[str]:
        candidates: list[str] = []
        for root_key in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData"):
            root = os.environ.get(root_key)
            if not root:
                continue
            base = Path(root)
            patterns = [
                "ODA/ODAFileConverter*/ODAFileConverter.exe",
                "ODA/ODAFileConverter*/TeighaFileConverter.exe",
                "Open Design Alliance/*/ODAFileConverter.exe",
                "Open Design Alliance/*/TeighaFileConverter.exe",
            ]
            for pattern in patterns:
                candidates.extend(str(path) for path in base.glob(pattern))
        return candidates

    def _convert_payload(self, command: Any, source_format: str, payload: dict[str, Any]) -> str:
        source_path = self._materialize_source_file(payload, ".dwg")
        source_name = str(payload.get("source_filename") or source_path.name)
        working_dir = Path(tempfile.mkdtemp(prefix="dwg-oda-"))
        input_dir = working_dir / "input"
        output_dir = working_dir / "output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        staged_input = input_dir / Path(source_name).name
        staged_input.write_bytes(source_path.read_bytes())
        command_parts = [
            *self._command_parts(command),
            str(input_dir),
            str(output_dir),
            "ACAD2018",
            "DXF",
            "0",
            "1",
            staged_input.name,
        ]
        self._run_command(command_parts)

        dxf_files = sorted(output_dir.rglob("*.dxf"))
        if not dxf_files:
            raise ValueError(f"provider {self.provider_id} did not produce a DXF output file")
        return dxf_files[0].read_text(encoding="utf-8", errors="ignore")

    def _command_parts(self, command: Any) -> list[str]:
        if isinstance(command, str):
            return shlex.split(command)
        return [str(part) for part in command]


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
    command_env_keys = ("DWG_LIBREDWG_COMMAND", "LIBREDWG_DWG2DXF_COMMAND")
    command_candidates = ("dwg2dxf",)
    output_format = "dxf"

    def _convert_payload(self, command: Any, source_format: str, payload: dict[str, Any]) -> str:
        source_path = self._materialize_source_file(payload, ".dwg")
        working_dir = Path(tempfile.mkdtemp(prefix="dwg-libredwg-"))
        output_path = working_dir / f"{source_path.stem}.dxf"
        command_parts = [*self._command_parts(command), str(source_path), "-o", str(output_path)]
        self._run_command(command_parts)
        if not output_path.exists():
            raise ValueError(f"provider {self.provider_id} did not produce {output_path.name}")
        return output_path.read_text(encoding="utf-8", errors="ignore")

    def _command_parts(self, command: Any) -> list[str]:
        if isinstance(command, str):
            return shlex.split(command)
        return [str(part) for part in command]


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
