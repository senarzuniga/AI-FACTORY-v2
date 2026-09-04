# Auditoría local: IS-BACKOFFICE (resumen de reutilización)

Fecha: 2026-07-19

Alcance
- Auditoría local del repositorio `C:/Users/Inaki Senar/Documents/GitHub/IS-BACKOFFICE` para identificar módulos, artefactos y APIs reutilizables por el "Factory Intelligence Workbench" y el `Mission Manager`.
- Método: inspección de estructura (carpetas/README), lectura de módulos clave (`knowledge_hub`, `backoffice/*`, `ingetrans-reel-simulator`, `plant_simulator`, `document_analysis`) y evaluación rápida de acoplamiento, documentación y encaje funcional.

Resumen ejecutivo
- IS-BACKOFFICE es un sistema modular y maduro orientado a inteligencia comercial, pero contiene módulos de propósito general que son altamente reutilizables para ingeniería industrial: motor de simulación, almacén de conocimiento (knowledge graph + evidence), motores de extracción, parser multi-formato y generadores de informe.
- Recomendación inmediata: Reusar antes que reconstruir. Priorizar `knowledge_hub/competitive_intel`, `document_analysis`, `ingetrans-reel-simulator`, `backoffice/graph` y `backoffice/reporting` para un POC del Workbench.

Inventario resumido y puntuación de reutilización (Reuse Score 0-100)
- `knowledge_hub/competitive_intel` — 88
  - Por qué: graph, truth engine, evidence store, indexer y pipelines para ingestión/versionado de hechos. Buen grado de desacoplo (JSON/JSONL), documentación local (`README.md`) y diseño explícito de veracidad/versionado.
- `ingetrans-reel-simulator` — 84
  - Por qué: runner RC1, `00_FIDELITY_FRAMEWORK.md`, escenarios YAML, scripts de ejecución y outputs reproducibles. Ideal como motor de simulación para POC (headless runner listo).
- `document_analysis` — 80
  - Por qué: parser multi-formato (PDF, DOCX, imágenes OCR, JSON, CSV), cache y salida estructurada; facilita ingestión de planos convertidos a SVG/PNG o de informes técnicos.
- `backoffice/graph` (GraphStore) — 78
  - Por qué: almacenamiento en memoria CRUD/exposición sencilla y funciones de timeline y estadísticas; requiere adaptación de modelos (pydantic) para Factory Graph pero es sólido como capa de persistencia temporal/POC.
- `backoffice/reporting` — 76
  - Por qué: generador de informes ejecutivos, export HTML/JSON; encaja con el `Executive Report Generator` solicitado.
- `plant_simulator` — 75
  - Por qué: `SimulationEngine` y `ScenarioOptimizer` útiles como base de motor/sandbox para pruebas rápidas (POC), outputs ya normalizados.
- `backoffice/extraction` — 74
  - Por qué: rule-based extraction y scoring; utilizable para extraer metadatos y hechos de documentación técnica y planos preprocesados.
- `backoffice/analytics` — 72
  - Por qué: engines de análisis y scoring, forecaster y componentes de insight que se pueden adaptar para análisis de flujos y KPIs industriales.
- `assets/layout_*.json` + `utils/canvas_renderer.py` — 70
  - Por qué: formato de layout JSON ya usado por simuladores; facilita construir Factory Graph a partir de un layout simple.
- `streamlit` UI components (pages, instruction_panel) — 65
  - Por qué: UI reutilizable para prototipos del Workbench (Factory Explorer, Scenario Manager), requiere adaptación visual y añadido de nuevos componentes CAD/visualización.

