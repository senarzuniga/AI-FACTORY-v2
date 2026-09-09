# Execution Backlog

| Priority | Mission | Value | Status | Notes |
| --- | --- | --- | --- | --- |
| P1 | Formalize the canonical application boundary between AI_FACTORY and IS_BACKOFFICE | High | OPEN | Required to avoid duplication |
| P1 | Consolidate the app registry into a single authoritative inventory | High | OPEN | Necessary for runtime mapping and menu integration |
| P1 | Expose only operational apps in the main UI menu | High | OPEN | Prevents internal engine leakage |
| P1 | Integrate the Transcripciones panel as visible entry point in the shell | High | OPEN | Explicit requirement from this mission |
| P2 | Document platform and capability registries in a canonical format | Medium | OPEN | Needed for architecture clarity |
| P2 | Add a contract model for health, API, and app ownership | Medium | OPEN | Supports operational governance |
| P2 | Add end-to-end UI/API checks for the main menu and the app shell | Medium | OPEN | Important validation step |
| P3 | Add backend support for transcript processing beyond manual intake | Medium | OPEN | Future milestone |
| P3 | Align the legacy implementation with the active orchestrator as a clearly documented compatibility layer | Medium | OPEN | Reduces confusion |
| P3 | Consolidate knowledge assets into a single Knowledge Hub interface | Medium | OPEN | Useful but not required for immediate menu exposure |

## Mission alignment

This backlog is intentionally aligned with the architecture described in the mission: AI_FACTORY as the brain, IS_BACKOFFICE as the operational shell, and user-visible applications as the interfaces for end users.

## Recommended next action

Integrate the main menu shell and ensure the transcript panel is visible while keeping engines and raw technical components hidden from direct user navigation.
