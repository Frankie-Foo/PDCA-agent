param(
  [Parameter(Mandatory = $true)]
  [string]$Query,

  [string]$Topic = "data-query"
)

$ErrorActionPreference = "Stop"

$workspace = Resolve-Path (Join-Path $PSScriptRoot "..")
$workspace = $workspace.Path
$hermesExe = "C:\Users\frank\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"

if (-not (Test-Path $hermesExe)) {
  $cmd = Get-Command hermes -ErrorAction SilentlyContinue
  if (-not $cmd) {
    throw "Hermes executable not found."
  }
  $hermesExe = $cmd.Source
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$safeTopic = ($Topic -replace '[^\p{L}\p{Nd}\-_]+', '-').Trim('-')
if ([string]::IsNullOrWhiteSpace($safeTopic)) {
  $safeTopic = "data-query"
}

$rawDir = Join-Path $workspace "data_raw"
$reportDir = Join-Path $workspace "data_reports"
$qualityDir = Join-Path $workspace "data_quality"
New-Item -ItemType Directory -Force -Path $rawDir, $reportDir, $qualityDir | Out-Null

$outFile = Join-Path $reportDir "$stamp`_$safeTopic`_summary.md"

$prompt = @"
You are acting as the data-access-agent for the Dealer PDCA workspace.

User data request:
$Query

Follow the data-access-agent rules in AGENTS.md.
Use installed Hermes Odoo skills when needed, especially:
- odoo-current-user-identity
- odoo-data-query-assistant
- odoo-daily-sales-report
- odoo-daily-report-assistant
- odoo-okr-management-assistant
- odoo-sale-personnel-efficiency
- odoo-knowledge-discovery

Rules:
1. Read-only only. Do not approve, reject, send messages, write, delete, or import data.
2. If VPS/Odoo data is needed, use the Vertu/Odoo skill or the vertu CLI.
3. Return these sections: user question, query scope, skill or command used, data source, result summary, data quality issues, next step.
4. If you cannot query, explain why and what information is needed next.
"@

Push-Location $workspace
try {
  $result = & $hermesExe -z $prompt
} finally {
  Pop-Location
}

$content = @"
# Data Access Agent Result

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Query

$Query

## Result

$result
"@

Set-Content -LiteralPath $outFile -Value $content -Encoding UTF8
Write-Host $outFile
