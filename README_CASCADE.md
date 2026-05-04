# Cascade Orchestrator

Autonomous cascade orchestration for AI-FACTORY-v2 with:

- Trigger-driven multi-agent cascade execution.
- Background self-learning and workflow auto-tuning.
- Agent evolution hooks.
- Controlled autonomous deployment (safe by default).

## Quick Start (Windows)

1. Run setup:

```powershell
./setup_cascade.ps1
```

2. Trigger cascade:

```powershell
./.venv/Scripts/python.exe ./cascade_orchestrator.py "improve code quality and reliability"
```

3. Monitor events in another terminal:

```powershell
./.venv/Scripts/python.exe ./monitor_cascade.py
```

## CLI

```powershell
# run
python cascade_orchestrator.py "fix security validations"

# run with context
python cascade_orchestrator.py "add feature: jwt auth" --context '{"candidate_files":["main.py"]}'

# show learning summary
python cascade_orchestrator.py --learn

# show latest statuses
python cascade_orchestrator.py --status

# show one status
python cascade_orchestrator.py --status <cascade_id>
```

## Deployment Controls

Git deployment is disabled by default.

Enable controlled deployment:

```powershell
python cascade_orchestrator.py "improve retries" --enable-git-deploy
```

Enable push to origin:

```powershell
python cascade_orchestrator.py "improve retries" --enable-git-deploy --allow-push
```

Enable linked app deployment hooks from config/linked_apps.json:

```powershell
python cascade_orchestrator.py "sync linked apps" --enable-linked-deploy
```

## Notes

- Generated artifacts are written under generated/.
- Learning state is persisted under data/learning/.
- Event stream is written to logs/cascade.log.
