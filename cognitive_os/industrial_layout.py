"""Industrial layout interpretation pipeline for DWG/DXF-like inputs.

The service accepts normalized layout payloads or DXF text and produces a
factory graph, semantic knowledge bundle, digital twin snapshot, simulation
baseline, and engineering analysis. The implementation is intentionally
dependency-light so it can run inside the existing Cognitive OS stack without
requiring external CAD tooling.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
        if import_summary is not None:
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
        executive_report = self._build_executive_report(layout_name, factory_graph, knowledge_graph, simulation, analysis)
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
            normalized.append(
                {
                    "id": item.get("id"),
                    "type": item.get("primitive", "entity"),
                    "label": item.get("label", "entity"),
                    "layer": item.get("layer", "default"),
                    "points": points,
                    "properties": item.get("properties", {}),
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

        properties = dict(raw_entity.get("properties") or {})
        properties.update(
            {
                "source_type": source_type,
                "classification_rationale": rationale,
                "raw_entity": raw_entity,
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

        connections: list[LayoutConnection] = []
        for source in entities:
            nearest = sorted(
                (target for target in entities if target.id != source.id),
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
        bottleneck_count = sum(1 for entity in entities if entity.kind in {"buffer", "warehouse"})

        travel_distance = round(sum(connection.distance for connection in connections), 3)
        production_capacity = round(machine_count * 18.0 + conveyor_count * 6.0 + amr_route_count * 4.0, 3)
        oee = round(min(0.97, 0.52 + machine_count * 0.03 + conveyor_count * 0.01 - bottleneck_count * 0.02), 4)
        roi = round(max(0.0, 1.0 + production_capacity / 150.0 - travel_distance / 2000.0), 4)
        bottlenecks = self._find_bottlenecks(entities, connections)

        return SimulationResult(
            material_flow={
                "flow_edges": len(connections),
                "flow_intensity": round(len(connections) / max(len(entities), 1), 4),
                "knowledge_coverage": knowledge_graph.get("confidence", 0.0),
            },
            amr_routing={
                "routes": amr_route_count,
                "coverage": round(min(1.0, amr_route_count * 0.2 + len(connections) / 50.0), 4),
            },
            travel_distance=travel_distance,
            production_capacity=production_capacity,
            oee=oee,
            roi=roi,
            bottlenecks=bottlenecks,
            buffer_occupancy={
                "buffers": buffer_count,
                "estimated_occupancy": round(min(1.0, 0.25 + buffer_count * 0.12 + len(bottlenecks) * 0.05), 4),
            },
            warehouse_capacity={
                "warehouses": warehouse_count,
                "estimated_capacity_units": warehouse_count * 1000,
            },
            cycle_times={
                "baseline_seconds": round(45.0 + travel_distance * 0.35 + len(bottlenecks) * 4.0, 3),
                "variance_seconds": round(5.0 + len(connections) * 0.2, 3),
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
                bottlenecks.append(
                    {
                        "id": entity.id,
                        "kind": entity.kind,
                        "label": entity.label,
                        "severity": round(min(1.0, 0.45 + (2 - min(degree.get(entity.id, 0), 2)) * 0.18), 4),
                    }
                )

        return bottlenecks[:6]

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

        layout_quality_score = round(min(1.0, 0.4 + len(entities) * 0.03 + len(connections) * 0.015), 4)
        flow_balance = round(min(1.0, 0.5 + machine_count * 0.04 + amr_route_count * 0.05 - buffer_count * 0.03), 4)

        constraint_analysis = {
            "safety_zones": safety_count,
            "constraints_found": safety_count + buffer_count + warehouse_count,
            "constraint_density": round((safety_count + buffer_count + warehouse_count) / max(len(entities), 1), 4),
        }

        amr_recommendations = []
        if amr_route_count == 0:
            amr_recommendations.append("Add AMR routes to connect production, buffer, and storage areas.")
        else:
            amr_recommendations.append("Validate AMR lane width and travel distance against peak traffic.")

        warehouse_optimisation = []
        if warehouse_count:
            warehouse_optimisation.append("Balance warehouse ingress and egress to reduce re-handling.")
        else:
            warehouse_optimisation.append("Introduce storage zoning when material staging is required.")

        production_optimisation = [
            "Use conveyor adjacency to remove avoidable material handoffs.",
            "Tune WIP buffers to keep cycle-time variance below the estimated threshold.",
        ]
        if machine_count:
            production_optimisation.append("Sequence machine clusters into production cells for shorter internal flows.")

        risk_analysis = [
            f"Bottleneck pressure identified on {len(simulation.bottlenecks)} layout nodes.",
            f"Travel distance accumulation is {simulation.travel_distance} units; watch for excess AMR path length.",
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
            "",
            "## Engineering Recommendations",
        ]
        for recommendation in analysis.executive_recommendations:
            lines.append(f"- {recommendation}")
        return "\n".join(lines)

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
