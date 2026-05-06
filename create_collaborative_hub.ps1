param(
    [string]$WorkspacePath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2",
    [string]$Client = "Ingercart",
    [string]$AdminEmail = "isenar.cta@gmail.com",
    [string]$ManagerEmail = "sales@ingecart.es",
    [string]$AdminChiefEmail = "administracion@ingecart.es",
    [string]$FixGitSpaces = "true",
    [string]$CreateSharePointHub = "true",
    [string]$CreateTeamsCore = "true",
    [string]$CreateAgentEcosystem = "true",
    [string]$CreateHumanInteractionEnv = "true",
    [string]$Deploy = "true"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $WorkspacePath)) {
    throw "Workspace path does not exist: $WorkspacePath"
}

$logsDir = Join-Path $WorkspacePath "logs"
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
$logFile = Join-Path $logsDir ("create_collaborative_hub_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

function Write-Log {
    param([string]$Message, [ConsoleColor]$Color = [ConsoleColor]::White)
    $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $Message
    Add-Content -Path $logFile -Value $line
    Write-Host $line -ForegroundColor $Color
}

function New-RequiredPath {
    param([string]$PathToCreate)
    New-Item -ItemType Directory -Path $PathToCreate -Force | Out-Null
}

function ConvertTo-Bool {
    param([string]$Value)
    if ($null -eq $Value) { return $false }
    $normalized = $Value.Trim().ToLowerInvariant()
    return @("1", "true", "yes", "y", "on") -contains $normalized
}

function Invoke-GitWorkspace {
    param([string[]]$GitArgs)
    & git -C "$WorkspacePath" @GitArgs
    if ($LASTEXITCODE -ne 0) {
        $joined = $GitArgs -join " "
        throw ("Git command failed: git -C '{0}' {1}" -f $WorkspacePath, $joined)
    }
}

Write-Log "Creating collaborative hub for $Client" Cyan
Write-Log "Workspace: $WorkspacePath" Yellow
Write-Log "Admin: $AdminEmail | Manager: $ManagerEmail | Admin chief: $AdminChiefEmail" Yellow

New-RequiredPath (Join-Path $WorkspacePath "docs")
New-RequiredPath (Join-Path $WorkspacePath "config")
New-RequiredPath (Join-Path $WorkspacePath "api\routes")
New-RequiredPath (Join-Path $WorkspacePath "dashboard\streamlit")

$fixGitSpacesEnabled = ConvertTo-Bool $FixGitSpaces
$createSharePointHubEnabled = ConvertTo-Bool $CreateSharePointHub
$createTeamsCoreEnabled = ConvertTo-Bool $CreateTeamsCore
$createAgentEcosystemEnabled = ConvertTo-Bool $CreateAgentEcosystem
$createHumanInteractionEnvEnabled = ConvertTo-Bool $CreateHumanInteractionEnv
$deployEnabled = ConvertTo-Bool $Deploy

if ($fixGitSpacesEnabled) {
    Write-Log "Applying git space-safe configuration" Magenta
    Invoke-GitWorkspace -GitArgs @("config", "core.longpaths", "true")
    Invoke-GitWorkspace -GitArgs @("config", "core.autocrlf", "true")
    Invoke-GitWorkspace -GitArgs @("config", "--add", "safe.directory", "$WorkspacePath")
    Invoke-GitWorkspace -GitArgs @("fetch")
    Write-Log "Git fetch completed using quoted -C path" Green
}

if ($createSharePointHubEnabled) {
    Write-Log "SharePoint hub docs are available at docs/SHAREPOINT_SETUP_RECIPE.md" Green
}

if ($createTeamsCoreEnabled) {
    Write-Log "Teams core docs are available at docs/TEAMS_CORE_SETUP.md" Green
}

if ($createAgentEcosystemEnabled) {
    Write-Log "Agent ecosystem endpoints available at api/routes/hub_api.py" Green
}

if ($createHumanInteractionEnvEnabled) {
    Write-Log "Human interaction portal available at dashboard/streamlit/human_interaction_portal.py" Green
}

$quickAccessPath = Join-Path $WorkspacePath "docs\QUICK_ACCESS.md"
@"
# Collaborative Hub Quick Access

## Local URLs
- Human Interaction Portal: http://localhost:8502
- Technical Dashboard: http://localhost:8501
- Hub API: http://localhost:8000
- Hub API Health: http://localhost:8000/hub/status

## Startup Commands
```powershell
.\start-collaborative-hub.ps1
.\start-collaborative-hub.ps1 -StartHumanPortal
.\start-collaborative-hub.ps1 -StartDashboard
.\start-collaborative-hub.ps1 -StartAPI
```

## External URLs
- SharePoint: https://ingecart.sharepoint.com/sites/Adaptive-Sales-Core
- Teams: https://teams.microsoft.com/l/team/19:ingecart_core
"@ | Set-Content -Path $quickAccessPath -Encoding UTF8
Write-Log "Quick access guide created" Green

if ($deployEnabled) {
    Write-Log "Deploy flag enabled. Starting local services through start-collaborative-hub.ps1" Cyan
    & (Join-Path $WorkspacePath "start-collaborative-hub.ps1") -HubPath "$WorkspacePath"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start collaborative hub services"
    }
}

Write-Log "Collaborative hub creation completed" Green
Write-Log "Log file: $logFile" White
