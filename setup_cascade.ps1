param(
    [string]$RepoPath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2"
)

$ErrorActionPreference = "Stop"
Set-Location $RepoPath

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Cascade Orchestrator Setup" -ForegroundColor Cyan
Write-Host "One Trigger -> Cascade -> Self-Learning -> Controlled Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

New-Item -ItemType Directory -Path "data\learning" -Force | Out-Null
New-Item -ItemType Directory -Path "generated" -Force | Out-Null
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
New-Item -ItemType Directory -Path "config" -Force | Out-Null

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install numpy pytest pytest-cov

if (-not (Test-Path "data\learning\learning_data.json")) {
@'
{
  "successful_patterns": [],
  "failure_patterns": [],
  "performance_metrics": {},
  "workflow_optimizations": []
}
'@ | Out-File -FilePath "data\learning\learning_data.json" -Encoding UTF8
}

if (-not (Test-Path "config\linked_apps.json")) {
@'
{
  "apps": [
    {
      "name": "adaptive-sales-engine",
      "deploy_command": "powershell -ExecutionPolicy Bypass -File scripts/deploy_linked_apps.ps1 -Target adaptive-sales-engine"
    },
    {
      "name": "collaborative-hub-api",
      "deploy_command": "powershell -ExecutionPolicy Bypass -File scripts/deploy_linked_apps.ps1 -Target collaborative-hub-api"
    }
  ]
}
'@ | Out-File -FilePath "config\linked_apps.json" -Encoding UTF8
}

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Run example:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\python.exe .\cascade_orchestrator.py \"improve code quality and resilience\"" -ForegroundColor White
