param(
    [ValidateSet("adaptive-sales-engine", "collaborative-hub-api", "all")]
    [string]$Target = "all",
    [string]$OrchestratorPath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2",
    [string]$AdaptiveSalesPath = "C:\Users\Inaki Senar\Documents\GitHub\adaptive-sales-engine"
)

$ErrorActionPreference = "Stop"
Set-Location $OrchestratorPath

Write-Host "[linked-deploy] target=$Target" -ForegroundColor Cyan

if ($Target -in @("adaptive-sales-engine", "all")) {
    if (-not (Test-Path $AdaptiveSalesPath)) {
        throw "Adaptive sales app path not found: $AdaptiveSalesPath"
    }

    Write-Host "[linked-deploy] adaptive-sales-engine found" -ForegroundColor Green
    python scripts/fix_connections.py | Out-Null
    python scripts/force_sync_data.py | Out-Null
    python scripts/cascade_agents.py | Out-Null
    python scripts/update_all_panels.py | Out-Null
    python scripts/verify_all.py | Out-Null
    Write-Host "[linked-deploy] adaptive-sales-engine integration pipeline completed" -ForegroundColor Green
}

if ($Target -in @("collaborative-hub-api", "all")) {
    $online = $false
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/hub/status" -UseBasicParsing -TimeoutSec 5
        $online = $response.StatusCode -eq 200
    } catch {
        $online = $false
    }

    if (-not $online) {
        if (-not (Test-Path "$OrchestratorPath\start-collaborative-hub.ps1")) {
            throw "start-collaborative-hub.ps1 not found"
        }
        powershell -ExecutionPolicy Bypass -File "$OrchestratorPath\start-collaborative-hub.ps1" -StartAPI | Out-Null
        Write-Host "[linked-deploy] collaborative-hub-api startup requested" -ForegroundColor Yellow
    } else {
        Write-Host "[linked-deploy] collaborative-hub-api already online" -ForegroundColor Green
    }
}

Write-Host "[linked-deploy] completed" -ForegroundColor Green
