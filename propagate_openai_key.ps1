param(
    [switch]$Force
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$masterKeyPath = Join-Path $repoRoot ".openai-master-key.json"
$githubRoot = Split-Path -Parent $repoRoot

Write-Host "=== OPENAI API KEY PROPAGATION ===" -ForegroundColor Cyan

if (-not (Test-Path $masterKeyPath)) {
    Write-Error "Master key file not found at $masterKeyPath"
    exit 1
}

$masterData = Get-Content $masterKeyPath -Raw | ConvertFrom-Json
$apiKey = [string]$masterData.openai.api_key
if ([string]::IsNullOrWhiteSpace($apiKey) -or $apiKey -eq "paste-your-openai-api-key-here") {
    Write-Host "Open .openai-master-key.json and replace the placeholder before propagating." -ForegroundColor Yellow
    exit 1
}

$apps = Get-ChildItem $githubRoot -Directory | Where-Object {
    $_.FullName -ne $repoRoot -and (
        (Test-Path (Join-Path $_.FullName "requirements.txt")) -or
        (Test-Path (Join-Path $_.FullName "package.json")) -or
        (Get-ChildItem $_.FullName -Filter "*.py" -File -ErrorAction SilentlyContinue | Select-Object -First 1)
    )
}

Write-Host ("Applications to update: " + (($apps | Select-Object -ExpandProperty Name) -join ", ")) -ForegroundColor Yellow

foreach ($app in $apps) {
    Write-Host "Processing $($app.Name)" -ForegroundColor Cyan

    $wrapperPath = Join-Path $app.FullName "openai_key_manager.py"
    $envGeneratorPath = Join-Path $app.FullName "generate_openai_env.py"

    if ((Test-Path $wrapperPath) -and -not $Force) {
        Write-Host "  Skipping existing $wrapperPath (use -Force to overwrite)" -ForegroundColor DarkYellow
    }
    else {
        @"
from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(r"$repoRoot")
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from openai_key_manager import (
    OpenAIMasterKeyManager,
    get_openai_api_key,
    get_openai_manager,
    setup_openai_env,
)

__all__ = [
    "OpenAIMasterKeyManager",
    "get_openai_api_key",
    "get_openai_manager",
    "setup_openai_env",
]
"@ | Out-File -FilePath $wrapperPath -Encoding utf8
        Write-Host "  Created $wrapperPath" -ForegroundColor Green
    }

    if ((Test-Path $envGeneratorPath) -and -not $Force) {
        Write-Host "  Skipping existing $envGeneratorPath (use -Force to overwrite)" -ForegroundColor DarkYellow
    }
    else {
        @"
from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(r"$repoRoot")
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from openai_key_manager import get_openai_api_key


def generate_env() -> int:
    api_key = get_openai_api_key()
    if not api_key:
        print("No OpenAI API key available.")
        return 1

    Path(".env").write_text(f'OPENAI_API_KEY="{api_key}"\n', encoding="utf-8")
    print("Generated .env with OPENAI_API_KEY")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate_env())
"@ | Out-File -FilePath $envGeneratorPath -Encoding utf8
        Write-Host "  Created $envGeneratorPath" -ForegroundColor Green
    }
}

Write-Host "Propagation complete." -ForegroundColor Green