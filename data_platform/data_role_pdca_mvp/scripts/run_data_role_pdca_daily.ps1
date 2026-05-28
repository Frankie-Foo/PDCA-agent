param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [string]$Workspace = "",
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$Python = "C:\Users\frank\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if ([string]::IsNullOrWhiteSpace($Workspace)) {
    $Workspace = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$Script = Join-Path $Workspace "scripts\data_role_pdca_daily.py"
$DataSourcesPath = Join-Path $Workspace "config\data_sources.json"

$dataSources = Get-Content -LiteralPath $DataSourcesPath -Encoding UTF8 | ConvertFrom-Json

$argsList = @(
    $Script,
    "--date", $Date,
    "--workspace", $Workspace
)

if ($dataSources.sales_json -and (Test-Path -LiteralPath $dataSources.sales_json)) {
    $argsList += @("--sales-json", $dataSources.sales_json)
} else {
    $Puller = Join-Path $Workspace "scripts\pull_vps_sales_data.ps1"
    if (Test-Path -LiteralPath $Puller) {
        $pulled = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Puller -Date $Date -Workspace $Workspace
        $pulledPath = ($pulled | Select-Object -Last 1).Trim()
        if ($pulledPath -and (Test-Path -LiteralPath $pulledPath)) {
            $argsList += @("--sales-json", $pulledPath)
        }
    }
}

if (-not ($argsList -contains "--sales-json") -and $dataSources.allow_excel_demo -and $dataSources.sales_xlsx -and (Test-Path -LiteralPath $dataSources.sales_xlsx)) {
    $argsList += @("--sales-xlsx", $dataSources.sales_xlsx)
    if ($dataSources.sales_sheet) {
        $argsList += @("--sales-sheet", $dataSources.sales_sheet)
    }
}

if ($dataSources.logistics_csv -and (Test-Path -LiteralPath $dataSources.logistics_csv)) {
    $argsList += @("--logistics-csv", $dataSources.logistics_csv)
}

if ($Push) {
    $argsList += "--push"
}

& $Python @argsList
