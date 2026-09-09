# Platform Registry

| Platform | Role | Location | Status |
| --- | --- | --- | --- |
| AI_FACTORY | governance and orchestration root | main.py; orchestrator/ | PARTIAL |
| IS_BACKOFFICE | operational UI shell | dashboard/streamlit/; api/routes/ | PARTIAL |
| Collaborative Hub | operational service shell | api/routes/hub_api.py | PARTIAL |
| Mission Manager | workflow control concept | orchestrator + shell actions | PARTIAL |
| Knowledge Hub | knowledge and evidence layer | .forge/; docs/; data/learning/ | PARTIAL |
| Adaptive Sales Engine | linked commercial app | external workspace | PARTIAL |
| Transcripciones | transcript intake app | dashboard/streamlit/transcriptions_app.py | UNDER_DEVELOPMENT |
| Legacy AI Factory v2 | compatibility implementation | ai-factory-v2/ | PARTIAL |

## What the current platform exposes

- FastAPI operational endpoints at localhost:8000
- Technical dashboard at localhost:8501
- Human portal at localhost:8502
- Transcript intake at localhost:8503 (new panel)
- Orchestrator central HTML panel 

## Platform conclusion

The actual repo is not an industrial plant simulator or a digital twin implementation in the form described by the mission brief. Instead, it is a real AI orchestration and operations shell with a linked business app and evidence-based design artifacts.
