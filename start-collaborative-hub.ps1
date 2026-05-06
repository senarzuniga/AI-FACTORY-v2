param(
    [string]$HubPath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2",
    [switch]$FixGit,
    [switch]$StartAPI,
    [switch]$StartDashboard,
    [switch]$StartHumanPortal,
    [switch]$TestSharePoint
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $HubPath)) {
    throw "Hub path not found: $HubPath"
}

Set-Location $HubPath
New-Item -ItemType Directory -Path "logs" -Force | Out-Null

$apiPort = 8000
$dashboardPort = 8501
$humanPortalPort = 8502

function Write-Step {
    param([string]$Message, [ConsoleColor]$Color = [ConsoleColor]::Cyan)
    Write-Host "[hub] $Message" -ForegroundColor $Color
}

function Test-PortInUse {
    param([int]$Port)
    $match = netstat -ano | Select-String -Pattern ":$Port\s+.*LISTENING"
    return ($null -ne $match)
}

function Start-ServiceWindow {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port
    )

    if (Test-PortInUse -Port $Port) {
        Write-Step "$Name skipped. Port $Port already in use." Yellow
        return
    }

    Start-Process powershell -WorkingDirectory $HubPath -ArgumentList @(
        "-NoExit",
        "-Command",
        $Command
    ) | Out-Null

    Write-Step "$Name started on port $Port" Green
}

if ($FixGit) {
    Write-Step "Applying git compatibility settings for Windows paths" Yellow
    git config core.longpaths true
    git config core.autocrlf true
    git config --add safe.directory "$HubPath"
    Write-Step "Git settings updated" Green
}

if ($TestSharePoint) {
    $configPath = Join-Path $HubPath "config\collaborative_hub.json"
    $sharepointUrl = "https://ingecart.sharepoint.com/sites/Adaptive-Sales-Core"
    if (Test-Path $configPath) {
        try {
            $cfg = Get-Content -Path $configPath -Raw | ConvertFrom-Json
            if ($cfg.urls.sharepoint) { $sharepointUrl = $cfg.urls.sharepoint }
        } catch {
            Write-Step "Could not parse config/collaborative_hub.json; using default SharePoint URL" Yellow
        }
    }

    Write-Step "SharePoint target URL: $sharepointUrl" Yellow
    try {
        $hostName = ([System.Uri]$sharepointUrl).Host
        Resolve-DnsName $hostName -ErrorAction Stop | Out-Null
        Write-Step "DNS OK for $hostName" Green
    } catch {
        Write-Step "DNS FAIL for SharePoint host. Tenant may not exist or URL is wrong." Red
    }
}

$singleMode = $StartAPI -or $StartDashboard -or $StartHumanPortal

if ($StartAPI -or -not $singleMode) {
    Start-ServiceWindow -Name "Hub API" -Port $apiPort -Command "python -m uvicorn api.routes.hub_api:app --host 0.0.0.0 --port $apiPort"
}

if ($StartDashboard -or -not $singleMode) {
    Start-ServiceWindow -Name "Technical Dashboard" -Port $dashboardPort -Command "streamlit run dashboard/streamlit/hub_dashboard.py --server.port $dashboardPort"
}

if ($StartHumanPortal -or -not $singleMode) {
    Start-ServiceWindow -Name "Human Interaction Portal" -Port $humanPortalPort -Command "streamlit run dashboard/streamlit/human_interaction_portal.py --server.port $humanPortalPort"
}

Write-Host ""
Write-Step "Access URLs" Cyan
Write-Host "- Human Portal : http://localhost:$humanPortalPort"
Write-Host "- Dashboard    : http://localhost:$dashboardPort"
Write-Host "- API          : http://localhost:$apiPort"
Write-Host "- API Health   : http://localhost:$apiPort/hub/status"
