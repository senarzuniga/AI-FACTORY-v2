# Safe restart helper for local dev services.
Write-Host "Restart helper started..." -ForegroundColor Cyan

Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Python/Node processes stopped." -ForegroundColor Green

$dataDir = "C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2\data"
if (Test-Path $dataDir) {
  Write-Host "Data files:" -ForegroundColor Magenta
  Get-ChildItem $dataDir -Filter "*.json" | ForEach-Object {
    $sizeKb = [math]::Round($_.Length / 1KB, 1)
    Write-Host " - $($_.Name) ($sizeKb KB)" -ForegroundColor Yellow
  }
}

Write-Host "Restart helper completed." -ForegroundColor Green
