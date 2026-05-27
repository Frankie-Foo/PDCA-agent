param(
    [string]$TeamPath = "D:\经销商PDCA\teams\yang-jingjing",
    [string]$Date = (Get-Date -Format "yyyy-MM-dd")
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "daily-team-check.py"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    throw "Python was not found. Install Python or run daily-team-check.py with an available Python runtime."
}

& $python.Source $PythonScript --team-path $TeamPath --date $Date
