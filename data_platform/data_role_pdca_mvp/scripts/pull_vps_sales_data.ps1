param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [string]$Workspace = "",
    [string]$VertuCmd = "C:\Users\frank\AppData\Roaming\npm\vertu.cmd"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Workspace)) {
    $Workspace = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}

$QueryFile = Join-Path $Workspace "system_queries\pull_dealer_sales_month_to_date.py"
$OutDir = Join-Path (Split-Path -Parent (Split-Path -Parent $Workspace)) "data_raw"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$OutFile = Join-Path $OutDir "dealer_sales_month_to_date_$Date.json"
$ParamsFile = Join-Path $OutDir "dealer_sales_month_to_date_$Date.params.json"

$paramsJson = @{ run_date = $Date } | ConvertTo-Json -Compress
$paramsJson | Set-Content -LiteralPath $ParamsFile -Encoding UTF8

if (-not (Test-Path -LiteralPath $VertuCmd)) {
    $cmd = Get-Command vertu -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "vertu CLI not found. Install/login vps-cli first."
    }
    $VertuCmd = $cmd.Source
}

$result = & $VertuCmd odoo data sandbox --code-file $QueryFile --params-file $ParamsFile
$resultText = ($result -join "`n")
$resultText | Set-Content -LiteralPath $OutFile -Encoding UTF8
Write-Host $OutFile
