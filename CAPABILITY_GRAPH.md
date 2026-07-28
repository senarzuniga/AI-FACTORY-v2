# AI-FACTORY-v2: Capability Graph & Dependency Map

**Date:** 2026-07-21  
**Purpose:** Visual representation of capabilities, strategic dependencies, and maturity progression

**Parallel Portfolio Addendum (2026-07-23):**
- Mission execution is now optimized by parallel work packages (critical path + independent high-value tracks).
- Blocked missions must spawn low-risk parallel deliverables (architecture, knowledge, documentation, models, UI mockups).
- Throughput-first policy: no idle engineering capacity while positive-value packages exist.
- Updated execution artifacts: `docs/aeos_review/Mission_Graph.json`, `mission_portfolio/mission_portfolio_003_parallel_30d.json`, `docs/aeos_review/Engineering_Investment_Portfolio_30d.json`.

---

## 1. CAPABILITY DEPENDENCY GRAPH

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        AUTONOMOUS ENGINEERING OPERATING SYSTEM                          │
│                                CAPABILITY ECOSYSTEM                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                                    ╔════════════════╗
                                    ║  Mission Mgr   ║
                                    ║  (Portfolio)   ║
                                    ╚════════╤═══════╝
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
            ╔═══════▼──────╗        ╔════════▼──────╗      ╔═════════▼─────╗
            ║ Governance   ║        ║  Decision     ║      ║ Learning &    ║
            ║ Engine       ║        ║  Intelligence ║      ║ Improvement   ║
            ║ (Quality)    ║◄───┐   ║  (Ranking)    ║      ║ (Feedback)    ║
            ╚═══════┬──────╝    │   ╚════════┬──────╘      ╚═════════┬─────╝
                    │           │           │                       │
        ┌───────────┼───────────┤           │                       │
        │           │           │           │                       │
    ╔───▼─────╗ ╔──▼────╗   ╔──▼──────╗   ╔▼────────╗         ┌────▼─────┐
    ║ Quality ║ ║ Arch  ║   ║ Data    ║   ║ Design  ║         │ Knowledge│
    ║Reviewer ║ ║Mgmt   ║   ║Synthesis║   ║Generator║         │ Memory   │
    ╚───┬─────╝ ╚──┬────╘   ╚────┬────╘   ╚───┬─────╘         └────┬─────┘
        │          │              │           │                     │
        │          │         ┌─────┴──────┬───┴──────┬──────────────┘
        │          │         │            │          │
        │    ╔─────▼─────╗  ╔▼──────────╗ │    ╔─────▼──────╗
        │    ║ Workflow  ║  ║Engineering║ │    ║ Enterprise ║
        │    ║Intelligence║  ║Intelligence║    ║ Digital    ║
        │    ╚─────┬─────╘  ╚▲──────────╘ │    ║ Twin       ║
        │          │        │             │    ╚─────┬──────╘
        │          │        │             │          │
        │    ╔─────▼─────┐  │    ╔────────▼────┐    │
        ├────┤Context    ├──┘    ║Industrial   │    │
        │    ║Layer      │        ║Knowledge   │    │
        │    ╚───────────┘        ║(Factory    │    │
        │                         ║Rules)      ║    │
        │                         ╚────────────╝    │
        │                                           │
        └─────────────────┬───────────────────────┬─┘
                          │                       │
                    ╔─────▼────────╗     ╔──────▼─────╗
                    ║ Autonomous   ║     ║ Capability ║
                    ║ Execution    ║     ║ Discovery  ║
                    ║ (Actions)    ║     ║ (Services) ║
                    ╚─────┬────────╝     ╚──────┬─────╘
                          │                     │
                          └──────┬──────────────┘
                                 │
                          ╔──────▼─────────╗
                          ║ Delivery       ║
                          ║ Engine         ║
                          ║ (Publishing)   ║
                          ╚────────────────╝
```

---

## 2. CAPABILITY MATURITY MATRIX

### Current State (2026-07)

```
Maturity Scale: 0 = Not Started | 1 = Conceptual | 2 = Partial | 3 = Active | 4 = Embedded | 5 = Autonomous

