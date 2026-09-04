# Mission Model Specification (Production Stabilization)

## 1. Mission Model Specification
Canonical source of truth:
- Schema: `schemas/canonical_mission_model.schema.json`
- Runtime model: `cognitive_os/models.py` (`MissionNode` and sub-entities)

The canonical mission model includes:
- Mission
- Objective
- Strategic Alignment
- Business Value
- Engineering Value
- Knowledge Value
- Hypothesis Portfolio
- Scoring Matrix
- Work Packages
- Dependencies
- Capabilities
- Evidence
- Deliverables
- Risks
- KPIs
- Milestones
- Lessons Learned
- Mission State
- Mission History
- Mission Evolution
- Mission Score
- Mission ROI
- Mission Confidence
- Mission Traceability
- Mission Knowledge Assets

## 2. Mission Lifecycle
Lifecycle stages:
1. `draft`
2. `planned`
3. `active`
4. `validation`
5. `completed`
6. `archived`

Alternative flow:
- `active` -> `blocked` -> `active`

The lifecycle is enforced by `MissionManagerCore` and captured in `mission_history` + `mission_evolution`.

## 3. Mission State Machine
Machine definition:
- `schemas/mission_state_machine.json`

Transition drivers:
- Dependency readiness
- Work package completion
- Governance policy pass/fail
- Scoring threshold pass/fail

## 4. Mission APIs
OpenAPI-compatible endpoints under `/api/cognitive-os`:
- `POST /missions/upsert`
- `POST /hypotheses/submit`
- `POST /mission-model/evaluate`
- `GET /mission-model/production-ready`
- `POST /autonomous/run`
- `GET /state`

Mission model gating:
- Autonomous execution is blocked until mission model reaches Production Ready.

## 5. Mission Persistence Model
Primary persistence:
- Enterprise Memory namespace `mission_model` for canonical selection + readiness state.
- Canonical missions persisted as JSON via migration outputs in `data/missions/`.

Migration outputs:
- `data/missions/canonical_missions_v1.json`
- `data/missions/canonical_missions_legacy_archive.json`
- `data/missions/canonical_mission_migration_report.json`

## 6. Mission Knowledge Model
Knowledge integration points:
- `KnowledgeCoreAPIs` for mission-linked evidence/truth knowledge.
- `mission_traceability` links sources, dependencies, and evidence.
- `mission_knowledge_assets` captures reusable assets and provenance.

## 7. Mission Metrics
Core metrics:
- `mission_score`
- `mission_roi`
- `mission_confidence`
- `scoring_matrix.*`
- KPI progress (target/current)

Selection metric:
- Mission Model selector computes weighted score over modularity, reuse, interoperability, migration safety, governance strength, and operational complexity.

## 8. Mission Governance
Governance gate prevents mission validation when:
- Industrial business modules are touched by canonical core actions.
- Modularity/reuse/interoperability gains are absent.

Governance implementation:
- `cognitive_os/governance.py`

## 9. Mission Testing Strategy
Recommended test layers:
1. Unit tests for canonical model normalization (`MissionNode.__post_init__`)
2. Unit tests for mission model selector scoring and winner selection
3. Unit tests for mission lifecycle transitions and history/evolution updates
4. API contract tests for mission endpoints
5. Migration snapshot tests (source fixtures -> canonical + archive integrity)
6. Regression tests ensuring autonomous run is blocked until production-ready mission model

## 10. Migration Strategy
Migration script:
- `scripts/migrate_mission_model.py`

Principles:
- Lossless preservation of legacy mission payloads in archive file.
- Canonical projection generated without deleting historical fields.
- Dependency links preserved and merged from mission graph edges.

Execution:
1. Run migration script.
2. Validate canonical schema compliance.
3. Validate record counts and source coverage in migration report.
4. Enable production mode only after mission model selection returns `production_ready=true`.
