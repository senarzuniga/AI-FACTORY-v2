# AI_FACTORY Architecture Map

## Layered architecture

AI_FACTORY
↓
AI COORDINATOR
↓
MISSION MANAGER
↓
AGENTS / ENGINES / RUNTIMES
↓
APPLICATIONS
↓
IS_BACKOFFICE / COLLABORATIVE HUB
↓
USER

## Components observed in this repository

### AI_FACTORY

- main.py
- config.yaml
- orchestrator/main.py
- orchestrator/core/*
- orchestrator/agents/*
- orchestrator/memory/*

Purpose:
- Govern execution rules
- Handle optimization cycles
- Coordinate agent and protocol decisions
- Keep evidence and learning artifacts

### AI COORDINATOR

- orchestrator/core/gnap_coordinator.py
- orchestrator/core/epoch_protocol.py
- orchestrator/core/imcts_engine.py
- orchestrator/core/escher_loop.py
- orchestrator/core/coepg_trainer.py

Purpose:
- Coordinate work queues
- Choose and evaluate strategies
- Manage improvement loops

### Mission Manager

- role is represented by orchestration and workflow logic around the app shell
- operational workflows are surfaced through the collaborative hub and portal views

Purpose:
- translate high-level goals into action plans
- manage business and engineering execution

### Applications

- Adaptive Sales Engine (external linked app)
- Collaborative Hub / IS_BACKOFFICE shell
- Transcripciones app
- legacy AI Factory runtime

### IS_BACKOFFICE / operational shell

- api/routes/hub_api.py
- dashboard/streamlit/hub_dashboard.py
- dashboard/streamlit/human_interaction_portal.py
- dashboard/orchestrator_panel.html
- start-collaborative-hub.ps1

Purpose:
- provide a user-facing operational layer
- expose health, portal, and status actions
- connect human operators to the underlying AI ecosystem

## Knowledge Flow

Repository files -> configuration -> orchestrator -> agents -> evidence -> learning -> dashboard / portal views

## Evidence Flow

Code + logs + JSON data + docs -> knowledge assets -> validation -> operational summaries -> status panel

## Data Flow

User intent / repo context -> AI_FACTORY decision loop -> memory + agents -> outputs -> API + dashboards -> action execution

## API Flow

Browser / user -> Streamlit portal -> FastAPI hub API -> actions pool -> agent or linked app -> status / dashboard response

## Mission Flow

Goal -> orchestration -> plan -> execution -> validation -> report -> learning capture

## UI Flow

Dashboard panel -> app selection -> operational UI -> linked app / portal -> API health and status -> operator feedback

## Design principle used

AI_FACTORY does not become a second copy of IS_BACKOFFICE. The intelligence layer remains the brain; the collaborative hub remains the operator environment.
