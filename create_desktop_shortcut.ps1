param(
    [string]$OrchestratorPath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2"
)

$ErrorActionPreference = "Stop"

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "AI-FACTORY-Orquestador.lnk"
$targetScript = Join-Path $OrchestratorPath "start_ecosystem.ps1"

if (-not (Test-Path $targetScript)) {
    throw "Missing start script: $targetScript"
}

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-ExecutionPolicy Bypass -NoExit -File `"$targetScript`""
$shortcut.WorkingDirectory = $OrchestratorPath
$shortcut.Description = "AI-FACTORY-v2 orchestrator launcher"
$shortcut.IconLocation = "powershell.exe,0"
$shortcut.Save()

Write-Host "Desktop shortcut created: $shortcutPath" -ForegroundColor Green
