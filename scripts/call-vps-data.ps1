param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("whoami", "caps", "search", "read-group")]
  [string]$Mode,

  [string]$ModelName = "",
  [string]$Domain = "[]",
  [string]$Fields = "[]",
  [string]$GroupBy = "[]",
  [string]$Aggregates = "[]",
  [int]$Limit = 20,
  [string]$Order = "",
  [string]$Topic = "vps-data"
)

$ErrorActionPreference = "Stop"

$workspace = Resolve-Path (Join-Path $PSScriptRoot "..")
$workspace = $workspace.Path
$rawDir = Join-Path $workspace "data_raw"
New-Item -ItemType Directory -Force -Path $rawDir | Out-Null

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$safeTopic = ($Topic -replace '[^\p{L}\p{Nd}\-_]+', '-').Trim('-')
if ([string]::IsNullOrWhiteSpace($safeTopic)) {
  $safeTopic = "vps-data"
}

$outFile = Join-Path $rawDir "$stamp`_$safeTopic.json"

function Invoke-Vertu {
  param([string[]]$ArgsForVertu)
  & vertu @ArgsForVertu
}

switch ($Mode) {
  "whoami" {
    $result = Invoke-Vertu @("whoami")
  }

  "caps" {
    $result = Invoke-Vertu @("caps", "list", "--json")
  }

  "search" {
    if ([string]::IsNullOrWhiteSpace($ModelName)) {
      throw "ModelName is required for search."
    }

    $args = @(
      "odoo", "data", "search",
      "--model-name", $ModelName,
      "--domain", $Domain,
      "--fields", $Fields,
      "--limit", "$Limit"
    )
    if (-not [string]::IsNullOrWhiteSpace($Order)) {
      $args += @("--order", $Order)
    }
    $result = Invoke-Vertu $args
  }

  "read-group" {
    if ([string]::IsNullOrWhiteSpace($ModelName)) {
      throw "ModelName is required for read-group."
    }

    $args = @(
      "odoo", "data", "read-group",
      "--model-name", $ModelName,
      "--domain", $Domain,
      "--fields", $Aggregates,
      "--groupby", $GroupBy,
      "--limit", "$Limit"
    )
    $result = Invoke-Vertu $args
  }
}

$payload = [ordered]@{
  generated_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
  mode = $Mode
  model_name = $ModelName
  domain = $Domain
  fields = $Fields
  group_by = $GroupBy
  aggregates = $Aggregates
  limit = $Limit
  order = $Order
  result_text = ($result -join "`n")
}

$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outFile -Encoding UTF8
Write-Host $outFile
