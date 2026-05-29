param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [string]$StartDate = "",
    [string]$Workspace = "",
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$Python = "C:\Users\frank\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        throw "python not found. Please install Python or set `$Python in run_data_role_pdca_daily.ps1."
    }
    $Python = $pythonCmd.Source
}
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
if (-not [string]::IsNullOrWhiteSpace($StartDate)) {
    $argsList += @("--start-date", $StartDate)
}

if ($dataSources.sales_json -and (Test-Path -LiteralPath $dataSources.sales_json)) {
    $argsList += @("--sales-json", $dataSources.sales_json)
} else {
    $fallbackSuffix = $Date
    if (-not [string]::IsNullOrWhiteSpace($StartDate) -and $StartDate -ne $Date) {
        $fallbackSuffix = "${StartDate}_to_${Date}"
    }
    $cachedRaw = Join-Path (Split-Path -Parent (Split-Path -Parent $Workspace)) "data_raw\dealer_sales_month_to_date_$fallbackSuffix.json"
    if ((Test-Path -LiteralPath $cachedRaw) -and ((Get-Date) - (Get-Item -LiteralPath $cachedRaw).LastWriteTime).TotalSeconds -lt 600) {
        $argsList += @("--sales-json", $cachedRaw)
    }
    $Puller = Join-Path $Workspace "scripts\pull_vps_sales_data.ps1"
    if (-not ($argsList -contains "--sales-json") -and (Test-Path -LiteralPath $Puller)) {
        $pullArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Puller, "-Date", $Date, "-Workspace", $Workspace)
        if (-not [string]::IsNullOrWhiteSpace($StartDate)) {
            $pullArgs += @("-StartDate", $StartDate)
        }
        $pulled = & powershell.exe @pullArgs
        $pulledPath = ($pulled | Select-Object -Last 1).Trim()
        if (-not ($pulledPath -and (Test-Path -LiteralPath $pulledPath))) {
            $pulledPath = $cachedRaw
        }
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
