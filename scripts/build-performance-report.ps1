param(
  [Parameter(Mandatory = $true)]
  [string]$InputPath,

  [int]$Year = 0,
  [string]$Channel = "",
  [string]$Department = "",
  [string]$Sheet = "",
  [string]$CustomerField = "",
  [string]$Metric = "实际业绩",
  [string]$Topic = "dealer-performance",
  [switch]$ExcludeRefunds,
  [switch]$AllSheets,
  [switch]$IncludeDetail
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$scriptPath = Join-Path $PSScriptRoot "process-sales-detail.py"
$outputDir = Join-Path $repoRoot "data_reports"
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (Test-Path $bundledPython) {
  $pythonExe = $bundledPython
} else {
  $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
  if (-not $pythonCmd) {
    throw "Python was not found. Install Python or run from Codex workspace runtime."
  }
  $pythonExe = $pythonCmd.Source
}

$argsList = @(
  $scriptPath,
  "--input", (Resolve-Path -LiteralPath $InputPath).Path,
  "--output-dir", $outputDir,
  "--topic", $Topic,
  "--metric", $Metric
)

if ($Year -gt 0) { $argsList += @("--year", $Year) }
if ($Channel) { $argsList += @("--channel", $Channel) }
if ($Department) { $argsList += @("--department", $Department) }
if ($Sheet) { $argsList += @("--sheet", $Sheet) }
if ($CustomerField) { $argsList += @("--customer-field", $CustomerField) }
if ($ExcludeRefunds) { $argsList += "--exclude-refunds" }
if ($AllSheets) { $argsList += "--all-sheets" }
if ($IncludeDetail) { $argsList += "--include-detail" }

& $pythonExe @argsList
