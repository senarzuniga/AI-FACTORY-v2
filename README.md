# AI-FACTORY-v2

Autonomous multi-agent engineering orchestrator for GitHub repositories.

## Included capabilities

- Full repository analysis with structured summary and opportunity detection
- Multi-hypothesis generation with structural-diversity enforcement
- Scoring gates based on business impact, risk, complexity, maintainability, and scalability
- Critic validation with explicit risk tracking
- Safe execution guardrails for minimal, validated changes only
- Automatic fallback to the next safe hypothesis when a better-ranked one is blocked
- Automatic branch and pull-request creation with retry support for transient API failures
- Learning history and per-cycle audit reports

## Run locally on Windows

1. Copy the environment template and fill in your credentials.
2. Run the launcher from the app folder.
3. Use dry-run mode when you want analysis without PR creation.

## Apply the rules across all repositories

- Leave the repository target unset or set it to ALL.
- Optionally set owner filters and rollout caps to cover your personal and organization repositories safely.
- The GitHub Action will then run the same orchestration, scoring, critic, and PR rules across the selected repositories.

