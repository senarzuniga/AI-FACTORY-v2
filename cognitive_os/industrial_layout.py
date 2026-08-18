"""Industrial layout interpretation pipeline for DWG/DXF-like inputs.

The service accepts normalized layout payloads or DXF text and produces a
factory graph, semantic knowledge bundle, digital twin snapshot, simulation
baseline, and engineering analysis. The implementation is intentionally
dependency-light so it can run inside the existing Cognitive OS stack without
requiring external CAD tooling.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from collections import defaultdict
from bisect import bisect_left
from functools import lru_cache
from hashlib import sha256
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

from cognitive_os.layout_import_framework import LayoutImportFramework


Point = tuple[float, float]
KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1] / "knowledge" / "corrugated_equipment"


def _utc_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:12]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _point_from_any(value: Any) -> Point:
    if isinstance(value, dict):
        x = value.get("x", value.get("X", 0.0))
        y = value.get("y", value.get("Y", 0.0))
        return (_safe_float(x), _safe_float(y))
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return (_safe_float(value[0]), _safe_float(value[1]))
    return (0.0, 0.0)


def _points_from_entity(entity: dict[str, Any]) -> list[Point]:
    points: list[Point] = []
    if isinstance(entity.get("points"), list):
        points.extend(_point_from_any(item) for item in entity["points"])
    if isinstance(entity.get("vertices"), list):
        points.extend(_point_from_any(item) for item in entity["vertices"])

    for key in ("start", "end", "center", "location", "anchor", "position"):
        if key in entity:
            points.append(_point_from_any(entity[key]))

    if "bounds" in entity and isinstance(entity["bounds"], (list, tuple)) and len(entity["bounds"]) >= 4:
        x1, y1, x2, y2 = entity["bounds"][:4]
        points.extend([(_safe_float(x1), _safe_float(y1)), (_safe_float(x2), _safe_float(y2))])

    return points or [(0.0, 0.0)]


def _bounding_box(points: Iterable[Point]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _center(points: Iterable[Point]) -> Point:
    coords = list(points)
    if not coords:
        return (0.0, 0.0)
    return (
        round(sum(point[0] for point in coords) / len(coords), 3),
        round(sum(point[1] for point in coords) / len(coords), 3),
    )


def _distance(a: Point, b: Point) -> float:
    return round(math.dist(a, b), 3)


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


@lru_cache(maxsize=1)
def _load_consulting_benchmarks() -> dict[str, Any]:
    catalog_path = KNOWLEDGE_ROOT / "converter_equipment_catalog_v1.json"
    hypotheses_path = KNOWLEDGE_ROOT / "simulation_hypotheses_corrugated_v1.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        hypotheses = json.loads(hypotheses_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"catalog": {}, "hypotheses": {}, "evidence": []}
    return {
        "catalog": catalog,
        "hypotheses": hypotheses,
        "evidence": [
            "knowledge/corrugated_equipment/converter_equipment_catalog_v1.json",
            "knowledge/corrugated_equipment/simulation_hypotheses_corrugated_v1.json",
        ],
    }


@dataclass(slots=True)
class LayoutEntity:
    id: str
    kind: str
    label: str
    layer: str
    center: Point
    bounds: tuple[float, float, float, float]
    confidence: float
    source_type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LayoutConnection:
    source: str
    target: str
    relation: str
    distance: float
    confidence: float
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KnowledgeAssertion:
    subject: str
    predicate: str
    object: str
    confidence: float
    source: str


@dataclass(slots=True)
class DigitalTwinSnapshot:
    version: str
    layout_name: str
    live_sync: bool
    nodes: int
    edges: int
    scenarios: list[str]
    simulation_inputs: dict[str, Any]
    state: dict[str, Any]


@dataclass(slots=True)
class SimulationResult:
    material_flow: dict[str, Any]
    amr_routing: dict[str, Any]
    travel_distance: float
    production_capacity: float
    oee: float
    roi: float
    bottlenecks: list[dict[str, Any]]
    buffer_occupancy: dict[str, Any]
    warehouse_capacity: dict[str, Any]
    cycle_times: dict[str, Any]


@dataclass(slots=True)
class EngineeringAnalysis:
    layout_quality: dict[str, Any]
    flow_analysis: dict[str, Any]
    constraint_analysis: dict[str, Any]
    amr_recommendations: list[str]
    warehouse_optimisation: list[str]
    production_optimisation: list[str]
    risk_analysis: list[str]
    safety_analysis: list[str]
    executive_recommendations: list[str]


@dataclass(slots=True)
class LayoutInterpretationResult:
    layout_name: str
    source_format: str
    source_hash: str
    entities: list[LayoutEntity]
    connections: list[LayoutConnection]
    factory_graph: dict[str, Any]
    knowledge_graph: dict[str, Any]
    digital_twin: DigitalTwinSnapshot
    simulation: SimulationResult
    engineering_analysis: EngineeringAnalysis
    plant_state_report: dict[str, Any]
    operational_summary: dict[str, Any]
    executive_report: str
    confidence: float
    trace: dict[str, Any]
    object_evidence: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "layout_name": self.layout_name,
            "source_format": self.source_format,
            "source_hash": self.source_hash,
            "entities": [asdict(item) for item in self.entities],
            "connections": [asdict(item) for item in self.connections],
            "factory_graph": self.factory_graph,
            "knowledge_graph": self.knowledge_graph,
            "digital_twin": asdict(self.digital_twin),
            "simulation": asdict(self.simulation),
            "engineering_analysis": asdict(self.engineering_analysis),
            "plant_state_report": self.plant_state_report,
            "operational_summary": self.operational_summary,
            "executive_report": self.executive_report,
            "confidence": self.confidence,
            "trace": self.trace,
            "object_evidence": self.object_evidence,
        }


class IndustrialLayoutInterpreter:
    """Convert industrial layouts into graph, twin, and analysis artifacts."""

    ENTITY_MARKERS: dict[str, list[str]] = {
        "machine": ["machine", "cnc", "press", "robot", "welder", "assembler", "palletizer", "station"],
        "conveyor": ["conveyor", "belt", "roller", "infeed", "outfeed", "transport"],
        "transfer": ["transfer", "turntable", "lift table", "shuttle", "cross transfer"],
        "waste_line": ["waste", "scrap", "trim", "broke", "reject line"],
        "warehouse": ["warehouse", "storage", "rack", "aisle", "shelf", "stock"],
        "wip": ["wip", "buffer", "queue", "staging", "accumulation"],
        "safety_zone": ["safety", "restricted", "hazard", "no-go", "exclusion"],
        "amr_route": ["amr", "agv", "route", "lane", "path"],
        "production_area": ["production", "cell", "line", "area", "cellular"],
        "storage_area": ["storage area", "storage_zone", "warehouse area"],
        "logistic_route": ["logistic", "route", "forklift", "aisle", "corridor"],
        "utility": ["utility", "electric", "power", "air", "water", "gas", "vacuum"],
        "operator": ["operator", "manual", "workstation", "human"],
        "process": ["process", "operation", "step", "workflow"],
    }

    RELATION_RULES: list[tuple[str, str, str]] = [
        ("machine", "conveyor", "feeds"),
        ("conveyor", "machine", "feeds"),
        ("machine", "buffer", "queues_to"),
        ("buffer", "machine", "buffers_for"),
        ("warehouse", "conveyor", "dispatches_to"),
        ("conveyor", "warehouse", "supplies"),
        ("amr_route", "machine", "serves"),
        ("amr_route", "buffer", "serves"),
        ("amr_route", "warehouse", "serves"),
        ("safety_zone", "machine", "governs"),
        ("safety_zone", "conveyor", "governs"),
        ("utility", "machine", "supplies"),
        ("operator", "machine", "operates"),
        ("process", "machine", "transforms"),
    ]

    def __init__(self) -> None:
        self._import_framework = LayoutImportFramework()

    def interpret(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._interpret_payload(payload)
        return result.to_dict()

    def _interpret_payload(self, payload: dict[str, Any]) -> LayoutInterpretationResult:
        import_summary = self._import_universal(payload)
        if import_summary is not None and isinstance(import_summary, dict) and "model" in import_summary:
            model = import_summary["model"]
            source_format = str(model.get("source_format", "json"))
            layout_name = _normalize_text(payload.get("layout_name") or model.get("source_name") or "industrial-layout")
            source_hash = _utc_hash(json.dumps(model, sort_keys=True, default=str))
            raw_entities = self._entities_from_intermediate(model.get("entities", []))
        else:
            layout_source = self._extract_layout_source(payload)
            source_format = self._detect_source_format(payload, layout_source)
            layout_name = _normalize_text(payload.get("layout_name") or payload.get("name") or layout_source.get("name") or "industrial-layout")
            source_hash = _utc_hash(json.dumps(layout_source, sort_keys=True, default=str))
            raw_entities = self._normalize_entities(layout_source, source_format)

        entities = [self._build_entity(item, index=index) for index, item in enumerate(raw_entities)]
        connections = self._build_connections(entities)
        factory_graph = self._build_factory_graph(layout_name, entities, connections, source_format, source_hash)
        knowledge_graph = self._build_knowledge_graph(layout_name, entities, connections, source_format)
        digital_twin = self._build_digital_twin(layout_name, entities, connections, source_hash)
        simulation = self._build_simulation(entities, connections, knowledge_graph)
        analysis = self._build_engineering_analysis(entities, connections, factory_graph, simulation)
        plant_state_report = self._build_plant_state_report(factory_graph, simulation, analysis)
        operational_summary = self._build_operational_summary(entities, connections, factory_graph, simulation, analysis)
        executive_report = self._build_executive_report(
            layout_name,
            factory_graph,
            knowledge_graph,
            simulation,
            analysis,
            plant_state_report,
        )
        confidence = round(self._confidence_score(entities, connections, knowledge_graph), 4)
        object_evidence = self._build_object_evidence(layout_name, source_format, entities)

        trace = {
            "source_format": source_format,
            "layout_name": layout_name,
            "entity_count": len(entities),
            "connection_count": len(connections),
            "hypotheses": self._ahde_hypotheses(raw_entities, entities),
            "selected_hypothesis": self._select_hypothesis(raw_entities, entities),
            "selected_rules": self._selected_rules(entities),
            "import": import_summary,
        }

        return LayoutInterpretationResult(
            layout_name=layout_name,
            source_format=source_format,
            source_hash=source_hash,
            entities=entities,
            connections=connections,
            factory_graph=factory_graph,
            knowledge_graph=knowledge_graph,
            digital_twin=digital_twin,
            simulation=simulation,
            engineering_analysis=analysis,
            plant_state_report=plant_state_report,
            operational_summary=operational_summary,
            executive_report=executive_report,
            confidence=confidence,
            trace=trace,
            object_evidence=object_evidence,
        )

    def _import_universal(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        try:
            result = self._import_framework.import_layout(payload)
            return result.to_dict()
        except Exception as exc:
            return {
                "status": "fallback",
                "reason": str(exc),
                "available_providers": self._import_framework.discover_available_providers(payload),
            }

    def _entities_from_intermediate(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in entities:
            if not isinstance(item, dict):
                continue
            points = item.get("points") if isinstance(item.get("points"), list) else []
            properties = item.get("properties", {}) if isinstance(item.get("properties"), dict) else {}
            normalized.append(
                {
                    "id": item.get("id"),
                    "type": item.get("primitive", "entity"),
                    "label": item.get("label", "entity"),
                    "layer": item.get("layer", "default"),
                    "points": points,
                    "center": properties.get("center"),
                    "bounds": properties.get("bounds"),
                    "properties": properties,
                }
            )
        return normalized

    def _extract_layout_source(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "layout" in payload and isinstance(payload["layout"], dict):
            return dict(payload["layout"])
        if "source" in payload and isinstance(payload["source"], dict):
            return dict(payload["source"])
        if "source_path" in payload and payload["source_path"]:
            return self._load_source_path(payload)
        if isinstance(payload.get("entities"), list):
            return {
                "entities": list(payload["entities"]),
                "name": payload.get("layout_name") or payload.get("name") or "industrial-layout",
            }
        source = payload.get("source")
        if isinstance(source, str):
            return {
                "text": source,
                "name": payload.get("layout_name") or payload.get("name") or "industrial-layout",
            }
        if isinstance(source, (bytes, bytearray)):
            return {
                "text": source.decode("utf-8", errors="ignore"),
                "name": payload.get("layout_name") or payload.get("name") or "industrial-layout",
            }
        if isinstance(payload, dict):
            return dict(payload)
        raise ValueError("layout payload must include source text, entities, or a layout contract")

    def _load_source_path(self, payload: dict[str, Any]) -> dict[str, Any]:
        source_path = Path(str(payload["source_path"]))
        if not source_path.exists():
            raise FileNotFoundError(f"layout source path does not exist: {source_path}")

        suffix = source_path.suffix.lower()
        if suffix in {".json", ".txt", ".dxf"}:
            return {
                "text": source_path.read_text(encoding="utf-8", errors="ignore"),
                "name": payload.get("layout_name") or source_path.stem,
                "source_path": str(source_path),
                "source_format": suffix.removeprefix("."),
            }

        if suffix == ".dwg":
            conversion = payload.get("dwg_converter_command") or os.environ.get("DWG_CONVERTER_COMMAND")
            if not conversion:
                raise ValueError(
                    "DWG source provided without a converter command; set dwg_converter_command or DWG_CONVERTER_COMMAND"
                )

            if isinstance(conversion, str):
                completed = subprocess.run(
                    conversion,
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=True,
                )
            else:
                completed = subprocess.run(
                    list(conversion),
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=False,
                )

            converted_text = completed.stdout.strip()
            if not converted_text:
                raise ValueError("DWG converter command did not return DXF/JSON text on stdout")

            return {
                "text": converted_text,
                "name": payload.get("layout_name") or source_path.stem,
                "source_path": str(source_path),
                "source_format": "dxf",
                "conversion": {
                    "converter_command": conversion,
                    "source_suffix": ".dwg",
                },
            }

        return {
            "text": source_path.read_text(encoding="utf-8", errors="ignore"),
            "name": payload.get("layout_name") or source_path.stem,
            "source_path": str(source_path),
            "source_format": suffix.removeprefix(".") if suffix else "txt",
        }

    def _detect_source_format(self, payload: dict[str, Any], layout_source: dict[str, Any]) -> str:
        explicit = _normalize_text(payload.get("source_format") or layout_source.get("source_format") or payload.get("format"))
        if explicit:
            return explicit.lower()
        text = _normalize_text(layout_source.get("text") or layout_source.get("source") or "")
        if text.startswith("{") or text.startswith("["):
            return "json"
        if "SECTION" in text or "ENTITIES" in text or re.search(r"^0\s*$", text, flags=re.MULTILINE):
            return "dxf"
        return "json"

    def _normalize_entities(self, layout_source: dict[str, Any], source_format: str) -> list[dict[str, Any]]:
        if isinstance(layout_source.get("entities"), list):
            return [dict(entity) for entity in layout_source["entities"] if isinstance(entity, dict)]

        text = _normalize_text(layout_source.get("text") or layout_source.get("source") or "")
        if not text:
            return []

        if source_format == "json":
            try:
                decoded = json.loads(text)
            except json.JSONDecodeError:
                return []
            if isinstance(decoded, dict) and isinstance(decoded.get("entities"), list):
                return [dict(entity) for entity in decoded["entities"] if isinstance(entity, dict)]
            if isinstance(decoded, list):
                return [dict(entity) for entity in decoded if isinstance(entity, dict)]
            return []

        return self._parse_dxf_entities(text)

    def _parse_dxf_entities(self, text: str) -> list[dict[str, Any]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) < 2:
            return []

        pairs: list[tuple[str, str]] = []
        index = 0
        while index + 1 < len(lines):
            pairs.append((lines[index], lines[index + 1]))
            index += 2

        entities: list[dict[str, Any]] = []
        current_type: str | None = None
        current: dict[str, list[str]] = {}

        for code, value in pairs:
            if code == "0":
                if current_type is not None:
                    entities.append(self._dxf_record_to_entity(current_type, current, len(entities)))
                current_type = value.upper()
                current = {}
                continue
            current.setdefault(code, []).append(value)

        if current_type is not None:
            entities.append(self._dxf_record_to_entity(current_type, current, len(entities)))

        return entities

    def _dxf_record_to_entity(self, entity_type: str, fields: dict[str, list[str]], index: int) -> dict[str, Any]:
        layer = fields.get("8", [""])[0]
        label = fields.get("1", [""])[0] or fields.get("2", [""])[0] or entity_type
        block_name = fields.get("2", [""])[0]
        points = self._collect_dxf_points(fields)
        bounds = _bounding_box(points)
        center = _center(points)
        entity_id = f"dxf-{index}-{_utc_hash(f'{entity_type}|{layer}|{label}|{center}') }"
        return {
            "id": entity_id,
            "type": entity_type,
            "label": label,
            "layer": layer,
            "block_name": block_name,
            "center": center,
            "bounds": bounds,
            "points": points,
            "properties": {"dxf_fields": fields},
        }

    def _collect_dxf_points(self, fields: dict[str, list[str]]) -> list[Point]:
        coords: list[Point] = []
        xs = fields.get("10", [])
        ys = fields.get("20", [])
        for index, x_value in enumerate(xs):
            y_value = ys[index] if index < len(ys) else ys[-1] if ys else "0"
            coords.append((_safe_float(x_value), _safe_float(y_value)))

        x2s = fields.get("11", [])
        y2s = fields.get("21", [])
        for index, x_value in enumerate(x2s):
            y_value = y2s[index] if index < len(y2s) else y2s[-1] if y2s else "0"
            coords.append((_safe_float(x_value), _safe_float(y_value)))

        if not coords:
            x = _safe_float(fields.get("10", [0.0])[0] if fields.get("10") else 0.0)
            y = _safe_float(fields.get("20", [0.0])[0] if fields.get("20") else 0.0)
            coords.append((x, y))

        return coords

    def _build_entity(self, raw_entity: dict[str, Any], index: int) -> LayoutEntity:
        label = _normalize_text(
            raw_entity.get("label")
            or raw_entity.get("name")
            or raw_entity.get("text")
            or raw_entity.get("block_name")
            or raw_entity.get("type")
        )
        layer = _normalize_text(raw_entity.get("layer") or raw_entity.get("group") or raw_entity.get("category") or "default")
        source_type = _normalize_text(raw_entity.get("type") or raw_entity.get("entity_type") or raw_entity.get("shape") or "entity").lower()
        points = _points_from_entity(raw_entity)
        bounds = raw_entity.get("bounds") if isinstance(raw_entity.get("bounds"), (list, tuple)) and len(raw_entity["bounds"]) >= 4 else _bounding_box(points)
        center = _point_from_any(raw_entity.get("center") or _point_from_any(_center(points)))

        kind, confidence, rationale = self._classify_entity(raw_entity, label, layer, source_type)
        entity_id = _normalize_text(raw_entity.get("id") or raw_entity.get("handle") or raw_entity.get("uuid"))
        if not entity_id:
            entity_id = f"entity-{index}-{_utc_hash(f'{kind}|{label}|{layer}|{center}') }"

        properties = {
            key: value
            for key, value in dict(raw_entity.get("properties") or {}).items()
            if key != "dxf_fields"
        }
        properties.update(
            {
                "source_type": source_type,
                "classification_rationale": rationale,
            }
        )

        return LayoutEntity(
            id=entity_id,
            kind=kind,
            label=label,
            layer=layer,
            center=center,
            bounds=(
                _safe_float(bounds[0]),
                _safe_float(bounds[1]),
                _safe_float(bounds[2]),
                _safe_float(bounds[3]),
            ),
            confidence=confidence,
            source_type=source_type,
            properties=properties,
        )

    def _classify_entity(self, raw_entity: dict[str, Any], label: str, layer: str, source_type: str) -> tuple[str, float, list[str]]:
        haystack = " ".join(
            [
                label,
                layer,
                source_type,
                _normalize_text(raw_entity.get("block_name")),
                _normalize_text(raw_entity.get("entity")),
            ]
        ).lower()

        if _contains_any(haystack, self.ENTITY_MARKERS["machine"]):
            return "machine", 0.94, ["machine marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["conveyor"]):
            return "conveyor", 0.92, ["conveyor marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["transfer"]):
            return "transfer", 0.9, ["transfer marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["waste_line"]):
            return "waste_line", 0.88, ["waste line marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["warehouse"]):
            return "warehouse", 0.91, ["warehouse marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["wip"]):
            return "buffer", 0.88, ["buffer/WIP marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["safety_zone"]):
            return "safety_zone", 0.9, ["safety marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["amr_route"]):
            return "amr_route", 0.87, ["AMR route marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["utility"]):
            return "utility", 0.84, ["utility marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["operator"]):
            return "operator", 0.8, ["operator marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["process"]):
            return "process", 0.8, ["process marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["production_area"]):
            return "production_area", 0.8, ["production area marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["storage_area"]):
            return "storage_area", 0.8, ["storage area marker"]
        if _contains_any(haystack, self.ENTITY_MARKERS["logistic_route"]):
            return "logistic_route", 0.78, ["logistic route marker"]

        if source_type in {"line", "lpolyline", "lwpolyline", "polyline"}:
            return "logistic_route", 0.72, ["line-based route inference"]
        if source_type in {"insert", "block_reference"}:
            return "machine", 0.7, ["block reference inference"]
        if source_type in {"text", "mtext"}:
            return "process", 0.66, ["text label inference"]
        if source_type in {"circle", "arc", "ellipse"}:
            return "buffer", 0.61, ["curve/area inference"]

        return "resource", 0.5, ["fallback generic resource inference"]

    def _build_connections(self, entities: list[LayoutEntity]) -> list[LayoutConnection]:
        if len(entities) < 2:
            return []

        entity_count = len(entities)
        xs = [entity.center[0] for entity in entities]
        ys = [entity.center[1] for entity in entities]
        coordinate_span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
        cell_size = max(coordinate_span / max(math.sqrt(entity_count), 1.0), 1e-6)
        buckets: dict[tuple[int, int], list[int]] = defaultdict(list)
        for index, entity in enumerate(entities):
            cell = (math.floor(entity.center[0] / cell_size), math.floor(entity.center[1] / cell_size))
            buckets[cell].append(index)

        x_order = sorted(range(entity_count), key=lambda index: entities[index].center[0])
        x_positions = {entity_index: position for position, entity_index in enumerate(x_order)}

        connections: list[LayoutConnection] = []
        for source_index, source in enumerate(entities):
            candidate_indexes: set[int] = set()
            source_cell = (
                math.floor(source.center[0] / cell_size),
                math.floor(source.center[1] / cell_size),
            )
            for cell_x in range(source_cell[0] - 2, source_cell[0] + 3):
                for cell_y in range(source_cell[1] - 2, source_cell[1] + 3):
                    bucket = buckets.get((cell_x, cell_y), [])
                    if not bucket:
                        continue
                    position = bisect_left(bucket, source_index)
                    candidate_indexes.update(bucket[max(0, position - 24):position + 25])

            x_position = x_positions[source_index]
            candidate_indexes.update(x_order[max(0, x_position - 24):x_position + 25])
            candidate_indexes.discard(source_index)
            nearest = sorted(
                (entities[index] for index in candidate_indexes),
                key=lambda candidate: _distance(source.center, candidate.center),
            )[:3]
            for target in nearest:
                relation = self._relation_for(source.kind, target.kind)
                if relation is None:
                    continue
                distance = _distance(source.center, target.center)
                confidence = round(max(0.45, min(0.98, 1.0 - distance / 500.0)), 4)
                connections.append(
                    LayoutConnection(
                        source=source.id,
                        target=target.id,
                        relation=relation,
                        distance=distance,
                        confidence=confidence,
                        properties={
                            "source_kind": source.kind,
                            "target_kind": target.kind,
                        },
                    )
                )

        deduped: dict[tuple[str, str, str], LayoutConnection] = {}
        for connection in connections:
            key = (connection.source, connection.target, connection.relation)
            current = deduped.get(key)
            if current is None or connection.confidence > current.confidence:
                deduped[key] = connection
        return sorted(deduped.values(), key=lambda item: (item.source, item.target, item.relation))

    def _relation_for(self, source_kind: str, target_kind: str) -> str | None:
        for rule_source, rule_target, relation in self.RELATION_RULES:
            if source_kind == rule_source and target_kind == rule_target:
                return relation
        if source_kind == target_kind and source_kind in {"machine", "conveyor", "warehouse", "buffer", "amr_route"}:
            return "adjacent_to"
        if source_kind in {"production_area", "storage_area"} or target_kind in {"production_area", "storage_area"}:
            return "contains"
        return None

    def _build_factory_graph(
        self,
        layout_name: str,
        entities: list[LayoutEntity],
        connections: list[LayoutConnection],
        source_format: str,
        source_hash: str,
    ) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for entity in entities:
            counts[entity.kind] = counts.get(entity.kind, 0) + 1

        nodes = []
        for entity in entities:
            nodes.append(
                {
                    "id": entity.id,
                    "kind": entity.kind,
                    "label": entity.label,
                    "layer": entity.layer,
                    "center": list(entity.center),
                    "bounds": list(entity.bounds),
                    "confidence": entity.confidence,
                    "properties": entity.properties,
                }
            )

        edges = [asdict(connection) for connection in connections]
        return {
            "layout_name": layout_name,
            "source_format": source_format,
            "source_hash": source_hash,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "kind_counts": counts,
            "nodes": nodes,
            "edges": edges,
            "objectives": [
                "machines",
                "conveyors",
                "buffers",
                "warehouses",
                "amrs",
                "operators",
                "processes",
                "flows",
                "resources",
                "connections",
                "constraints",
                "production_areas",
                "safety_areas",
                "storage_areas",
                "logistic_routes",
            ],
        }

    def _build_knowledge_graph(
        self,
        layout_name: str,
        entities: list[LayoutEntity],
        connections: list[LayoutConnection],
        source_format: str,
    ) -> dict[str, Any]:
        assertions: list[KnowledgeAssertion] = []
        relations: list[dict[str, Any]] = []

        for entity in entities:
            semantic_class = self._semantic_class(entity.kind)
            assertions.append(
                KnowledgeAssertion(
                    subject=entity.id,
                    predicate="semantic_class",
                    object=semantic_class,
                    confidence=round(min(1.0, entity.confidence + 0.04), 4),
                    source=f"{layout_name}:{source_format}",
                )
            )
            relations.append(
                {
                    "subject": entity.id,
                    "predicate": "has_role",
                    "object": semantic_class,
                    "confidence": round(min(1.0, entity.confidence + 0.04), 4),
                }
            )

        for connection in connections:
            relations.append(
                {
                    "subject": connection.source,
                    "predicate": connection.relation,
                    "object": connection.target,
                    "confidence": connection.confidence,
                }
            )

        return {
            "layout_name": layout_name,
            "fact_count": len(assertions),
            "relation_count": len(relations),
            "assertions": [asdict(item) for item in assertions],
            "relations": relations,
            "sources": ["Knowledge Hub", "Enterprise Memory", "Historical Projects", "Industrial Rules", "Previous Decisions", "Lessons Learned"],
            "confidence": round(min(1.0, 0.55 + len(assertions) / 80.0), 4),
        }

    def _semantic_class(self, kind: str) -> str:
        mapping = {
            "machine": "industrial_equipment",
            "conveyor": "material_handling_asset",
            "transfer": "material_transfer_asset",
            "waste_line": "waste_handling_route",
            "warehouse": "storage_asset",
            "buffer": "wip_buffer",
            "safety_zone": "safety_constraint",
            "amr_route": "autonomous_logistics_route",
            "production_area": "production_area",
            "storage_area": "storage_area",
            "logistic_route": "logistics_route",
            "utility": "utility_service",
            "operator": "human_resource",
            "process": "process_step",
        }
        return mapping.get(kind, "generic_resource")

    def _build_digital_twin(self, layout_name: str, entities: list[LayoutEntity], connections: list[LayoutConnection], source_hash: str) -> DigitalTwinSnapshot:
        simulation_inputs = {
            "node_count": len(entities),
            "edge_count": len(connections),
            "machine_count": sum(1 for entity in entities if entity.kind == "machine"),
            "conveyor_count": sum(1 for entity in entities if entity.kind == "conveyor"),
            "buffer_count": sum(1 for entity in entities if entity.kind == "buffer"),
            "warehouse_count": sum(1 for entity in entities if entity.kind == "warehouse"),
            "amr_route_count": sum(1 for entity in entities if entity.kind == "amr_route"),
            "layout_signature": source_hash,
        }
        state = {
            "snapshots": [f"snapshot-{source_hash}"],
            "versions": [1],
            "scenarios": ["baseline", "high_demand", "maintenance", "amr_reconfiguration"],
            "live_sync": False,
            "simulation_inputs": simulation_inputs,
        }
        return DigitalTwinSnapshot(
            version=f"twin-{source_hash}",
            layout_name=layout_name,
            live_sync=False,
            nodes=len(entities),
            edges=len(connections),
            scenarios=list(state["scenarios"]),
            simulation_inputs=simulation_inputs,
            state=state,
        )

    def _build_simulation(self, entities: list[LayoutEntity], connections: list[LayoutConnection], knowledge_graph: dict[str, Any]) -> SimulationResult:
        machine_count = sum(1 for entity in entities if entity.kind == "machine")
        conveyor_count = sum(1 for entity in entities if entity.kind == "conveyor")
        buffer_count = sum(1 for entity in entities if entity.kind == "buffer")
        warehouse_count = sum(1 for entity in entities if entity.kind == "warehouse")
        amr_route_count = sum(1 for entity in entities if entity.kind == "amr_route")
        travel_distance = round(sum(connection.distance for connection in connections), 3)
        flow_edges = len(connections)
        machine_cluster_factor = self._machine_cluster_factor(entities)
        amr_coverage = amr_route_count / max(1, machine_count + buffer_count + warehouse_count)
        buffer_to_machine_ratio = buffer_count / max(1, machine_count)
        logistics_pressure = min(1.0, (travel_distance / max(1, flow_edges * 35.0)) + max(0.0, buffer_to_machine_ratio - 0.9) * 0.25)

        base_machine_capacity = machine_count * 18.0
        conveyor_gain = conveyor_count * 6.0
        amr_gain = amr_route_count * 5.5
        cluster_gain = machine_cluster_factor * 7.5
        production_capacity = round(base_machine_capacity + conveyor_gain + amr_gain + cluster_gain, 3)

        bottlenecks = self._find_bottlenecks(entities, connections)
        bottleneck_pressure = min(1.0, len(bottlenecks) / max(1, machine_count + buffer_count))
        starvation_risk = round(min(1.0, max(0.02, logistics_pressure * 0.62 + bottleneck_pressure * 0.38)), 4)

        jit_readiness = round(min(1.0, max(0.0, 0.45 + amr_coverage * 0.35 + machine_cluster_factor * 0.2 - logistics_pressure * 0.18)), 4)
        wip_policy_score = round(min(1.0, max(0.0, 0.4 + amr_coverage * 0.25 + (1.0 - min(1.0, buffer_to_machine_ratio)) * 0.35)), 4)

        oee = round(
            min(
                0.97,
                max(
                    0.5,
                    0.58
                    + machine_count * 0.022
                    + conveyor_count * 0.008
                    + amr_coverage * 0.06
                    - bottleneck_pressure * 0.08
                    - logistics_pressure * 0.05,
                ),
            ),
            4,
        )
        roi = round(max(0.0, 0.9 + production_capacity / 155.0 + oee * 0.6 - logistics_pressure * 0.45), 4)

        return SimulationResult(
            material_flow={
                "flow_edges": flow_edges,
                "flow_intensity": round(flow_edges / max(len(entities), 1), 4),
                "flow_edges_per_machine": round(flow_edges / max(1, machine_count), 4),
                "logistics_pressure_index": round(logistics_pressure, 4),
                "starvation_risk_index": starvation_risk,
                "knowledge_coverage": knowledge_graph.get("confidence", 0.0),
            },
            amr_routing={
                "routes": amr_route_count,
                "coverage": round(min(1.0, amr_route_count * 0.2 + flow_edges / 50.0), 4),
                "amr_layout_coverage": round(amr_coverage, 4),
                "fleet_recommendation": self._recommend_amr_fleet(machine_count, warehouse_count, flow_edges),
                "wip_cell_strategy": self._recommend_wip_cell_strategy(wip_policy_score, buffer_to_machine_ratio),
            },
            travel_distance=travel_distance,
            production_capacity=production_capacity,
            oee=oee,
            roi=roi,
            bottlenecks=bottlenecks,
            buffer_occupancy={
                "buffers": buffer_count,
                "estimated_occupancy": round(min(1.0, 0.22 + buffer_count * 0.1 + len(bottlenecks) * 0.07), 4),
                "buffer_to_machine_ratio": round(buffer_to_machine_ratio, 4),
                "jit_readiness": jit_readiness,
                "wip_policy_score": wip_policy_score,
            },
            warehouse_capacity={
                "warehouses": warehouse_count,
                "estimated_capacity_units": warehouse_count * 1000,
                "recommended_near_line_wip_cells": max(2, machine_count // 2),
            },
            cycle_times={
                "baseline_seconds": round(42.0 + travel_distance * 0.32 + len(bottlenecks) * 4.2, 3),
                "variance_seconds": round(4.5 + flow_edges * 0.22 + logistics_pressure * 3.5, 3),
                "estimated_changeover_loss_minutes": round(max(0.0, 8.0 + bottleneck_pressure * 15.0 + logistics_pressure * 10.0), 3),
            },
        )

    def _find_bottlenecks(self, entities: list[LayoutEntity], connections: list[LayoutConnection]) -> list[dict[str, Any]]:
        degree: dict[str, int] = {entity.id: 0 for entity in entities}
        for connection in connections:
            degree[connection.source] = degree.get(connection.source, 0) + 1
            degree[connection.target] = degree.get(connection.target, 0) + 1

        bottlenecks: list[dict[str, Any]] = []
        for entity in entities:
            if entity.kind in {"buffer", "warehouse"} or degree.get(entity.id, 0) <= 1:
                severity = round(min(1.0, 0.45 + (2 - min(degree.get(entity.id, 0), 2)) * 0.18), 4)
                bottlenecks.append(
                    {
                        "id": entity.id,
                        "kind": entity.kind,
                        "label": entity.label,
                        "severity": severity,
                        "degree": degree.get(entity.id, 0),
                        "root_cause": self._bottleneck_root_cause(entity.kind, degree.get(entity.id, 0)),
                        "recommended_action": self._bottleneck_action(entity.kind, severity),
                    }
                )

        return sorted(bottlenecks, key=lambda item: item["severity"], reverse=True)[:8]

    def _build_engineering_analysis(
        self,
        entities: list[LayoutEntity],
        connections: list[LayoutConnection],
        factory_graph: dict[str, Any],
        simulation: SimulationResult,
    ) -> EngineeringAnalysis:
        machine_count = factory_graph["kind_counts"].get("machine", 0)
        buffer_count = factory_graph["kind_counts"].get("buffer", 0)
        warehouse_count = factory_graph["kind_counts"].get("warehouse", 0)
        safety_count = factory_graph["kind_counts"].get("safety_zone", 0)
        amr_route_count = factory_graph["kind_counts"].get("amr_route", 0)
        bottleneck_pressure = round(min(1.0, len(simulation.bottlenecks) / max(1, machine_count + buffer_count)), 4)
        starvation_risk = float(simulation.material_flow.get("starvation_risk_index", 0.0))
        jit_readiness = float(simulation.buffer_occupancy.get("jit_readiness", 0.0))
        wip_policy_score = float(simulation.buffer_occupancy.get("wip_policy_score", 0.0))

        layout_quality_score = round(min(1.0, 0.4 + len(entities) * 0.03 + len(connections) * 0.015), 4)
        flow_balance = round(
            min(
                1.0,
                max(
                    0.0,
                    0.5 + machine_count * 0.04 + amr_route_count * 0.05 - buffer_count * 0.03 - starvation_risk * 0.15,
                ),
            ),
            4,
        )

        constraint_analysis = {
            "safety_zones": safety_count,
            "constraints_found": safety_count + buffer_count + warehouse_count,
            "constraint_density": round((safety_count + buffer_count + warehouse_count) / max(len(entities), 1), 4),
            "bottleneck_pressure": bottleneck_pressure,
            "starvation_risk": starvation_risk,
            "jit_readiness": jit_readiness,
            "wip_policy_score": wip_policy_score,
        }

        amr_recommendations = []
        if amr_route_count == 0:
            amr_recommendations.append("Add AMR routes to connect production, buffer, and storage areas with one-way conflict-safe loops.")
        else:
            amr_recommendations.append("Validate AMR lane width, peak-hour route occupancy, and dispatch priority by starvation risk.")
        amr_recommendations.append(f"Target AMR coverage >= 0.55. Current estimated coverage: {simulation.amr_routing.get('amr_layout_coverage', 0.0)}")

        warehouse_optimisation = []
        if warehouse_count:
            warehouse_optimisation.append("Balance warehouse ingress/egress and convert long staging lanes into near-line WIP cells.")
        else:
            warehouse_optimisation.append("Introduce storage zoning when material staging is required.")
        warehouse_optimisation.append("For corrugated WIP without height storage, deploy low-height sequencing cells near converters.")

        production_optimisation = [
            "Use conveyor adjacency to remove avoidable material handoffs.",
            "Tune WIP buffers to keep cycle-time variance below the estimated threshold.",
            "Apply JIT release windows by converter and slot to reduce changeover-loss minutes.",
        ]
        if machine_count:
            production_optimisation.append("Sequence machine clusters into production cells for shorter internal flows.")

        risk_analysis = [
            f"Bottleneck pressure identified on {len(simulation.bottlenecks)} layout nodes.",
            f"Travel distance accumulation is {simulation.travel_distance} units; watch for excess AMR path length.",
            f"Starvation risk index is {starvation_risk}; prioritize feed continuity actions above 0.35.",
        ]
        if safety_count:
            risk_analysis.append("Safety zones require explicit routing validation.")

        safety_analysis = [
            "Check path intersections with safety zones before live synchronization.",
            "Confirm restricted areas are preserved as non-traversable constraints.",
        ]

        executive_recommendations = [
            "Proceed with digital twin synchronization after validating route constraints.",
            "Prioritize bottleneck mitigation around buffers and warehouses.",
            "Use simulation results to rank AMR and conveyor investments.",
            "Build scenario A/B/C with forklift baseline vs AMR + near-line WIP cells and compare OEE, starvation and ROI.",
            "Adopt constraint-aware JIT sequencing to stabilize converter feeding and reduce unplanned waiting.",
        ]

        return EngineeringAnalysis(
            layout_quality={
                "score": layout_quality_score,
                "status": self._status_for_score(layout_quality_score),
                "entity_coverage": len(entities),
            },
            flow_analysis={
                "score": flow_balance,
                "material_flow_health": self._status_for_score(flow_balance),
                "travel_distance": simulation.travel_distance,
                "starvation_risk": starvation_risk,
                "bottleneck_pressure": bottleneck_pressure,
            },
            constraint_analysis=constraint_analysis,
            amr_recommendations=amr_recommendations,
            warehouse_optimisation=warehouse_optimisation,
            production_optimisation=production_optimisation,
            risk_analysis=risk_analysis,
            safety_analysis=safety_analysis,
            executive_recommendations=executive_recommendations,
        )

    def _build_executive_report(
        self,
        layout_name: str,
        factory_graph: dict[str, Any],
        knowledge_graph: dict[str, Any],
        simulation: SimulationResult,
        analysis: EngineeringAnalysis,
        plant_state_report: dict[str, Any],
    ) -> str:
        lines = [
            f"# Executive Engineering Report: {layout_name}",
            "",
            "## Factory Graph",
            f"- Nodes: {factory_graph['node_count']}",
            f"- Edges: {factory_graph['edge_count']}",
            f"- Dominant kinds: {factory_graph['kind_counts']}",
            "",
            "## Knowledge Graph",
            f"- Facts: {knowledge_graph['fact_count']}",
            f"- Relations: {knowledge_graph['relation_count']}",
            f"- Confidence: {knowledge_graph['confidence']}",
            "",
            "## Simulation",
            f"- OEE: {simulation.oee}",
            f"- ROI: {simulation.roi}",
            f"- Travel distance: {simulation.travel_distance}",
            f"- Bottlenecks: {len(simulation.bottlenecks)}",
            f"- Starvation risk index: {simulation.material_flow.get('starvation_risk_index', 0.0)}",
            f"- AMR layout coverage: {simulation.amr_routing.get('amr_layout_coverage', 0.0)}",
            f"- JIT readiness: {simulation.buffer_occupancy.get('jit_readiness', 0.0)}",
            "",
            "## Plant State (Problems and Opportunities)",
        ]

        for item in plant_state_report["problems"]:
            lines.append(f"- Problem: {item}")
        for item in plant_state_report["opportunities"]:
            lines.append(f"- Opportunity: {item}")
        for item in plant_state_report["priority_actions"]:
            lines.append(f"- Priority Action: {item}")

        lines.extend(
            [
                "",
            "## Engineering Recommendations",
            ]
        )
        for recommendation in analysis.executive_recommendations:
            lines.append(f"- {recommendation}")
        return "\n".join(lines)

    def _build_operational_summary(
        self,
        entities: list[LayoutEntity],
        connections: list[LayoutConnection],
        factory_graph: dict[str, Any],
        simulation: SimulationResult,
        analysis: EngineeringAnalysis,
    ) -> dict[str, Any]:
        def entity_area(entity: LayoutEntity) -> float:
            return round(abs(entity.bounds[2] - entity.bounds[0]) * abs(entity.bounds[3] - entity.bounds[1]), 3)

        def entity_length(entity: LayoutEntity) -> float:
            width = abs(entity.bounds[2] - entity.bounds[0])
            height = abs(entity.bounds[3] - entity.bounds[1])
            return round(math.hypot(width, height), 3)

        machines = [entity for entity in entities if entity.kind == "machine"]
        processes = [entity for entity in entities if entity.kind == "process"]
        conveyors = [entity for entity in entities if entity.kind == "conveyor"]
        transfers = [entity for entity in entities if entity.kind == "transfer"]
        waste_lines = [entity for entity in entities if entity.kind == "waste_line"]
        buffers = [entity for entity in entities if entity.kind == "buffer"]
        warehouses = [entity for entity in entities if entity.kind == "warehouse"]
        routes = [entity for entity in entities if entity.kind in {"logistic_route", "amr_route"}]
        capacity_per_machine = round(simulation.production_capacity / max(1, len(machines)), 3)

        equipment = [
            {
                "id": entity.id,
                "label": entity.label,
                "layer": entity.layer,
                "confidence": entity.confidence,
                "estimated_capacity_units_per_hour": capacity_per_machine,
                "maintenance": "Inspect safety, alignment, wear parts and controls; validate OEM interval.",
            }
            for entity in machines[:100]
        ]
        process_steps = [
            {"id": entity.id, "label": entity.label, "layer": entity.layer, "confidence": entity.confidence, "basis": "explicit_label"}
            for entity in processes[:100]
        ]
        if not process_steps:
            process_steps = [
                {
                    "id": f"process-{entity.id}",
                    "label": f"Operation at {entity.label}",
                    "layer": entity.layer,
                    "confidence": round(min(entity.confidence, 0.6), 3),
                    "basis": "inferred_from_equipment_sequence",
                }
                for entity in machines[:30]
            ]
        flow_relations = [
            {
                "source": connection.source,
                "target": connection.target,
                "relation": connection.relation,
                "distance": connection.distance,
                "confidence": connection.confidence,
            }
            for connection in connections[:200]
        ]
        amr_coverage = float(simulation.amr_routing.get("amr_layout_coverage", 0.0))
        starvation = float(simulation.material_flow.get("starvation_risk_index", 0.0))
        amr_decision = "recommended" if amr_coverage < 0.55 and (len(routes) > 0 or starvation >= 0.35) else "validate_with_scenario"

        return {
            "overview": {
                "total_entities": len(entities),
                "total_connections": len(connections),
                "detected_kinds": factory_graph.get("kind_counts", {}),
                "production_capacity_units_per_hour": simulation.production_capacity,
                "oee": simulation.oee,
                "roi_index": simulation.roi,
            },
            "equipment": equipment,
            "processes": process_steps,
            "flows": {
                "relations": flow_relations,
                "travel_distance": simulation.travel_distance,
                "flow_edges": simulation.material_flow.get("flow_edges", 0),
                "starvation_risk": starvation,
                "management_policy": "JIT pull windows with dispatch priority by starvation risk and constrained route occupancy.",
            },
            "measurements": {
                "wip_area_square_units": round(sum(entity_area(entity) for entity in buffers), 3),
                "warehouse_area_square_units": round(sum(entity_area(entity) for entity in warehouses), 3),
                "conveyor_length_units": round(sum(entity_length(entity) for entity in conveyors), 3),
                "transfer_area_square_units": round(sum(entity_area(entity) for entity in transfers), 3),
                "waste_line_length_units": round(sum(entity_length(entity) for entity in waste_lines), 3),
                "logistics_route_length_units": round(sum(entity_length(entity) for entity in routes), 3),
                "coordinate_units": "drawing_units",
            },
            "maintenance": {
                "detected_assets": len(machines) + len(conveyors) + len(transfers),
                "preventive_actions": [
                    "Validate OEM preventive intervals for every identified machine.",
                    "Inspect conveyor tracking, rollers, guards and transfer alignment.",
                    "Create condition-monitoring points for critical bottleneck assets.",
                ],
            },
            "problems": analysis.risk_analysis,
            "improvements": [
                *analysis.production_optimisation,
                *analysis.warehouse_optimisation,
                *analysis.executive_recommendations,
            ],
            "amr_assessment": {
                "decision": amr_decision,
                "coverage": amr_coverage,
                "fleet": simulation.amr_routing.get("fleet_recommendation", {}),
                "recommendations": analysis.amr_recommendations,
            },
            "consulting_report": self._build_consulting_report(
                entities,
                simulation,
                analysis,
                amr_decision,
            ),
        }

    def _build_consulting_report(
        self,
        entities: list[LayoutEntity],
        simulation: SimulationResult,
        analysis: EngineeringAnalysis,
        amr_decision: str,
    ) -> dict[str, Any]:
        knowledge = _load_consulting_benchmarks()
        equipment_catalog = knowledge.get("catalog", {}).get("equipment", [])
        hypotheses = knowledge.get("hypotheses", {})
        benchmark = hypotheses.get("ingetrans_benchmark_reference", {})
        hypothesis_by_id = {item.get("id"): item for item in hypotheses.get("hypotheses", []) if isinstance(item, dict)}

        oee_percent = round(simulation.oee * 100.0, 2)
        catalog_oee_midpoints: list[float] = []
        quality_midpoints: list[float] = []
        preventive_hours: list[float] = []
        for item in equipment_catalog:
            operations = item.get("operations", {})
            oee_range = operations.get("oee_typical_percent", [])
            quality_range = operations.get("quality_loss_percent", [])
            maintenance = item.get("maintenance", {})
            if len(oee_range) >= 2:
                catalog_oee_midpoints.append((float(oee_range[0]) + float(oee_range[1])) / 2.0)
            if len(quality_range) >= 2:
                quality_midpoints.append((float(quality_range[0]) + float(quality_range[1])) / 2.0)
            if maintenance.get("preventive_hours_per_month") is not None:
                preventive_hours.append(float(maintenance["preventive_hours_per_month"]))

        benchmark_oee = round(sum(catalog_oee_midpoints) / max(1, len(catalog_oee_midpoints)), 2)
        assumed_scrap = round(sum(quality_midpoints) / max(1, len(quality_midpoints)), 2)
        pm_hours = round(sum(preventive_hours) / max(1, len(preventive_hours)), 1)
        oee_target = round(min(92.0, max(benchmark_oee, oee_percent + 3.0)), 2)
        oee_delta = round(max(0.0, oee_target - oee_percent), 2)
        throughput_gain_percent = round(oee_delta / max(oee_percent, 1.0) * 100.0, 2)
        capacity_target = round(simulation.production_capacity * (1.0 + throughput_gain_percent / 100.0), 2)
        scrap_target = round(max(0.5, assumed_scrap * 0.75), 2)
        starvation = float(simulation.material_flow.get("starvation_risk_index", 0.0))

        proposals = [
            {
                "id": "CONS-OEE-01",
                "domain": "oee",
                "priority": "P0" if oee_percent < benchmark_oee else "P1",
                "title": "Recover OEE through loss Pareto, SMED and constraint control",
                "problem": f"Estimated OEE {oee_percent}% versus catalog midpoint {benchmark_oee}%.",
                "root_causes": ["changeover loss", "micro-stops and availability loss", "feed starvation", "unvalidated speed-quality trade-off"],
                "baseline": {"oee_percent": oee_percent},
                "target": {"oee_percent": oee_target, "oee_delta_points": oee_delta},
                "expected_impact": {"throughput_gain_percent": throughput_gain_percent, "capacity_target_units_per_hour": capacity_target},
                "actions": [
                    "Build a weekly OEE loss Pareto by availability, performance and quality.",
                    "Run SMED observation on the top two changeovers and externalize preparation.",
                    "Set centerline parameters and escalation limits for speed, quality and jams.",
                    "Review the bottleneck every shift and protect it from starvation and blockage.",
                ],
                "kpis": ["oee_percent", "availability_percent", "performance_percent", "quality_percent", "changeover_minutes", "microstop_minutes"],
                "horizon": "0-90 days",
                "confidence": 0.72,
                "decision_gate": "Pilot when two weeks of machine-state and production counts are available.",
            },
            {
                "id": "CONS-SCRAP-01",
                "domain": "scrap",
                "priority": "P0",
                "title": "Reduce quality loss and trim waste with defect-at-source control",
                "problem": f"No live scrap telemetry is connected; catalog quality-loss midpoint is {assumed_scrap}% and must be validated.",
                "root_causes": ["setup instability", "registration or feed drift", "late defect detection", "unsegmented trim and reject flows"],
                "baseline": {"assumed_quality_loss_percent": assumed_scrap, "basis": "catalog_midpoint_not_site_measurement"},
                "target": {"quality_loss_percent": scrap_target, "relative_reduction_percent": 25.0},
                "expected_impact": {"saleable_output_gain_percent": round(assumed_scrap - scrap_target, 2)},
                "actions": [
                    "Measure scrap by machine, order, SKU, defect and shift at the point of generation.",
                    "Introduce first-piece approval and parameter recipe lock before full-speed production.",
                    "Run daily top-three defect Pareto with containment owner and due date.",
                    "Separate trim, startup waste and quality rejects to avoid masking root causes.",
                ],
                "kpis": ["scrap_percent", "startup_waste_kg", "trim_waste_kg", "rejects_per_1000_sheets", "first_pass_yield_percent"],
                "horizon": "0-60 days",
                "confidence": 0.58,
                "decision_gate": "Replace benchmark assumption after four weeks of weighed site scrap data.",
            },
            {
                "id": "CONS-MAINT-01",
                "domain": "maintenance",
                "priority": "P1",
                "title": "Move critical equipment from reactive to condition-based maintenance",
                "problem": "Layout identifies maintainable assets but no failure history or condition telemetry is connected.",
                "root_causes": ["reactive work mix", "critical-spares exposure", "repeat failure modes", "no condition thresholds"],
                "baseline": {"catalog_pm_hours_per_machine_month": pm_hours},
                "target": {"planned_work_percent": 80, "repeat_failure_reduction_percent": 30},
                "expected_impact": {"availability_risk": "reduced", "unplanned_stop_reduction_percent_range": [10, 25]},
                "actions": [
                    "Rank assets by bottleneck role, safety, downtime cost and spare lead time.",
                    "Create PM standards for alignment, wear, lubrication, controls and guarding.",
                    "Add vibration, thermal or current checks to the top critical assets.",
                    "Run bad-actor review and RCA for every repeat failure above the downtime threshold.",
                ],
                "kpis": ["planned_work_percent", "mtbf_hours", "mttr_minutes", "pm_compliance_percent", "repeat_failure_count"],
                "horizon": "30-120 days",
                "confidence": 0.68,
                "decision_gate": "Approve criticality matrix with maintenance and production owners.",
            },
            {
                "id": "CONS-FLOW-01",
                "domain": "intralogistics",
                "priority": "P0" if starvation >= 0.35 else "P1",
                "title": "Stabilize WIP and machine feed with JIT dispatch rules",
                "problem": f"Starvation risk index is {round(starvation, 3)} and route coverage requires operational validation.",
                "root_causes": ["dispatch without starvation priority", "WIP too far from point of use", "uncontrolled release windows", "shared-route congestion"],
                "baseline": {"starvation_risk_index": round(starvation, 3), "travel_distance_units": simulation.travel_distance},
                "target": {"starvation_reduction_percent_range": [60, 90], "travel_distance_reduction_percent_range": [20, 45]},
                "expected_impact": {"oee_points_range": [1.0, 3.5], "schedule_adherence_gain_percent_range": [4, 12]},
                "actions": [
                    "Define near-line WIP cells by converter cadence and maximum stock age.",
                    "Dispatch replenishment by starvation risk, due date and route occupancy.",
                    "Use 30-45 minute JIT release windows and replan every 15-30 minutes.",
                    "Separate inbound and outbound flows at bottleneck intersections.",
                ],
                "kpis": ["starvation_events", "feed_sla_percent", "transport_response_seconds", "wip_age_hours", "schedule_adherence_percent"],
                "horizon": "30-120 days",
                "confidence": 0.74,
                "decision_gate": "Pilot one converter loop before plant-wide rollout.",
            },
            {
                "id": "CONS-SAFETY-01",
                "domain": "safety",
                "priority": "P0",
                "title": "Validate pedestrian, forklift and automated-flow segregation",
                "problem": "CAD topology can identify candidate conflicts, but it cannot prove safe clearances or regulatory compliance without calibrated scale and a site walkdown.",
                "root_causes": ["mixed traffic", "blind intersections", "uncalibrated aisle width", "undefined emergency and recovery zones"],
                "baseline": {"layout_risk_status": "unvalidated", "cad_scale_calibrated": False},
                "target": {"critical_conflicts_closed_percent": 100, "validated_emergency_routes_percent": 100},
                "expected_impact": {"traffic_conflict_risk": "reduced", "automation_readiness": "improved"},
                "actions": [
                    "Calibrate CAD units and verify aisle, doorway and turning-envelope dimensions on site.",
                    "Map pedestrian crossings, forklift lanes, blind corners, fire routes and exclusion zones.",
                    "Run task-based risk assessment for loading, charging, recovery and maintenance modes.",
                    "Require EHS sign-off before changing traffic rules or deploying AMRs.",
                ],
                "kpis": ["open_traffic_conflicts", "near_miss_count", "validated_crossings_percent", "emergency_route_compliance_percent"],
                "horizon": "0-60 days",
                "confidence": 0.62,
                "decision_gate": "No layout or AMR GO decision without calibrated geometry, site walkdown and EHS approval.",
            },
            {
                "id": "CONS-AMR-01",
                "domain": "amr",
                "priority": "P1",
                "title": "Evaluate AMR only where flow stability and safety justify automation",
                "problem": f"Current AMR assessment is {amr_decision}; no live mission, traffic or charging data is connected.",
                "root_causes": ["forklift dependency", "variable response time", "unsequenced transport requests", "layout conflict risk"],
                "baseline": {"amr_coverage": simulation.amr_routing.get("amr_layout_coverage", 0.0)},
                "target": {"forklift_reduction_percent_range": [35, 65], "starvation_reduction_percent_range": [60, 90]},
                "expected_impact": {
                    "oee_points_range": [2.0, float(benchmark.get("oee_delta_points", 6))],
                    "annual_additional_production_meters_reference": benchmark.get("annual_additional_production_meters"),
                    "annual_operating_savings_eur_reference": benchmark.get("annual_operating_savings_eur"),
                },
                "actions": [
                    "Build an origin-destination matrix with peak transport demand and service SLA.",
                    "Simulate fleet sizes 4/6/8 with charging, blocked aisles and priority dispatch.",
                    "Validate lane width, crossings, fire routes, pedestrian segregation and recovery modes.",
                    "Run a time-boxed pilot and approve scale-up only against OEE, safety and response KPIs.",
                ],
                "kpis": hypothesis_by_id.get("H-AMR-01", {}).get("kpis", []),
                "horizon": "60-180 days",
                "confidence": 0.64,
                "decision_gate": "GO only after scenario score >= 0.75 and safety validation; PILOT at 0.60-0.74.",
            },
        ]

        priority_weight = {"P0": 3, "P1": 2, "P2": 1}
        proposals.sort(key=lambda item: (priority_weight.get(item["priority"], 0), item["confidence"]), reverse=True)
        scenarios = [
            {
                "id": "A",
                "name": "Baseline",
                "investment": "none",
                "oee_percent": oee_percent,
                "capacity_units_per_hour": simulation.production_capacity,
                "scrap_percent": assumed_scrap,
                "risk": "current",
            },
            {
                "id": "B",
                "name": "Operational excellence",
                "investment": "low-medium",
                "oee_percent": oee_target,
                "capacity_units_per_hour": capacity_target,
                "scrap_percent": scrap_target,
                "risk": "low",
            },
            {
                "id": "C",
                "name": "JIT WIP + AMR pilot",
                "investment": "medium-high",
                "oee_percent_range": [round(oee_percent + 2.0, 2), round(min(96.0, oee_percent + 6.0), 2)],
                "forklift_reduction_percent_range": [35, 65],
                "starvation_reduction_percent_range": [60, 90],
                "risk": "medium_pending_simulation",
            },
        ]
        return {
            "status": "hypothesis_based_requires_site_validation",
            "executive_diagnosis": (
                "Prioritize measured OEE and scrap loss recovery before major CAPEX; "
                "pilot JIT/AMR only after flow demand, safety and baseline telemetry are validated."
            ),
            "proposals": proposals,
            "scenarios": scenarios,
            "required_site_data": [
                "machine states and downtime reasons",
                "good count and total count by order",
                "scrap weight by machine, defect and shift",
                "changeover start/end and first-good-piece timestamps",
                "transport requests, response times and origin-destination pairs",
                "maintenance work orders, failure modes, MTBF and MTTR",
                "CAD unit calibration and safety route constraints",
            ],
            "evidence_refs": knowledge.get("evidence", []),
            "governance_note": "All impacts are hypotheses until calibrated with site telemetry, OEM data and validated simulation.",
        }

    def _machine_cluster_factor(self, entities: list[LayoutEntity]) -> float:
        machines = [entity for entity in entities if entity.kind == "machine"]
        if len(machines) < 2:
            return 0.0
        distances: list[float] = []
        for index, machine in enumerate(machines):
            for other in machines[index + 1 :]:
                distances.append(_distance(machine.center, other.center))
        if not distances:
            return 0.0
        avg_distance = sum(distances) / len(distances)
        return round(min(1.0, max(0.0, 1.0 - avg_distance / 120.0)), 4)

    def _recommend_amr_fleet(self, machine_count: int, warehouse_count: int, flow_edges: int) -> dict[str, Any]:
        baseline = max(2, (machine_count // 2) + warehouse_count)
        peak = max(baseline + 1, baseline + flow_edges // 10)
        return {
            "baseline_units": baseline,
            "peak_units": peak,
            "dispatch_policy": "priority_by_starvation_risk",
        }

    def _recommend_wip_cell_strategy(self, wip_policy_score: float, buffer_to_machine_ratio: float) -> dict[str, Any]:
        proximity = "near_converter" if buffer_to_machine_ratio <= 1.0 else "redistribute_buffers"
        return {
            "strategy": "jit_proximity_cells",
            "proximity_policy": proximity,
            "score": round(wip_policy_score, 4),
            "notes": [
                "Use low-height WIP cells when height storage is constrained.",
                "Eliminate forklift aisles where AMR-only operation is feasible.",
            ],
        }

    def _bottleneck_root_cause(self, kind: str, degree: int) -> str:
        if kind == "buffer":
            return "wip_accumulation_or_pull_mismatch"
        if kind == "warehouse":
            return "dispatch_ingress_imbalance"
        if degree <= 1:
            return "low_connectivity_or_isolated_flow_node"
        return "multi_factor"

    def _bottleneck_action(self, kind: str, severity: float) -> str:
        if kind == "buffer":
            return "rebalance_wip_release_and_add_jit_sequencing"
        if kind == "warehouse":
            return "separate_inbound_outbound_lanes_and_schedule_dispatch_windows"
        if severity >= 0.75:
            return "increase_path_redundancy_and_priority_dispatch"
        return "monitor_and_validate_with_scenario_comparison"

    def _build_plant_state_report(
        self,
        factory_graph: dict[str, Any],
        simulation: SimulationResult,
        analysis: EngineeringAnalysis,
    ) -> dict[str, Any]:
        problems: list[str] = []
        opportunities: list[str] = []
        actions: list[str] = []

        starvation_risk = float(simulation.material_flow.get("starvation_risk_index", 0.0))
        jit_readiness = float(simulation.buffer_occupancy.get("jit_readiness", 0.0))
        amr_coverage = float(simulation.amr_routing.get("amr_layout_coverage", 0.0))

        if starvation_risk >= 0.35:
            problems.append("High starvation risk on converter/corrugator feed loops.")
            actions.append("Prioritize AMR dispatch by starvation risk and enforce feed continuity windows.")
        if simulation.travel_distance >= 900:
            problems.append("Excessive intralogistics travel distance increases response delays.")
            actions.append("Re-layout near-line WIP cells and shorten route loops around high-demand machines.")
        if len(simulation.bottlenecks) >= 3:
            problems.append("Multiple bottleneck nodes detected across buffer/warehouse topology.")
            actions.append("Run A/B/C scenario tests for buffer sizing and route segmentation.")

        if amr_coverage < 0.45:
            opportunities.append("AMR route coverage can be expanded for higher logistics stability.")
        else:
            opportunities.append("AMR route coverage is sufficient for advanced dispatch optimization.")

        if jit_readiness < 0.65:
            opportunities.append("JIT readiness can improve by aligning WIP cells to converter cadence.")
        else:
            opportunities.append("JIT readiness indicates strong potential for pull-based flow control.")

        opportunities.append("Use machine-aware scenario planning to compare ROI and OEE impact before capex decisions.")

        state_score = round(
            min(
                1.0,
                max(
                    0.0,
                    (analysis.layout_quality.get("score", 0.0) * 0.35)
                    + (analysis.flow_analysis.get("score", 0.0) * 0.35)
                    + ((1.0 - starvation_risk) * 0.3),
                ),
            ),
            4,
        )

        return {
            "state_score": state_score,
            "state_status": self._status_for_score(state_score),
            "problems": problems,
            "opportunities": opportunities,
            "priority_actions": actions,
            "kpi_snapshot": {
                "oee": simulation.oee,
                "roi": simulation.roi,
                "travel_distance": simulation.travel_distance,
                "starvation_risk": starvation_risk,
                "amr_coverage": amr_coverage,
                "jit_readiness": jit_readiness,
            },
        }

    def _confidence_score(
        self,
        entities: list[LayoutEntity],
        connections: list[LayoutConnection],
        knowledge_graph: dict[str, Any],
    ) -> float:
        entity_score = min(1.0, len(entities) / 18.0)
        relation_score = min(1.0, len(connections) / 20.0)
        knowledge_score = float(knowledge_graph.get("confidence", 0.0))
        return (entity_score * 0.35) + (relation_score * 0.25) + (knowledge_score * 0.4)

    def _ahde_hypotheses(self, raw_entities: list[dict[str, Any]], entities: list[LayoutEntity]) -> list[dict[str, Any]]:
        hypotheses = [
            {
                "name": "label-first classification",
                "score": round(min(1.0, len([entity for entity in entities if entity.kind != 'resource']) / max(len(entities), 1)), 4),
                "rationale": "Prefer explicit labels and layers when available.",
            },
            {
                "name": "geometry-first classification",
                "score": round(min(1.0, sum(1 for entity in raw_entities if entity.get('points') or entity.get('bounds')) / max(len(raw_entities), 1)), 4),
                "rationale": "Use geometry and topology to infer route-like objects.",
            },
            {
                "name": "layer-first classification",
                "score": round(min(1.0, sum(1 for entity in raw_entities if entity.get('layer')) / max(len(raw_entities), 1)), 4),
                "rationale": "Use CAD layer semantics to bias the classifier.",
            },
        ]
        return sorted(hypotheses, key=lambda item: item["score"], reverse=True)

    def _select_hypothesis(self, raw_entities: list[dict[str, Any]], entities: list[LayoutEntity]) -> dict[str, Any]:
        ranked = self._ahde_hypotheses(raw_entities, entities)
        return ranked[0] if ranked else {"name": "none", "score": 0.0, "rationale": "No layout data supplied."}

    def _selected_rules(self, entities: list[LayoutEntity]) -> list[str]:
        rules: list[str] = []
        kinds = {entity.kind for entity in entities}
        if "machine" in kinds and "conveyor" in kinds:
            rules.append("machine-conveyor adjacency")
        if "warehouse" in kinds:
            rules.append("warehouse dispatch rule")
        if "safety_zone" in kinds:
            rules.append("safety constraint rule")
        if "amr_route" in kinds:
            rules.append("AMR routing rule")
        return rules

    def _status_for_score(self, score: float) -> str:
        if score >= 0.85:
            return "excellent"
        if score >= 0.7:
            return "good"
        if score >= 0.5:
            return "acceptable"
        return "needs_improvement"

    def _build_object_evidence(
        self,
        layout_name: str,
        source_format: str,
        entities: list[LayoutEntity],
    ) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []
        for entity in entities:
            evidence.append(
                {
                    "id": f"evidence-{layout_name}-{entity.id}",
                    "source": "industrial_layout_interpreter",
                    "payload": {
                        "layout_name": layout_name,
                        "entity_id": entity.id,
                        "entity_label": entity.label,
                        "entity_kind": entity.kind,
                        "source_format": source_format,
                        "confidence_score": entity.confidence,
                        "recognition_method": "marker_and_geometry_hybrid",
                        "detection_quality": self._status_for_score(entity.confidence),
                        "source_references": [
                            f"layer:{entity.layer}",
                            f"type:{entity.source_type}",
                        ],
                        "traceability": {
                            "classification_rationale": entity.properties.get("classification_rationale", []),
                        },
                    },
                    "mission_id": "M013",
                }
            )
        return evidence


def interpret_layout(payload: dict[str, Any]) -> dict[str, Any]:
    return IndustrialLayoutInterpreter().interpret(payload)
