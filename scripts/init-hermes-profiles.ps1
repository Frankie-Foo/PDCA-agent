$ErrorActionPreference = "Stop"

$hermes = Get-Command hermes -ErrorAction SilentlyContinue
if (-not $hermes) {
  Write-Host "Hermes command not found. Install Hermes first, then rerun this script."
  exit 1
}

$profileNames = @("market-analyst", "contract-expert", "sales-manager")
$templateRoot = Join-Path $PSScriptRoot "..\profiles"
$hermesProfilesRoot = Join-Path $env:USERPROFILE ".hermes\profiles"

foreach ($name in $profileNames) {
  Write-Host "Ensuring Hermes profile:" $name
  hermes profile create $name

  $sourceSoul = Join-Path $templateRoot "$name\SOUL.md"
  $targetDir = Join-Path $hermesProfilesRoot $name
  $targetSoul = Join-Path $targetDir "SOUL.md"

  if (Test-Path $sourceSoul) {
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    Copy-Item -Force $sourceSoul $targetSoul
    Write-Host "Copied SOUL.md to" $targetSoul
  }
}

Write-Host "Profiles initialized. Review each profile config before enabling API access."

