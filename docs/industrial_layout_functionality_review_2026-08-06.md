# Industrial Layout Intelligence Platform Review (2026-08-06)

## Executive Snapshot

- Status: partial and improving.
- Major improvement completed: DWG/DXF upload is now functional at UI level (Ready/Loaded state and file input flow).
- Core backend pipeline exists for CADParser -> Factory Graph -> Knowledge Graph -> Digital Twin -> Simulation -> Optimization.
- Main gaps: production-grade DWG conversion pipeline, richer industrial semantic recognition, scenario comparison UX, and converter benchmark knowledge integration.

## Functional Review Against Target Flow

## 1. Layout Import

- Supported now:
- DWG (UI upload + backend attempt via industrial-intelligence endpoint).
- DXF (UI upload + backend attempt; local load fallback).
- JSON (UI upload + backend parsing attempt).
- SVG (UI upload + backend parsing attempt).
- PDF vector (UI upload local capture; parser pipeline still pending).
- Future placeholders:
- IFC.
- DGN.

Gaps:

- DWG still depends on converter command/provider for real geometric ingestion.
- PDF/SVG runtime conversion path not productionized.
- IFC/DGN providers missing.

## 2. Geometric Interpretation

- Implemented:
- `cognitive_os/industrial_layout.py` creates normalized entities, bounds, centers, relations and derived metrics.
- `cognitive_os/layout_import_framework.py` has pluggable providers and failover.

Gaps:

- No robust wall/column CAD topology reconstruction for all CAD standards.
- No strict georeferencing contract (plant coordinate reference, datum management).

## 3. Intelligent Recognition

- Implemented:
- Heuristic semantic classification by markers (machine, conveyor, warehouse, wip, amr_route, etc).

Gaps:

- No model-based industrial classifier trained on corrugated equipment signatures.
- No confidence calibration by equipment family/version.

## 4. Factory Graph

- Implemented:
- Nodes/edges generated with relation rules.
- Connectivity and distances are produced.

Gaps:

- Need persistent graph storage adapter and query API for advanced traversal.

## 5. Knowledge Graph

- Implemented:
- Assertions and relationship artifacts generated from interpretation pipeline.

Gaps:

- Live integration with ERP/manuals/historical projects not complete.
- Enterprise Knowledge Hub synchronization still partial.

## 6. Digital Twin

- Implemented:
- Snapshot object generation, scenario placeholders, and state payloads.

Gaps:

- Live synchronization with telemetry and plant states pending.

## 7. Simulation

- Implemented:
- Deterministic KPI simulation baseline (material flow, OEE, ROI, bottlenecks, buffer occupancy).

Gaps:

- No high-fidelity discrete-event runtime calibration loop yet.
- Scenario model for corrugator + converter logistics needs stronger parameterization.

## 8. Automatic Engineering

- Implemented:
- Optimization runtimes and recommendation structures exist.

Gaps:

- Recommendation scoring must include validated machine constraints and logistics feasibility checks.

## 9. Scenario Comparison

- Implemented:
- Architecture supports scenarios in simulation and versioning.

Gaps:

- No user-facing A/B/C comparison dashboard with KPI deltas and investment view.

## 10. Automatic Documentation

- Implemented:
- Executive status and mission/governance reports are auto-generated.

Gaps:

- Need direct generation pipeline for commercial proposals and board-ready simulation packs.

## Intralogistics Focus (AMR + WIP + JIT)

High-priority business logic for corrugated plants:

- WIP cells next to converters when height storage is limited.
- No forklift aisles in AMR-dominated zones increases usable floor ratio.
- JIT sequencing can reduce converter waiting and corrugator starvation coupling.

Critical KPIs to track:

- Corrugator starvation events per week.
- Converter feed SLA (% jobs fed on-time).
- Internal transport lead time (request-to-delivery seconds).
- AMR utilization (%), queueing and deadlocks.
- WIP age distribution (hours) and turnover/day.
- Forklift km/day residual after AMR migration.
- OEE delta points and annual output delta.

Reference benchmark anchors used:

- INGECART digital twin benchmark (forklift vs INGETRANS):
- +6 OEE points.
- -87% starvation events.
- +4.2M m annual production.
- ~EUR309k operating savings/year.
- AMR technology benchmark data from IS-BACKOFFICE reports:
- multi-criteria scores for fleet orchestration options.

## Corrugated Converters Knowledge Base (Created)

Created assets:

- `knowledge/corrugated_equipment/converter_equipment_catalog_v1.json`
- `knowledge/corrugated_equipment/simulation_hypotheses_corrugated_v1.json`

Coverage includes:

- FFG and RDC machine families.
- Typical capacities and throughput ranges.
- Changeover benchmarks.
- Maintenance requirements and common failures.
- Indicative CAPEX/retrofit/service ranges.
- AMR/WIP compatibility factors for simulation scoring.

## Recommended Maintenance Packages

- Basic package (legacy RDC/FFG):
- PM monthly.
- Annual alignment and die-system overhaul.
- Spare kit level 1.

- Performance package (mid-generation FFG):
- PM biweekly critical sections.
- Servo and registration health checks.
- Spare kit level 2 with fast-wear print/cut parts.

- High-automation package (high-speed + robotic palletizing):
- Condition-based maintenance + vibration/thermal checks.
- Quarterly software/safety validation.
- Spare kit level 3 with critical electronics and gripper modules.

## Priority Backlog for Productization

1. Add production DWG converter adapter with controlled provider selection.
2. Add PDF/SVG vector-to-intermediate conversion service.
3. Add machine-aware semantic classifier for corrugated lines.
4. Add scenario comparison API and dashboard (A/B/C with ROI/OEE/risk deltas).
5. Integrate equipment catalog scoring directly into simulation runtime.
6. Add DS Smith-like calibration profile presets for annual throughput envelopes.

## Data Governance Notes

- Prices and capacities in catalog are indicative ranges for simulation hypotheses.
- Investment decisions require OEM quotation and site-specific calibration.
- Keep benchmark sources versioned and evidence-linked in enterprise memory.
