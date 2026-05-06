# Complete Agent Optimization Script
# For AI-FACTORY-v2 Orchestrator Repository

$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2"
Set-Location $repoPath

Write-Host "Starting Complete Agent Optimization for AI-FACTORY-v2" -ForegroundColor Cyan

function Invoke-ForgeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    Write-Host $Label -ForegroundColor Yellow
    Write-Host "  $Command" -ForegroundColor DarkGray
    # Run in the active shell so this script works in both VS Code terminal and standalone PowerShell.
    Invoke-Expression $Command
}

# Phase 1: Initialization
Invoke-ForgeCommand -Label "Phase 1: Initializing Forge Framework..." -Command "/factory-init --force --create-agents --setup-actor-framework"

# Phase 2: Agent Discovery
Invoke-ForgeCommand -Label "Phase 2: Discovering All Agents..." -Command "/scan-agents --depth=recursive --discover-interactions --map-dependencies"

# Phase 3: Performance Baseline
Invoke-ForgeCommand -Label "Phase 3: Establishing Performance Baseline..." -Command "/benchmark-agents --iterations=100 --metrics=latency,accuracy,resource-usage"

# Phase 4: Full Pipeline Execution
Invoke-ForgeCommand -Label "Phase 4: Running Complete Agent Pipeline..." -Command "@product-owner /optimize-vision --repository=AI-FACTORY-v2 --create-improvement-roadmap"
Invoke-ForgeCommand -Label "Phase 4: Running Complete Agent Pipeline..." -Command "@architect /restructure-agents --target=performance --generate-optimized-schemas"
Invoke-ForgeCommand -Label "Phase 4: Running Complete Agent Pipeline..." -Command "@planner /create-optimization-milestones --agents=all --deadline=immediate"
Invoke-ForgeCommand -Label "Phase 4: Running Complete Agent Pipeline..." -Command "@technical-writer /refine-agent-specs --from-performance-audit"
Invoke-ForgeCommand -Label "Phase 4: Running Complete Agent Pipeline..." -Command "@engineer /implement-agent-optimizations --changeset=complete --auto-commit"
Invoke-ForgeCommand -Label "Phase 4: Running Complete Agent Pipeline..." -Command "@quality-assurance /validate-agent-performance --regression-test=full"

# Phase 5: Cross-Repository Sync
Invoke-ForgeCommand -Label "Phase 5: Synchronizing Across Repositories..." -Command "/sync-agent-configs --source=AI-FACTORY-v2 --targets=all --force-overwrite"

# Phase 6: Performance Optimization
Invoke-ForgeCommand -Label "Phase 6: Applying Performance Optimizations..." -Command "/optimize-agent-performance --mode=aggressive --targets=inference,memory,response"
Invoke-ForgeCommand -Label "Phase 6: Applying Performance Optimizations..." -Command "/vectorize-agents --embedding-model=text-embedding-3-small --cache-strategy=persistent"
Invoke-ForgeCommand -Label "Phase 6: Applying Performance Optimizations..." -Command "/enable-parallel-agents --max-concurrent=10 --task-queue=redis --auto-scale"

# Phase 7: Learning Loop + Validation + Deployment
Invoke-ForgeCommand -Label "Phase 7: Activating Continuous Learning..." -Command "/agent-learning-loop --source=interaction-logs --pattern=performance-degradation --auto-correct"
Invoke-ForgeCommand -Label "Phase 7: Activating Continuous Learning..." -Command "/optimize-prompts --metric=success-rate --threshold=0.85 --auto-deploy"
Invoke-ForgeCommand -Label "Phase 7: Validating Ecosystem..." -Command "/validate-ecosystem --tests=performance,integration,compatibility --generate-report"
Invoke-ForgeCommand -Label "Phase 7: Deploying Optimized Agents..." -Command "/deploy-agents --environment=production --strategy=canary --rollback-on-failure"
Invoke-ForgeCommand -Label "Phase 7: Enabling Monitoring..." -Command "/monitor-agents --duration=24h --alert-on-degradation --auto-remediate"
Invoke-ForgeCommand -Label "Phase 7: Scheduling Auto-Improvement PRs..." -Command "/auto-improvement-pr --schedule=hourly --reviewer=@quality-assurance --auto-merge-if-passing"

Write-Host "Optimization workflow completed." -ForegroundColor Green
