# AI Factory v2 -- Windows Setup
# Run this ONCE to:
#   1. Create a desktop shortcut (double-click = manual run)
#   2. Register a Task Scheduler task (auto-run at every Windows login)
#
# Usage (run as your normal user -- no admin required):
#   Right-click -> "Run with PowerShell"
#   OR from a PS terminal: .\setup_windows.ps1

$ErrorActionPreference = "Stop"

$LaunchScript = Join-Path $PSScriptRoot "launch.ps1"
$TaskName     = "AI Factory v2"
$Delay        = "PT3M"

if (-not (Test-Path $LaunchScript)) {
    Write-Error "launch.ps1 not found at $LaunchScript. Run this from inside ai-factory-v2/."
    exit 1
}

Write-Host ""
Write-Host "  AI Factory v2 -- Windows Setup" -ForegroundColor Cyan
Write-Host "  ================================" -ForegroundColor Cyan
Write-Host ""

# -- 1. Desktop shortcut -----------------------------------------------------
$DesktopPath  = [System.Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "AI Factory v2.lnk"

$WshShell                  = New-Object -ComObject WScript.Shell
$Shortcut                  = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath       = "powershell.exe"
$Shortcut.Arguments        = "-ExecutionPolicy Bypass -NoProfile -File `"$LaunchScript`""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.WindowStyle      = 1
$Shortcut.Description      = "Run AI Factory v2 autonomous engineering cycle"

$pyCmd = Get-Command python -ErrorAction SilentlyContinue
$pyExe = if ($pyCmd) { $pyCmd.Source } else { $null }
if ($pyExe) {
    $Shortcut.IconLocation = "$pyExe,0"
} else {
    $Shortcut.IconLocation = "powershell.exe,0"
}

$Shortcut.Save()
Write-Host "[1/2] Desktop shortcut created:" -ForegroundColor Green
Write-Host "      $ShortcutPath" -ForegroundColor White

# -- 2. Task Scheduler -- run at logon ----------------------------------------
$psArgs = "-ExecutionPolicy Bypass -NonInteractive -WindowStyle Hidden -File `"$LaunchScript`" -NoWait"

$Action = New-ScheduledTaskAction `
    -Execute  "powershell.exe" `
    -Argument $psArgs `
    -WorkingDirectory $PSScriptRoot

$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Trigger.Delay = $Delay

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit  (New-TimeSpan -Hours 1) `
    -RestartCount        2 `
    -RestartInterval     (New-TimeSpan -Minutes 5) `
    -MultipleInstances   IgnoreNew `
    -StartWhenAvailable

$Principal = New-ScheduledTaskPrincipal `
    -UserId   $env:USERNAME `
    -LogonType Interactive `
    -RunLevel  Limited

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName    $TaskName `
    -Action      $Action `
    -Trigger     $Trigger `
    -Settings    $Settings `
    -Principal   $Principal `
    -Description "AI Factory v2 autonomous cycle -- runs 3 min after login" `
    -Force | Out-Null

Write-Host "[2/2] Startup task registered: '$TaskName'" -ForegroundColor Green
Write-Host "      Fires 3 minutes after every login (hidden window)." -ForegroundColor White

Write-Host ""
Write-Host "  Setup complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "   1. Fill in .env at the repo root with your credentials." -ForegroundColor White
Write-Host "   2. Double-click 'AI Factory v2' on your desktop for a manual run." -ForegroundColor White
Write-Host "   3. The system will run automatically on every login." -ForegroundColor White
Write-Host ""

# Auto-create .env from example if it does not exist yet
$RepoRoot   = Split-Path -Parent $PSScriptRoot
$EnvExample = Join-Path $RepoRoot ".env.example"
$EnvFile    = Join-Path $RepoRoot ".env"
if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "  Created .env from .env.example -- opening in Notepad..." -ForegroundColor DarkGray
    Start-Process notepad.exe $EnvFile
}
