# Application Inventory

This repository contains a real operational stack around an intelligence orchestrator and a collaborative/human operating shell. The inventory below is evidence-based on the files currently in the repo.

## Canonical applications and active interfaces

| ID | Name | Type | Status | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| ai-factory-core | AI_FACTORY | APPLICATION | PARTIAL | README.md; main.py; orchestrator/main.py | Governance and orchestration root |
| legacy-ai-factory | Legacy AI Factory v2 | APPLICATION | PARTIAL | ai-factory-v2/orchestrator.py | Backward-compatible implementation |
| collaborative-hub | Collaborative Hub | APPLICATION | PARTIAL | api/routes/hub_api.py; dashboard/streamlit/*.py | Closest operational equivalent to IS_BACKOFFICE |
| transcriptions-app | Transcripciones | APPLICATION | UNDER_DEVELOPMENT | dashboard/streamlit/transcriptions_app.py | User-facing entry panel added for transcript intake |
| adaptive-sales-engine | Adaptive Sales Engine | APPLICATION | PARTIAL | config/linked_apps.json; dashboard/orchestrator_panel.html | Linked external app |
| knowledge-hub | Knowledge Hub | KNOWLEDGE | PARTIAL | .forge/knowledge_map.json; docs/ | Evidence and knowledge layer |
| orchestrator-core | Orchestrator Core | ENGINE | PARTIAL | orchestrator/core/*.py | Reusable intelligence engines |

## Operating model

- AI_FACTORY is the brain and governance layer.
- The collaborative hub is the operational shell and user-facing environment.
- Internal engines and agent modules remain internal and should not be promoted into the main IS_BACKOFFICE menu.
- Only the user-facing applications should appear in the main menu.

## User-visible menu candidates

The following are appropriate for the operational menu:

- Mission Manager (conceptual; orchestrator shell)
- Collaborative Hub / IS_BACKOFFICE shell
- Transcripciones
- Adaptive Sales Engine
- Knowledge Hub (admin/evidence view only)

The following remain hidden from primary user navigation:

- EPOCH protocol
- I-MCTS engine
- GNAP coordinator
- parsing utilities
- internal agents
- raw memory layers
- technical dashboards without user value

## Recommended canonical architecture

AI_FACTORY
↓
AI COORDINATOR / orchestrator core
↓
Mission Manager (operational workflow)
↓
Agents / Engines / Runtimes
↓
Collaborative Hub / IS_BACKOFFICE
↓
User / UI

## Evidence notes

The inventory above reflects files that are present and executable in the repo. It does not create duplicate application shells where a single operational service already exists.
