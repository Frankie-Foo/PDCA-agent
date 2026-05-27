param(
  [string]$Profile = "default"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Resolve-Path (Join-Path $PSScriptRoot ".."))

$hermesExe = Join-Path $env:LOCALAPPDATA "hermes\hermes-agent\venv\Scripts\hermes.exe"
if (-not (Test-Path $hermesExe)) {
  throw "Hermes executable not found at $hermesExe"
}

Write-Host "Starting Hermes in" (Get-Location)
Write-Host "Project AGENTS.md will be loaded from this directory."
Write-Host "Available performance profiles: performance-data-puller, performance-cleaner, performance-aggregator, performance-report-builder"

if ($Profile -eq "default") {
  & $hermesExe chat
} else {
  & $hermesExe profile use $Profile
  & $hermesExe chat
}
