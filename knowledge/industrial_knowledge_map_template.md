# Industrial Knowledge Map — Plantilla

Campos por objeto de conocimiento
- `id`: identificador único
- `name`: nombre del objeto
- `category`: (e.g., Machine, Process, Metric, Standard)
- `description`: resumen y propósito
- `evidence`: lista de items con `source`, `type`, `snippet`, `confidence` (0-1)
- `confidence`: estimación agregada (0-1)
- `applicability`: contexto(s) donde aplica
- `source`: URL o repositorio
- `revision`: fecha y autor
- `related_missions`: lista de `mission_id`

Ejemplo
```
id: mach_0001
name: Corrugator Type A
category: Machine
description: High-speed corrugator used in primary forming.
evidence:
- source: vendor/manuals/corrugatorA.pdf
  type: manual
  snippet: "Max throughput 300 m/min"
  confidence: 0.9
confidence: 0.9
applicability: ["Plant Line 1", "High-volume"]
source: vendor/manuals/corrugatorA.pdf
revision: 2026-07-19 by Team
related_missions: ["M-001"]
```
