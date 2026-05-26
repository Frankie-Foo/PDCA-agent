$ErrorActionPreference = "Stop"

$hermesCommand = Get-Command hermes -ErrorAction SilentlyContinue
if ($hermesCommand) {
  $hermesExe = $hermesCommand.Source
} else {
  $defaultHermesExe = Join-Path $env:LOCALAPPDATA "hermes\hermes-agent\venv\Scripts\hermes.exe"
  if (Test-Path $defaultHermesExe) {
    $hermesExe = $defaultHermesExe
  } else {
    Write-Host "Hermes command not found. Install Hermes first, then rerun this script."
    exit 1
  }
}

$profileNames = @("market-analyst", "contract-expert", "sales-manager")
$templateRoot = Join-Path $PSScriptRoot "..\profiles"
$legacyHermesHome = Join-Path $env:USERPROFILE ".hermes"
$localHermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA "hermes" }
$hermesHome = if (Test-Path (Join-Path $legacyHermesHome "profiles")) { $legacyHermesHome } else { $localHermesHome }
$hermesProfilesRoot = Join-Path $hermesHome "profiles"

foreach ($name in $profileNames) {
  Write-Host "Ensuring Hermes profile:" $name
  & $hermesExe profile create $name

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