┌──────────────────────────┬─────────┬─────────┬─────────┬──────────────────────────────────────────┐
│ Capability               │ Current │ Target  │ Gap     │ Roadmap Path                             │
│                          │ (2026)  │ (2028)  │ Rating  │                                          │
├──────────────────────────┼─────────┼─────────┼─────────┼──────────────────────────────────────────┤
│ Mission Management       │ 2       │ 5       │ +3      │ T1 → T2 → T5 (M-001, M-009+)            │
│ Workflow Intelligence    │ 3       │ 5       │ +2      │ T1 → T5 (embedded in all)                │
│ Data Synthesis           │ 2       │ 4       │ +2      │ T2 → T3 → T4 (M-003, M-002)             │
│ Engineering Intelligence │ 2       │ 5       │ +3      │ T1 → T3 → T4 (M-007, M-005)             │
│ Decision Engine          │ 4       │ 5       │ +1      │ T1 → T2 (refinement only)                │
│ Design Generator         │ 2       │ 5       │ +3      │ T2 → T4 (M-012)                         │
│ Quality Reviewer         │ 3       │ 5       │ +2      │ T2 → T3 (M-009, M-010)                  │
│ Knowledge Memory         │ 2       │ 5       │ +3      │ T1 → T3 → T5 (M-004, M-015)             │
│ Digital Twin             │ 1       │ 5       │ +4      │ T1 → T3 (M-001, M-002, M-003, M-007)   │
│ Delivery Engine          │ 3       │ 4       │ +1      │ T2 → T3 (M-010)                         │
│ Autonomous Executor      │ 1       │ 5       │ +4      │ T2 → T4 (M-020)                         │
│ Governance               │ 1       │ 5       │ +4      │ T2 → T5 (M-009, M-010, M-011)          │
│ Industrial Knowledge     │ 0       │ 5       │ +5      │ T1 → T3 (M-004, domain ingestion)       │
│ Capability Discovery     │ 0       │ 5       │ +5      │ T4 → T5 (M-016, M-017, M-018)           │
│ Learning & Improvement   │ 1       │ 5       │ +4      │ T1 → T5 (M-015, continuous)             │
│ Architecture Management  │ 1       │ 5       │ +4      │ T2 → T4 (M-012, M-013)                  │
└──────────────────────────┴─────────┴─────────┴─────────┴──────────────────────────────────────────┘
```

---

## 3. STRATEGIC CAPABILITY LAYERS

### Layer Architecture and Evolution

```
TIER 5 (Q4 2027):
  Autonomous Engineering Organization
  ├── Cross-Domain Orchestration
  ├── Capability Marketplace
  ├── Organizational Learning
  └── Service Ecosystem (internal + external)

TIER 4 (Q3 2027):
  Autonomous CTO
  ├── Technology Strategy Automation
  ├── Architecture Design Synthesis
  ├── Tech Debt Management
  └── Learning Feedback Loops

TIER 3 (Q2 2027):
  Enterprise Digital Twin
  ├── Live Factory Synchronization
  ├── Real-Time Simulation
  ├── Predictive Analytics
  └── Autonomous Opportunities

TIER 2 (Q1 2027):
  Engineering Governance Engine
  ├── Quality Assurance Automation
  ├── Compliance Auditing
  ├── Governance Observatory
  └── Self-Correcting Feedback

TIER 1 (Q4 2026):
  AI Director
  ├── Mission Manager (Portfolio + Graph)
  ├── Decision Intelligence
  ├── Factory Graph + Digital Twin
  └── Engineering Copilot

TIER 0 (NOW):
  Operational Foundation
  ├── Hybrid Orchestration
  ├── Intent Detection
  ├── Multi-Agent Coordination
  └── Basic Validation
