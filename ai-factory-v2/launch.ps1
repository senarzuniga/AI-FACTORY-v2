# AI Factory v2 -- Windows Launcher
# Loads .env, finds Python, installs deps, runs one orchestrator cycle.

param(
    [switch]$NoWait
)

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "AI Factory v2"

$RepoRoot     = Split-Path -Parent $PSScriptRoot
$AppDir       = $PSScriptRoot
$EnvFile      = Join-Path $RepoRoot ".env"
$ReqFile      = Join-Path $AppDir   "requirements.txt"
$Orchestrator = Join-Path $AppDir   "orchestrator.py"

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host "           AI FACTORY v2  LAUNCHER" -ForegroundColor Cyan
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host ""

# -- Load .env ----------------------------------------------------------------
if (Test-Path $EnvFile) {
    Write-Host "[+] Loading environment from $EnvFile" -ForegroundColor Green
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and $line -notmatch '^\s*#' -and $line -match '^([^=]+)=(.*)$') {
            $key   = $Matches[1].Trim()
            $value = $Matches[2].Trim().Trim('"').Trim("'")
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
} else {
    Write-Warning ".env not found at $EnvFile"
    Write-Warning "Copy .env.example to .env and fill in your credentials."
    if (-not $NoWait) {
        Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    exit 1
}

# -- Validate required variables ----------------------------------------------
if (-not [System.Environment]::GetEnvironmentVariable("GITHUB_REPOSITORY", "Process")) {
    [System.Environment]::SetEnvironmentVariable("GITHUB_REPOSITORY", "ALL", "Process")
    Write-Host "[i] GITHUB_REPOSITORY not set -- defaulting to ALL" -ForegroundColor Yellow
}

$missing = @()
foreach ($var in @("GITHUB_TOKEN", "OPENAI_API_KEY")) {
    if (-not [System.Environment]::GetEnvironmentVariable($var, "Process")) {
        $missing += $var
    }
}
if ($missing.Count -gt 0) {
    Write-Error "Missing required variables in .env: $($missing -join ', ')"
    if (-not $NoWait) {
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    exit 1
}

# -- Find Python --------------------------------------------------------------
$candidates = @(
    (Join-Path $RepoRoot ".venv\Scripts\python.exe"),
    (Join-Path $RepoRoot "venv\Scripts\python.exe"),
    "python",
    "python3"
)
$python = $null
foreach ($c in $candidates) {
    try {
        $out = & $c --version 2>&1
        if ($LASTEXITCODE -eq 0) { $python = $c; break }
    } catch { }
}
if (-not $python) {
    Write-Error "Python not found. Install Python 3.10+ and add it to PATH."
    if (-not $NoWait) { $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") }
    exit 1
}
Write-Host "[+] Python: $python" -ForegroundColor Green

# -- Install / update dependencies --------------------------------------------
Write-Host "[+] Checking dependencies..." -ForegroundColor Green
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet -r $ReqFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies."
    if (-not $NoWait) { $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") }
    exit 1
}

# -- Run orchestrator ---------------------------------------------------------
Write-Host "[+] Starting AI Factory v2 cycle..." -ForegroundColor Green
Write-Host ""
Set-Location $AppDir
& $python $Orchestrator
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "  Cycle completed successfully." -ForegroundColor Green
} elseif ($exitCode -eq 1) {
    Write-Host "  Cycle completed -- change rejected (no PR created)." -ForegroundColor Yellow
} else {
    Write-Host "  Cycle ended with error code $exitCode." -ForegroundColor Red
}

if (-not $NoWait) {
    Write-Host "`n  Press any key to close..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

exit $exitCode