Observaciones relevantes
- Format support: No hay soporte nativo para DWG; sí hay layout JSON y soporte amplio para PDF/imagen/HTML/text por `document_analysis`.
- Simulation fidelity: `ingetrans-reel-simulator` tiene marco de fidelidad y runner headless — excelente punto de partida para Scenario Generator y Simulation Preparation.
- Knowledge & evidence: `knowledge_hub/competitive_intel` ya implementa `EvidenceStore` (JSONL), `KnowledgeGraph` y `TruthEngine` con `FactVersioning` y resolución de contradicciones — coincide con el requisito de `Truth Graph` y `Knowledge Map`.
- Tight coupling points: varios módulos dependen de `backoffice.models` (Pydantic) — para reusar será necesario un adaptador de datos o capas DTO que conviertan `FactoryGraph`/Workbench entities al modelo esperado.

Mapping rápido: Workbench capabilities → candidatos a reutilizar
- Drawing Import / Drawing Recognition: `document_analysis` (para raster/OCR), plus recommend `ezdxf` or external DWG->DXF/SVG conversion as pre-step.
- Factory Graph Builder: `knowledge_hub.KnowledgeGraph` + `backoffice/graph.GraphStore` (adaptadores de modelo).
- Simulation Preparation / Scenario Generator: `ingetrans-reel-simulator` (scenarios YAML) + `plant_simulator.SimulationEngine`.
- Flow/Bottleneck/WIP Analyzer: `plant_simulator` outputs + custom analyzers built over `backoffice/analytics` engines.
- Executive Report Generator: `backoffice/reporting.ReportGenerator` + `plant_simulator/report_generator.py` for PDF/Excel placeholders.
- Evidence, versioning, truth: `knowledge_hub/competitive_intel` (EvidenceStore + TruthEngine + FactVersioning).

Riesgos y limitaciones
- DWG/DXF: no parser nativo; requiere conversión (external tool) o integración de `ezdxf`/CAD SDK.
- Model binding: `backoffice.*` usa modelos Pydantic específicos a dominio comercial; se necesitarán adaptadores para entidades industriales (FactoryGraph schema).
- Tests: cobertura de tests limitada visible; incluir sanity checks y crear tests para adaptadores.

Prioridad de POCs (recomendado, corto plazo)
1. POC A (2–4 días): Factory Graph contract + adapter
   - Objetivo: definir JSON contract del `Factory Graph` y construir adapter que cargue `assets/layout_common.json` en `KnowledgeGraph`/`GraphStore`.
2. POC B (3–6 días): Simulation adapter
   - Objetivo: mapear `Factory Graph` → scenario YAML para `ingetrans-reel-simulator` y ejecutar RC1, capturar outputs y métricas (throughput, bottlenecks).
3. POC C (3–7 días): Evidence/Truth integration
   - Objetivo: ingestión de hechos extraídos de documentos (document_analysis → extraction) hacia `EvidenceStore` y `TruthEngine` y generación de resumenes con `ReportGenerator`.

Recomendaciones concretas
- Adoptar un patrón de adaptadores: `WorkbenchEntity ↔ BackofficeModel` para evitar forzar dependencias.
- Implementar una pequeña capa `is_backoffice_adapter/` con funciones de mapeo y tests unitarios.
- Añadir un script `tools/poe_backoffice_reuse.md` con pasos reproducibles para ejecutar POCs (entorno virtual, dependencias mínimas, comandos de ejemplo).
- Para DWG: elegir estrategia (1) requerir conversión externa a DXF/SVG en pipeline de ingestión o (2) integrar `ezdxf` y `pyautocad` según licencia y disponibilidad.

Próximos pasos propuestos (elige una)
- Opción 1 — Ejecutar POC A (Factory Graph adapter) ahora; necesito permiso para crear el adaptador en `ai-factory-v2/` y usar `assets/layout_common.json` como caso de prueba.
- Opción 2 — Auditoría profunda (automática) del código en IS-BACKOFFICE para generar un inventario por módulo y estimación de esfuerzo (require clonación/lectura completa, 1–2 horas extra).
- Opción 3 — Preparar entorno local reproducible y ejecutar RC1 del simulador para recoger outputs (necesito permiso para ejecutar scripts y tiempo estimado ~10–30 min local).

---
Archivo generado automáticamente por el asistente — ¿qué opción quieres ejecutar a continuación?
