# ADR-2026-07-23: Next Mission Selection

Status: Accepted
Date: 2026-07-23
Decision makers: Independent CTO review

## Context
AI-FACTORY-v2 has strong strategic documentation but uneven implementation depth across governance, mission management runtime, testing reliability, and industrial digital twin execution.

## Decision
Select PLAN-A (Reliability and Governance First) as immediate continuation strategy.

## Why
1. Highest normalized Global Engineering Score in mission_portfolio/mission_portfolio_002_aeos.json.
2. Does not require irreversible architecture changes.
3. Can be executed under existing technical authority with low business approval overhead.
4. Unblocks M-001/M-004/M-006 execution with reduced delivery risk.

## Consequences
1. Short-term focus shifts from feature expansion to platform hardening.
2. Mission manager and governance become enforceable runtime components, not only documentation.
3. Industrial missions start from a stronger baseline and improved testability.

## Follow-up
1. Execute NXT-001 charter.
2. Gate next strategic missions using measurable DoD and automated checks.
