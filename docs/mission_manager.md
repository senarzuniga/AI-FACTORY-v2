# Mission Manager — Diseño inicial

Propósito
- Gestionar el ciclo de vida de misiones de ingeniería por encima del `HybridOrchestrator` existente.
- Centralizar planificación, misión-graph, hipótesis, métricas de ingeniería y evidencia.

Principales responsabilidades
- Lifecycle: creación, planificación, ejecución, revisión, cierre.
- Mission Graph: grafo de dependencias y desbloqueos entre misiones.
- Hypothesis Management: generar, versionar y evaluar hipótesis por misión.
- Scoring & Selection: computar puntuaciones de ingeniería y seleccionar alternativas.
- Knowledge & Evidence: enlazar artefactos de conocimiento y evidencia empírica.
- Observatory: métricas agregadas de plataforma y madurez.

Integración con arquitectura actual
- Se despliega como componente superior (orquestador de misiones). No sustituye a `HybridOrchestrator`.
- `HybridOrchestrator` seguirá ejecutando pipelines; Mission Manager decide qué misiones y con qué parámetros invocarlas.
- Integración mediante API interna/colas: Mission Manager envía triggers y provee `mission_context` al HybridOrchestrator.

Datos y modelos principales
- `Mission` (ver [schemas/mission_graph_schema.json](schemas/mission_graph_schema.json)): id, objetivos, valor, dependencias, riesgos, estado, métricas, evidencia.
- `Hypothesis`: alternativas con métricas de evaluación y resultado de scoring.
- `KnowledgeRef`: referencias a objetos en el Knowledge Map.

Operaciones iniciales (MVP)
1. Inventario de reutilización sobre `IS-BACKOFFICE` (auditoría de módulos y modelos reutilizables).
2. Definir API mínima para crear/leer/actualizar misiones y listar dependencias.
3. Implementar UI ligera (panel de misiones) en `dashboard/streamlit/` para visualización de Mission Graph.

Próximos pasos recomendados
- Autorizar auditoría completa de reutilización (local o clonado de `IS-BACKOFFICE`).
- Aceptar el esquema de Mission Graph o proponer cambios.
- Definir criterios iniciales para `Engineering Score` (ver `docs/engineering_scoring.md`).
