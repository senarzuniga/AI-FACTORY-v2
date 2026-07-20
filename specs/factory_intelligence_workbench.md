# Factory Intelligence Workbench — Especificación inicial

Objetivo
- Módulo autónomo de Ingeniería Industrial reutilizable, preparado para integración en `IS_BACKOFFICE`.

Alcance funcional (MVP)
- Import de planos: DWG/DXF/PDF/imágenes raster.
- Reconocimiento de dibujos y maquinaria (CAD → entidades industriales).
- Factory Graph Builder: grafo de planta, flujos de producción y material.
- Análisis: Bottleneck Analyzer, Flow Analyzer, WIP Analyzer, Queue Analysis.
- Opportunity Engines: AMR, Ingetrans, Forklift Elimination.
- Simulation Preparation & Scenario Generator.
- Executive Report & Offer Generator.

Componentes principales
- `ingest/` — parsers de DWG/DXF/PDF y normalizadores.
- `vision/` — OCR y reconocimiento de símbolos/maquinas.
- `graph/` — builder y persistencia del Factory Graph.
- `analysis/` — motores estadísticos y heurísticos (bottleneck, WIP, flow).
- `optimizer/` — generadores de hipótesis y scoring.
- `simulator/` — preparación y export para motores de simulación externos.
- `ui/` — componentes reutilizables: Factory Explorer, Knowledge Panel, Copilot.

Requisitos no funcionales
- Desacoplado de AI-FACTORY: empaquetable y con API REST/CLI.
- Extensible: adaptadores para distintos formatos CAD y motores de simulación.
- Trazabilidad: todos los análisis generan `evidence` y `confidence`.

Interfaces e integración
- API REST para consulta/ingestión/export.
- Output standarizado (Factory Graph JSON + evidence bundle) para `IS_BACKOFFICE`.
- Autenticación via platform secrets (compatible con `openai_key_manager.py`).

Próximos pasos (MVP)
1. Reuse audit: identificar componentes existentes en `IS-BACKOFFICE` susceptibles de reutilizar (p. ej. Knowledge Hub, Simulation Center).
2. Prototipo de ingestión DWG → Factory Graph (POC con un plano simple).
3. Definir contrato JSON del `Factory Graph`.
