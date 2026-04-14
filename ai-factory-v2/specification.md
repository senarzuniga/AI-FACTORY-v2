# AI Factory v2 — System Specification

## 0. Purpose of the System

AI Factory v2 is an autonomous system inside a GitHub repository that:

- Analyses repository code
- Generates multiple solutions (hypotheses)
- Evaluates and scores alternatives
- Selects the best safe solution
- Executes incremental changes
- Opens Pull Requests automatically
- Learns from results

---

## 1. Fundamental Principle

> "Every improvement must result from hypothesis comparison and validation, never from a single direct decision."

---

## 2. System Architecture

The system is composed of **5 mandatory layers**.

### 2.1 Orchestrator (CORE SYSTEM)

Responsible for:

- Starting the cycle
- Coordinating agents
- Controlling execution flow
- Deciding whether to create a PR or reject a change

### 2.2 Analysis Agent (Planner / Scout)

Responsible for:

- Reading the complete repository
- Identifying areas for improvement
- Generating structured system context

Expected output:

- Repository summary
- Detected problems
- Improvement opportunities

### 2.3 Hypothesis Agent (Generator)

Responsible for:

- Generating a minimum of **2** and maximum of **5** solutions per problem
- Each solution must differ in approach

Mandatory rule:

- A single solution is not allowed

### 2.4 Evaluation Agent (Evaluator)

Responsible for:

- Comparing all hypotheses
- Assigning scores (0–10) across:

| Criterion | Description |
|-----------|-------------|
| Business Impact | Real value to the system |
| Technical Risk | Probability of failure (lower is better) |
| Complexity | Implementation difficulty (lower is better) |
| Maintainability | Future ease of maintenance |
| Scalability | Ability to grow with demand |

Rule:

- Only solutions with a high score can continue

### 2.5 Critic Agent

Responsible for:

- Detecting flaws in the best solution
- Evaluating production risks
- Blocking execution if there are high risks

Rule:

- If there is uncertainty → DO NOT execute

### 2.6 Executor Agent (PR Engine)

Responsible for:

- Applying minimal safe changes
- Creating a new branch
- Generating a Pull Request
- Documenting changes

Rule:

- Never commit directly to `main`

---

## 3. Operational Flow (MANDATORY)

Each cycle must follow **exactly** this flow:

```
1. Analyse repository
2. Detect opportunities
3. Generate multiple hypotheses
4. Evaluate and score hypotheses
5. Select the best safe option
6. Critical validation
7. If approved → execute change
8. Create Pull Request
9. Register learning
```

---

## 4. Hypothesis Engineering Rules

Each detected problem must satisfy:

- Minimum **2** hypotheses
- Each hypothesis must differ **structurally**
- Minor variations of the same idea are not permitted

Valid example:

- Architecture refactor
- Algorithm optimisation
- Logic simplification

Invalid example:

- Rename a variable
- Repeated micro-adjustment

---

## 5. Scoring System

Each hypothesis is evaluated with:

| Metric | Description |
|--------|-------------|
| Business Impact | Real value in the system (0–10) |
| Technical Risk | Probability of failure (0–10, lower is better) |
| Complexity | Implementation difficulty (0–10, lower is better) |
| Maintainability | Future ease of maintenance (0–10) |
| Scalability | Ability to scale (0–10) |

Composite score formula:

```
score = (
    business_impact * 2.0
    + (10 - technical_risk) * 1.5
    + (10 - complexity) * 0.5
    + maintainability * 1.0
    + scalability * 1.0
) / 6.0
```

---

## 6. Execution Rule

A solution **can only be executed** if it meets:

- `business_impact >= 7`
- `technical_risk <= 4`
- Positive evaluation from the Critic Agent

If not satisfied → discard or reiterate the cycle.

---

## 7. Iteration Principle (CASCADE LOOP)

```
INPUT → ANALYSIS → HYPOTHESES → SCORING → SELECTION → VALIDATION → EXECUTION → LEARNING
```

Rule:

- Never stop at the first valid solution
- Always compare alternatives

---

## 8. Change Control (GitHub)

All modifications must:

- Create a new branch
- Include a detailed description of the change
- Explain discarded hypotheses
- Justify the final decision

---

## 9. Security System

The system must avoid:

- Simultaneous mass changes
- Complete refactors without validation
- Modifications without sufficient context

Critical rule:

> "If there is uncertainty → DO NOT execute"

---

## 10. Learning System

After each PR, the system must record:

- Whether it was accepted or rejected
- Reason for the result
- Impact of the change

This feeds future decisions.

---

## 11. Mandatory Output of the System

Each cycle must produce:

1. Analysed repository
2. Detected problems
3. Generated hypotheses
4. Comparative scoring
5. Selected solution
6. Created PR or rejected action
7. Registered learning

---

## 12. Final Principle

> The system must behave like an autonomous senior engineering team that never makes decisions without comparison, validation, and critique.
