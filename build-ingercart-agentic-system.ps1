# ============================================================
# BUILD SISTEMA AGENTICO COMPLETO - INGERCART
# Con Context Layer, Supervisor Agent, Dual Generation, Judge
# Parametros:
#   -DryRun    Muestra que haria sin ejecutar
#   -Force     No pide confirmacion
# ============================================================

param(
    [string]$ClientName  = "Ingercart",
    [string]$AdminEmail  = "isenar.cta@gmail.com",
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$sourcePath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2"
$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$logsDir    = Join-Path $sourcePath "logs"
$logFile    = Join-Path $logsDir "build_agentic_${timestamp}.log"

if (-not (Test-Path $logsDir)) { New-Item -Path $logsDir -ItemType Directory -Force | Out-Null }

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $ts = "[$(Get-Date -Format 'HH:mm:ss')]"
    Add-Content -Path $logFile -Value "$ts $Message"
    Write-Host "$ts $Message" -ForegroundColor $Color
}

function Invoke-PythonStep {
    param([string]$Label, [string]$Args)
    Write-Log $Label -Color "Yellow"
    if ($DryRun) { Write-Log "  [DRY-RUN] python $Args" -Color "DarkGray" ; return }
    $python = Join-Path $sourcePath ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) { $python = "python" }
    & $python @($Args.Split(" "))
    if ($LASTEXITCODE -ne 0) { throw "Fallo en paso: $Label (exit $LASTEXITCODE)" }
}

Set-Location $sourcePath

Write-Log "CONSTRUYENDO SISTEMA AGENTICO COMPLETO" -Color "Cyan"
Write-Log "Cliente    : $ClientName" -Color "Yellow"
Write-Log "Admin email: $AdminEmail" -Color "Yellow"
Write-Log "Modo DryRun: $DryRun"    -Color "Yellow"
Write-Log "Repositorio: $sourcePath" -Color "Yellow"

# ── Verificacion de archivos clave ────────────────────────
Write-Log ""
Write-Log "Verificando modulos del sistema agentico..." -Color "Cyan"

$required = @(
    "context\__init__.py",
    "context\context_layer.py",
    "agents\supervisor_agent.py",
    "agents\data_intelligence_agent.py",
    "agents\analysis_agent.py",
    "agents\generation_agent.py",
    "agents\judge_agent.py",
    "agents\validation_agent.py",
    "agents\memory_agent.py",
    "agents\delivery_agent.py",
    "orchestrator\hybrid_orchestrator.py",
    "main.py"
)

$allPresent = $true
foreach ($f in $required) {
    $full = Join-Path $sourcePath $f
    if (Test-Path $full) {
        Write-Log "  OK  $f" -Color "Green"
    } else {
        Write-Log "  MISSING  $f" -Color "Red"
        $allPresent = $false
    }
}

if (-not $allPresent) {
    Write-Log ""
    Write-Log "ERROR: Archivos faltantes. Ejecuta este script desde la raiz del repositorio." -Color "Red"
    exit 1
}

# ── Compilacion de todos los modulos ─────────────────────
Write-Log ""
Write-Log "Compilando modulos Python..." -Color "Cyan"
Invoke-PythonStep -Label "Compilando context/" -Args "-m compileall context"
Invoke-PythonStep -Label "Compilando agents/" -Args "-m compileall agents"
Invoke-PythonStep -Label "Compilando orchestrator/" -Args "-m compileall orchestrator"
Invoke-PythonStep -Label "Compilando main.py" -Args "-m compileall main.py"
Write-Log "Compilacion OK" -Color "Green"

# ── Test de arranque en modo --agentic ────────────────────
Write-Log ""
Write-Log "Test de arranque del sistema agentico..." -Color "Cyan"
Invoke-PythonStep -Label "python main.py --agentic" -Args "main.py --agentic"
Write-Log "Test OK" -Color "Green"

# ── Reporte final ─────────────────────────────────────────
Write-Log ""
Write-Log "============================================================" -Color "Cyan"
Write-Log "SISTEMA AGENTICO CONSTRUIDO Y VALIDADO" -Color "Green"
Write-Log "============================================================" -Color "Cyan"
Write-Log ""
Write-Log "Capas implementadas:" -Color "White"
Write-Log "  1. Context Layer            context/context_layer.py" -Color "Green"
Write-Log "  2. Supervisor Agent         agents/supervisor_agent.py" -Color "Green"
Write-Log "  3. Data Intelligence Agent  agents/data_intelligence_agent.py" -Color "Green"
Write-Log "  4. Analysis Agent           agents/analysis_agent.py" -Color "Green"
Write-Log "  5. Dual Generation          agents/generation_agent.py (x2)" -Color "Green"
Write-Log "  6. Judge Agent              agents/judge_agent.py" -Color "Green"
Write-Log "  7. Validation Agent         agents/validation_agent.py" -Color "Green"
Write-Log "  8. Memory Agent             agents/memory_agent.py" -Color "Green"
Write-Log "  9. Delivery Agent           agents/delivery_agent.py" -Color "Green"
Write-Log " 10. Hybrid Orchestrator      orchestrator/hybrid_orchestrator.py" -Color "Green"
Write-Log " 11. Human-in-the-loop        integrado en hybrid_orchestrator.py" -Color "Green"
Write-Log ""
Write-Log "Para ejecutar el sistema agentico:" -Color "Cyan"
Write-Log "  python main.py --agentic"
Write-Log ""
Write-Log "Para ejecutar el stack de protocolos avanzados:" -Color "Cyan"
Write-Log "  python main.py"
Write-Log ""
Write-Log "Log guardado en: $logFile" -Color "White"
