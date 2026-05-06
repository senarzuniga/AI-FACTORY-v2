$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Host @"
╔════════════════════════════════════════════════════════════════════════════════╗
║ AI-FACTORY-V2 ORCHESTRATOR - MAXIMUM PERFORMANCE SELF-HEALING PROTOCOL       ║
╚════════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

$apps = Get-ChildItem (Split-Path -Parent $repoRoot) -Directory | Where-Object {
    $_.Name -ne "AI-FACTORY-v2" -and (
        (Test-Path (Join-Path $_.FullName "package.json")) -or
        (Test-Path (Join-Path $_.FullName "requirements.txt")) -or
        (Get-ChildItem $_.FullName -Filter "*.py" -File -ErrorAction SilentlyContinue | Select-Object -First 1)
    )
} | Select-Object -ExpandProperty Name

Write-Host "Found $($apps.Count) applications" -ForegroundColor Cyan
Write-Host ($apps -join ", ") -ForegroundColor DarkCyan

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

& $python (Join-Path $repoRoot "ultimate_orchestrator.py") --once

$dashboard = Join-Path $repoRoot "orchestrator_dashboard.html"
if (Test-Path $dashboard) {
    Start-Process $dashboard
    Write-Host "Dashboard opened: $dashboard" -ForegroundColor Green
}
