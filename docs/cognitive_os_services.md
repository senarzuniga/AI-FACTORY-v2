# Cognitive Operating System Services

This document defines the reusable Cognitive OS layer added to AI-FACTORY-v2.

## Scope
- Provide reusable platform services and APIs.
- Exclude industrial business modules from this layer.
- Maximize modularity, reuse and interoperability.

## Implemented Components
- AI Coordinator: event coordination across services.
- Agent Registry: catalog of autonomous agents.
- Mission Manager Core: mission lifecycle and decision workflow.
- Capability Graph: capability nodes and dependencies.
- Mission Graph: mission dependency graph and unblock checks.
- Platform Registry: external consumers and contracts.
- Evidence Runtime: evidence ingestion and storage.
- Truth Runtime: truth assertion support checks from evidence.
- Hypothesis Engine: proposal registration and status tracking.
- Scoring Engine: weighted engineering score.
- Enterprise Memory Core: reusable memory namespaces with persistence.
- Knowledge Core APIs: memory/evidence/truth reusable interface.
- Governance: policy gates for modularity/reuse/interoperability.
- SDK: simple Python facade for platform consumers.
- Autonomous Execution Framework: Hypothesis -> Scoring -> Selection -> Validation loop.

## API Surface
The service is exposed in:
- `api/routes/cognitive_os_api.py`

Base path:
- `/api/cognitive-os`

Main endpoints:
- `GET /health`
- `POST /agents/register`
- `POST /platforms/register`
- `POST /capabilities/upsert`
- `POST /missions/upsert`
- `POST /hypotheses/submit`
- `POST /knowledge/evidence`
- `POST /knowledge/truth`
- `POST /autonomous/run`
- `GET /state`

## External Consumption
Designed so systems like IS_BACKOFFICE and ING_DIGHUB can consume neutral APIs and SDK methods without coupling to industrial domain modules.
