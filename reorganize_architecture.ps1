param(
    [string]$OrchestratorPath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2",
    [string]$AppPath = "C:\Users\Inaki Senar\Documents\GitHub\adaptive-sales-engine",
    [bool]$TeamsIntegration = $true,
    [bool]$LauncherPanel = $true,
    [bool]$FixConnections = $true,
    [string]$OutputReport = "architecture_reorganization_report.txt"
)

$ErrorActionPreference = "Stop"

function Add-ReportLine {
    param([System.Collections.Generic.List[string]]$Buffer, [string]$Line)
    $Buffer.Add($Line)
}

$report = New-Object 'System.Collections.Generic.List[string]'
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Add-ReportLine -Buffer $report -Line ("=" * 90)
Add-ReportLine -Buffer $report -Line "ARCHITECTURE REORGANIZATION REPORT"
Add-ReportLine -Buffer $report -Line ("=" * 90)
Add-ReportLine -Buffer $report -Line "Timestamp: $timestamp"
Add-ReportLine -Buffer $report -Line "Orchestrator: $OrchestratorPath"
Add-ReportLine -Buffer $report -Line "Main app: $AppPath"
Add-ReportLine -Buffer $report -Line ""

if (-not (Test-Path $OrchestratorPath)) {
    throw "Orchestrator path not found: $OrchestratorPath"
}

Set-Location $OrchestratorPath

$expectedFiles = @(
    "dashboard/orchestrator_panel.html",
    "scripts/fix_connections.py",
    "start_ecosystem.ps1"
)

Add-ReportLine -Buffer $report -Line "[1] Artifact validation"
foreach ($item in $expectedFiles) {
    if (Test-Path $item) {
        Add-ReportLine -Buffer $report -Line "  OK  $item"
    } else {
        Add-ReportLine -Buffer $report -Line "  MISSING  $item"
    }
}
Add-ReportLine -Buffer $report -Line ""

if ($FixConnections) {
    Add-ReportLine -Buffer $report -Line "[2] Connection repair"
    $fixOutput = & python scripts/fix_connections.py 2>&1
    foreach ($line in $fixOutput) {
        Add-ReportLine -Buffer $report -Line "  $line"
    }
    Add-ReportLine -Buffer $report -Line ""
}

Add-ReportLine -Buffer $report -Line "[3] Data pipeline execution"
$commands = @(
    "python scripts/force_sync_data.py",
    "python scripts/cascade_agents.py",
    "python scripts/update_all_panels.py",
    "python scripts/verify_all.py"
)

foreach ($cmd in $commands) {
    Add-ReportLine -Buffer $report -Line "  > $cmd"
    $output = & powershell -NoProfile -Command $cmd 2>&1
    foreach ($line in $output) {
        Add-ReportLine -Buffer $report -Line "    $line"
    }
}
Add-ReportLine -Buffer $report -Line ""

Add-ReportLine -Buffer $report -Line "[4] Architecture roles"
Add-ReportLine -Buffer $report -Line "  - AI-FACTORY-v2: orchestrator and coordination hub"
Add-ReportLine -Buffer $report -Line "  - adaptive-sales-engine: main daily business application"
if ($TeamsIntegration) {
    Add-ReportLine -Buffer $report -Line "  - Teams integration: enabled"
}
if ($LauncherPanel) {
    Add-ReportLine -Buffer $report -Line "  - Launcher panel: dashboard/orchestrator_panel.html"
}
Add-ReportLine -Buffer $report -Line ""

Add-ReportLine -Buffer $report -Line "[5] Start command"
Add-ReportLine -Buffer $report -Line "  ./start_ecosystem.ps1 -OrchestratorPath `"$OrchestratorPath`" -AppPath `"$AppPath`" -RunDataPipeline"
Add-ReportLine -Buffer $report -Line ""

$reportPath = Join-Path $OrchestratorPath $OutputReport
$report | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host "Reorganization report generated:" -ForegroundColor Green
Write-Host "  $reportPath"
