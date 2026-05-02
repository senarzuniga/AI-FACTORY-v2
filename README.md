# AI-FACTORY-v2

Autonomous multi-agent engineering orchestrator for GitHub repositories, featuring an advanced protocol stack for self-improving, distributed AI-driven development cycles.

## Architecture

The system has two layers:

### `orchestrator/` — Advanced Protocol Stack (active)

New top-level package implementing the full v2 protocol suite:

| Module | Protocol | Purpose |
|---|---|---|
| `core/epoch_protocol.py` | EPOCH | Baseline tracking, round management, auto-rollback |
| `core/imcts_engine.py` | I-MCTS | Introspective Monte Carlo Tree Search with failure analysis |
| `core/escher_loop.py` | Escher-Loop | Mutual agent co-evolution via numpy-backed scoring |
| `core/gnap_coordinator.py` | GNAP | Git-native job coordination with async worker pool |
| `core/coepg_trainer.py` | Co-EPG | Planning/grounding co-evolution feedback loop |
| `agents/planning_agent.py` | — | OpenAI-backed plan generation with offline fallback |
| `agents/grounding_agent.py` | — | Converts plans into concrete code changes |
| `agents/critic_agent.py` | — | Safety and quality validation gate |
| `agents/optimizer_agent.py` | — | Protocol-level tuning and hyperparameter adjustment |
| `memory/vector_store.py` | — | FAISS vector store with numpy fallback |
| `memory/experience_replay.py` | — | Prioritized experience replay buffer |
| `utils/config.py` | — | YAML config loader |
| `utils/logger.py` | — | Structured logging |
| `utils/github_client.py` | — | PyGithub wrapper with offline fallback |

### `ai-factory-v2/` — Legacy Production System

Original orchestrator with critic, generator, evaluator, executor, and analyzer agents. Preserved and untouched. Uses `launch.ps1` for Windows execution.

## Capabilities

**Legacy system (`ai-factory-v2/`)**
- Full repository analysis with structured summary and opportunity detection
- Multi-hypothesis generation with structural-diversity enforcement
- Scoring gates based on business impact, risk, complexity, maintainability, and scalability
- Critic validation with explicit risk tracking
- Safe execution guardrails for minimal, validated changes only
- Automatic fallback to the next safe hypothesis when a better-ranked one is blocked
- Automatic branch and pull-request creation with retry support for transient API failures
- Learning history and per-cycle audit reports

**Advanced stack (`orchestrator/`)**
- EPOCH-based rollback protection with baseline snapshotting
- I-MCTS for intelligent exploration of the hypothesis space with introspective failure analysis
- Escher-Loop mutual evolution: planning and grounding agents iteratively improve each other
- GNAP Git-native async job dispatch and distributed worker coordination
- Co-EPG co-training of planning vs. grounding quality signals
- FAISS-backed semantic memory with prioritized experience replay

## Repository structure

```
AI-FACTORY-v2/
├── main.py               # Entrypoint for the advanced stack
├── config.yaml           # Full protocol configuration
├── requirements.txt      # All dependencies
├── setup.sh              # Environment setup script
├── orchestrator/         # Advanced protocol stack (v2)
│   ├── core/             # EPOCH, I-MCTS, Escher-Loop, GNAP, Co-EPG
│   ├── agents/           # Planning, Grounding, Critic, Optimizer
│   ├── memory/           # VectorStore, ExperienceReplay
│   └── utils/            # Config, Logger, GitHubClient
├── gnap/                 # GNAP coordination artefacts
│   ├── manifest.json
│   ├── requests/
│   └── results/
├── ai-factory-v2/        # Legacy production orchestrator
│   ├── orchestrator.py
│   ├── agents/
│   ├── learning/
│   └── output/cycles/
└── tests/                # Test suite
```

## Getting started

### Advanced stack

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env        # Fill in OPENAI_API_KEY, GITHUB_TOKEN, etc.

# 4. Edit config.yaml to set target repository and protocol parameters

# 5. Run
python main.py
```

### Legacy system (Windows)

```powershell
cd ai-factory-v2
.\launch.ps1
```

## Configuration

All advanced-stack settings live in `config.yaml`:

- `epoch` — round budget, rollback threshold, baseline snapshot path
- `imcts` — exploration constant, simulation depth, failure memory size
- `escher_loop` — evolution rounds, mutation rate, diversity weight
- `gnap` — worker count, job timeout, git coordination branch
- `coepg` — feedback learning rate, co-evolution epochs
- `agents` — model names and temperature per agent role
- `memory` — FAISS index path, replay buffer capacity
- `github` — owner, repo, base branch, dry-run flag
- `monitoring` — log level, output directory

## Apply across all repositories

Set `github.repo` to `ALL` in `config.yaml` (or leave unset). Add owner filters and rollout caps to cover personal and organization repositories safely. The GitHub Action runs the same orchestration, scoring, critic, and PR rules across all selected repositories.

## Forge workflow assets

This repository now includes Forge-ready orchestration assets aligned with the full optimization workflow:

- `.forge/commands/orchestrate-all.md` — reusable master command sequence
- `.forge/ai-factory-v2.config.json` — repository-specific optimization targets and sync policy
- `optimize-agents.ps1` — one-command PowerShell workflow runner from repo root

Quick run options:

```bash
/orchestrate-all --force --yes --verbose
```

```powershell
.\optimize-agents.ps1
```

