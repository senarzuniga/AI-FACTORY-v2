# Orphan Components

This review identifies components that are present and evidence-backed but not clearly user-visible or connected to a primary operational workflow.

| Component | Observation | Action |
| --- | --- | --- |
| orchestrator/core/*.py | Internal engine layer, no direct user route | KEEP |
| .forge/*.json | Schema and skill metadata; useful but not a user app | KEEP |
| ai-factory-v2/ | Historical implementation retained for compatibility | KEEP / MIGRATE |
| gnap/requests and gnap/results | Coordination artifacts no direct UI or app | KEEP |
| logs/cascade.log | Operational evidence; not a user app | KEEP |
| data/*.json | Operational data and metrics; useful as evidence and integration data | INTEGRATE |
| dashboard/orchestrator_panel.html | Central control panel; good operational shell | KEEP |
| dashboard/streamlit/hub_dashboard.py | Technical dashboard; useful but not a primary business app | KEEP |
| dashboard/streamlit/transcriptions_app.py | New operational app in progress | INTEGRATE |

## Orphan recommendation summary

- Keep internal engine modules because they are active architecture components.
- Integrate the transcriptions panel into the main shell.
- Keep evidence files and logs as operational artifacts.
- Do not create new menu entries for parser, memory, or config-only components.