```

---

## 4. MISSION DEPENDENCY NETWORK

```
Legend:
  [M-###] = Mission ID
  → = Depends on
  ◆ = Foundational (no dependencies)

FOUNDATIONAL MISSIONS (Execute First):

  ◆ [M-001] Factory Graph Adapter
      └─→ [M-002] DWG/DXF Ingest
      └─→ [M-003] Simulation Integration
      └─→ [M-004] Evidence & Truth Sync
      └─→ [M-007] Bottleneck & WIP Analyzer

  ◆ [M-004] Evidence & Truth Sync
      └─→ [M-006] Engineering Copilot
      └─→ [M-010] Compliance Auditor

  ◆ [M-009] Quality Governance Framework
      └─→ [M-010] Compliance Auditor
      └─→ [M-011] Governance Observatory

DEPENDENT MISSIONS (Execute After Foundations):

  [M-003] Simulation Integration
      └─→ [M-005] AMR Opportunity Engine
      └─→ [M-007] Bottleneck & WIP Analyzer

  [M-006] Engineering Copilot (TIER 1 CAPSTONE)
      └─→ [M-012] Architecture Design Generator
      └─→ [M-013] Technology Selection Engine

  [M-010] Compliance Auditor
      └─→ [M-011] Governance Observatory
      └─→ [M-014] Tech Debt Predictor

STRATEGIC MISSIONS (Execute in TIER 2-5):

  [M-012] Architecture Design Generator
      └─→ [M-013] Technology Selection
      └─→ [M-015] Learning Feedback Loops

  [M-015] Learning Feedback Loops
      └─→ [M-016] Capability Discovery
      └─→ [M-017] Training Orchestrator
      └─→ [M-018] Service Marketplace

  [M-016-018] Ecosystem Missions
      └─→ [M-020] Cross-Domain Composer
      └─→ [M-019] Organization Observatory

CRITICAL PATH (Shortest Route to Full Autonomy):

  [M-001] (2w)
    ↓
  [M-004] (3w) + [M-003] (4w) parallel
    ↓
  [M-006] (8w) + [M-009] (4w) parallel
    ↓
  [M-012] (8w)
    ↓
  [M-013-015] (parallel development)
    ↓
  [M-016-019] (ecosystem)
    ↓
  FULL AUTONOMY

Total: ~23 months (2026-07 to 2027-06)
```

---

## 5. CAPABILITY REUSE & COMPOSITION

### Reusable Components from IS-BACKOFFICE

```
┌────────────────────────────────────────────────────────────────────────────┐
│ IS-BACKOFFICE → AI-FACTORY-v2 Adapter Strategy                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ✓ knowledge_hub/competitive_intel                                          │
│   ├─→ EvidenceStore (fact versioning, provenance)                         │
│   ├─→ TruthEngine (contradiction detection, resolution)                   │
│   └─→ Maps to: [M-004] Evidence & Truth Sync                              │
│                                                                             │
│ ✓ ingetrans-reel-simulator                                                │
│   ├─→ RC1 runner (headless, YAML scenarios)                               │
│   ├─→ Fidelity framework (scenario templates)                             │
│   └─→ Maps to: [M-003] Simulation Integration                             │
│                                                                             │
│ ✓ plant_simulator                                                          │
│   ├─→ SimulationEngine (flow models)                                       │
│   ├─→ ScenarioOptimizer (multi-scenario support)                          │
│   └─→ Maps to: [M-003] + [M-007]                                          │
│                                                                             │
│ ✓ document_analysis                                                        │
│   ├─→ Multi-format parser (PDF, images, OCR)                              │
│   ├─→ Structured output (JSON/CSV)                                        │
│   └─→ Maps to: [M-004] Evidence ingestion                                  │
│                                                                             │
│ ✓ backoffice/reporting                                                    │
│   ├─→ ReportGenerator (HTML/JSON/PDF)                                     │
│   ├─→ Executive templates (offer, investment roadmap)                     │
│   └─→ Maps to: [M-008] Executive Offer Generator                          │
│                                                                             │
│ ✓ backoffice/analytics                                                    │
│   ├─→ Statistical engines (bottleneck, WIP analysis)                      │
│   ├─→ Insight scoring (opportunity ranking)                               │
│   └─→ Maps to: [M-007] + [M-005]                                          │
│                                                                             │
│ ✓ backoffice/graph (GraphStore)                                           │
│   ├─→ In-memory CRUD operations                                            │
│   ├─→ Timeline and statistics functions                                    │
│   └─→ Maps to: [M-001] Factory Graph persistence                          │
│                                                                             │
│ ✓ assets/layout_*.json + canvas_renderer.py                               │
│   ├─→ Layout JSON schema (existing, proven)                               │
│   ├─→ Canvas rendering for visualization                                  │
│   └─→ Maps to: [M-001] sample data + UI                                   │
│                                                                             │
│ ✓ streamlit UI components                                                 │
│   ├─→ Reusable pages and panels                                            │
│   ├─→ Data visualization templates                                         │
│   └─→ Maps to: [M-006] Engineering Copilot UI                             │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘

Adapter Strategy:
  • Create /tools/is_backoffice_adapter/ directory
  • Implement DTO layers (AI-FACTORY entities ↔ IS-BACKOFFICE models)
  • Add integration tests for each component
  • Maintain separation of concerns (no direct coupling)
```

---

## 6. CAPABILITY DISCOVERY FRAMEWORK

### Self-Discovery Over Time

```
Phase 1 (T0-T1): Manual Capability Inventory
├── Identify existing agents: 9 core agents
├── Map to 12 engineering domains
├── Score maturity on 0-5 scale
└── Result: This document

Phase 2 (T1-T2): Semi-Automated Discovery
├── Capability registry (JSON schema)
├── Automated performance metrics collection
├── Dependency graph generation
└── Result: Real-time capability dashboard

Phase 3 (T2-T3): Autonomous Discovery
├── Service introspection APIs
├── Self-describing capabilities (OpenAPI, gRPC)
├── Automated integration testing
└── Result: Self-documenting ecosystem

Phase 4 (T3-T4): Marketplace Intelligence
├── Internal service pricing (cost-benefit analysis)
├── External service discovery
├── Skill taxonomy and proficiency scoring
└── Result: Autonomous service selection

Phase 5 (T4-T5): Organizational Learning
├── Decision outcome tracking
├── Historical pattern analysis
├── Capability evolution scoring
└── Result: Self-improving organization
```

---

## 7. STRATEGIC CAPABILITIES SCORECARD

### Comparative Analysis: Current vs. Target

```
CAPABILITY INVESTMENT PRIORITIZATION

Priority 1 (IMMEDIATE - Critical Path):
├── [M-001] Factory Graph Adapter          | Engineering: ★★★★★ | Business: ★★★★☆ | Risk: ★☆☆☆☆
├── [M-004] Evidence & Truth Sync          | Engineering: ★★★★☆ | Business: ★★★★☆ | Risk: ★☆☆☆☆
├── [M-006] Engineering Copilot            | Engineering: ★★★★★ | Business: ★★★★★ | Risk: ★★☆☆☆
└── [M-009] Governance Framework           | Engineering: ★★★★★ | Business: ★★★★☆ | Risk: ★☆☆☆☆

Priority 2 (SEQUENTIAL - Next Wave):
├── [M-003] Simulation Integration         | Engineering: ★★★★☆ | Business: ★★★★☆ | Risk: ★★☆☆☆
├── [M-007] Bottleneck Analyzer            | Engineering: ★★★★☆ | Business: ★★★★☆ | Risk: ★☆☆☆☆
├── [M-010] Compliance Auditor             | Engineering: ★★★★☆ | Business: ★★★★☆ | Risk: ★★☆☆☆
└── [M-012] Design Generator               | Engineering: ★★★★★ | Business: ★★★★☆ | Risk: ★★★☆☆

Priority 3 (STRATEGIC - Year 2):
├── [M-002] DWG/DXF Pipeline               | Engineering: ★★★☆☆ | Business: ★★★★★ | Risk: ★★★☆☆
├── [M-013] Technology Selection           | Engineering: ★★★★★ | Business: ★★★★☆ | Risk: ★★★☆☆
├── [M-015] Learning Feedback Loops        | Engineering: ★★★★☆ | Business: ★★★★☆ | Risk: ★★☆☆☆
└── [M-016] Capability Discovery           | Engineering: ★★★★☆ | Business: ★★★☆☆ | Risk: ★★★☆☆

QUICK WINS (Low Effort, High Value):
├── [M-004] Evidence & Truth (3 weeks, $7K, huge future unlock)
├── [M-008] Executive Report Generator (3 weeks, $6K, immediate revenue)
└── [M-011] Governance Observatory (3 weeks, $8K, compliance reporting)
```

---

## 8. FUTURE CAPABILITY HORIZONS

### Beyond TIER 5: Emergent Capabilities

```
YEAR 2 CAPABILITIES (2028):

[M-021] Cross-Organizational Intelligence
  • Multi-tenant capability federation
  • Shared knowledge markets
  • Competitive intelligence synthesis
  • Engineering value: ★★★★☆ | Business: ★★★★★

[M-022] Predictive Engineering
  • Outcome prediction (before execution)
  • Risk forecasting (months ahead)
  • Opportunity discovery (market-aware)
  • Engineering value: ★★★★★ | Business: ★★★★★

[M-023] Regulatory Automation
  • Real-time compliance reporting
  • Audit trail generation
  • Policy interpretation
  • Engineering value: ★★★☆☆ | Business: ★★★★★

[M-024] Supply Chain Orchestration
  • Vendor capability matching
  • Procurement automation
  • Just-in-time planning
  • Engineering value: ★★★★☆ | Business: ★★★★☆

[M-025] Customer Experience Co-Design
  • Customer feedback synthesis
  • Design iteration automation
  • Feature prioritization
  • Engineering value: ★★★☆☆ | Business: ★★★★★
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-21  
**Next Review:** After M-001 completion  

