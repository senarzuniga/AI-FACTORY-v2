param(
    [string]$OrchestratorPath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2",
    [string]$AppPath = "C:\Users\Inaki Senar\Documents\GitHub\adaptive-sales-engine",
    [string]$TeamsUrl = "https://teams.live.com/l/community/FEA5JSTpd_3FAKh9gI",
    [switch]$SkipBrowser,
    [switch]$SkipTeams,
    [switch]$RunDataPipeline
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Text, [ConsoleColor]$Color = [ConsoleColor]::Cyan)
    Write-Host "[ecosystem] $Text" -ForegroundColor $Color
}

function Test-PortInUse {
    param([int]$Port)
    return (Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue) -ne $null
}

function Start-Window {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port
    )

    if ($Port -gt 0 -and (Test-PortInUse -Port $Port)) {
        Write-Step "$Name skipped (port $Port already in use)" Yellow
        return
    }

    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $Command) | Out-Null
    Write-Step "$Name started" Green
}

if (-not (Test-Path $OrchestratorPath)) {
    throw "Orchestrator path not found: $OrchestratorPath"
}

Set-Location $OrchestratorPath
Write-Step "Launching orchestrator + app ecosystem"

# 1) Start static panel server
$panelCommand = "cd '$OrchestratorPath' ; python -m http.server 8080"
Start-Window -Name "Orchestrator panel server" -Command $panelCommand -Port 8080

# 2) Start Hub API
$hubCommand = "cd '$OrchestratorPath' ; python -m uvicorn api.routes.hub_api:app --host 0.0.0.0 --port 8000"
Start-Window -Name "Hub API" -Command $hubCommand -Port 8000

# 3) Start streamlit dashboards if available
if (Test-Path "$OrchestratorPath\dashboard\streamlit\hub_dashboard.py") {
    $dashCommand = "cd '$OrchestratorPath' ; streamlit run dashboard/streamlit/hub_dashboard.py --server.port 8501"
    Start-Window -Name "Technical dashboard" -Command $dashCommand -Port 8501
}

if (Test-Path "$OrchestratorPath\dashboard\streamlit\human_interaction_portal.py") {
    $humanCommand = "cd '$OrchestratorPath' ; streamlit run dashboard/streamlit/human_interaction_portal.py --server.port 8502"
    Start-Window -Name "Human portal" -Command $humanCommand -Port 8502
}

# 4) Start adaptive-sales-engine when available
if (Test-Path $AppPath) {
    if (Test-Path "$AppPath\package.json") {
        $appCommand = "cd '$AppPath' ; npm run dev"
        Start-Window -Name "Adaptive sales engine" -Command $appCommand -Port 5173
    } elseif (Test-Path "$AppPath\requirements.txt") {
        $appCommand = "cd '$AppPath' ; python app.py"
        Start-Window -Name "Adaptive sales engine (python)" -Command $appCommand -Port 5000
    } else {
        Write-Step "App path exists but start command is unknown. Opened folder in VS Code." Yellow
        Start-Process code -ArgumentList "$AppPath" | Out-Null
    }
} else {
    Write-Step "App path not found: $AppPath" Red
}

# 5) Run connection repair and optional data pipeline
Write-Step "Running connection check"
python scripts/fix_connections.py

if ($RunDataPipeline) {
    Write-Step "Running data sync + cascade + panel update + verification"
    python scripts/force_sync_data.py
    python scripts/cascade_agents.py
    python scripts/update_all_panels.py
    python scripts/verify_all.py
}

# 6) Open browser shortcuts
if (-not $SkipBrowser) {
    Start-Process "http://localhost:8080/dashboard/orchestrator_panel.html" | Out-Null
    Start-Process "http://localhost:8501" | Out-Null
}

if (-not $SkipTeams) {
    Start-Process $TeamsUrl | Out-Null
}

Write-Host ""
Write-Step "Ecosystem started" Green
Write-Host "- Orchestrator panel : http://localhost:8080/dashboard/orchestrator_panel.html"
Write-Host "- Hub API            : http://localhost:8000/hub/status"
Write-Host "- Dashboard          : http://localhost:8501"
Write-Host "- Human portal       : http://localhost:8502"
Write-Host "- Sales app          : dynamic (usually http://localhost:5173 or http://localhost:8082)"
Write-Host "- Teams              : $TeamsUrl"
