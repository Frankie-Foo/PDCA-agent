$ErrorActionPreference = "Stop"

$envPath = Join-Path $env:USERPROFILE ".hermes\.env"
New-Item -ItemType File -Force -Path $envPath | Out-Null

$key = Read-Host "Paste DASHSCOPE_API_KEY then press Enter"
if ([string]::IsNullOrWhiteSpace($key)) {
  Write-Host "No key entered. Nothing changed."
  exit 1
}

$lines = @(Get-Content -LiteralPath $envPath -ErrorAction SilentlyContinue)
$lines = $lines | Where-Object {
  ($_ -notlike "DASHSCOPE_API_KEY=*") -and
  ($_ -notlike "DASHSCOPE_BASE_URL=*")
}

$lines += "DASHSCOPE_API_KEY=$key"
$lines += "DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1"

Set-Content -LiteralPath $envPath -Value $lines -Encoding UTF8
Write-Host "DashScope key saved to $envPath"
Write-Host "You can close this window."
