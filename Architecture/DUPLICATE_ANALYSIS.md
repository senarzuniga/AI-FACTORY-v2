# Duplicate Analysis

This repository has a clear core/legacy split but no risky app duplication detected in a way that requires code removal. The main concerns are conceptual and integration overlap, not hard duplicate implementations.

| Component A | Component B | Similarity | Functional overlap | Recommended canonical component | Migration required | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| AI_FACTORY core (main.py + orchestrator/) | Legacy AI Factory v2 (ai-factory-v2/) | High | Both orchestrate AI flows and repository operations | orchestrator/ is canonical | Low | Medium |
| Collaborative Hub shell | IS_BACKOFFICE concept | High | User-facing operational layer | Collaborative Hub shell is canonical in this repo | Low | Low |
| AI_FACTORY brain | Operational menu | Low | Different roles: governance vs interface | Keep separated | None | Low |
| Streamlit portal | Technical dashboard | Medium | Both are UI surfaces for same ecosystem | Keep both; one for human portal and one for technical ops | None | Low |

## Duplicate detection outcome

- There are not two independent production apps implementing the same business function in this repo.
- The legacy folder has historical value and should remain as compatibility evidence.
- The main risk is role confusion: AI_FACTORY must not be presented as a second IS_BACKOFFICE shell.

## Recommended consolidation

- Keep AI_FACTORY as orchestration / governance.
- Keep collaborative hub as user-facing operational shell.
- Keep transcriptions panel as a visible application under the menu.
- Hide internal engines from the main menu.
