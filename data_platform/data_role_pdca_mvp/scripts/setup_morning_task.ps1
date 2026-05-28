param(
    [string]$TaskName = "DealerDataRolePDCAMorning",
    [string]$Time = "09:00",
    [string]$Workspace = ""
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($Workspace)) {
    $Workspace = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$Runner = Join-Path $Workspace "scripts\run_data_role_pdca_daily.ps1"
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Runner`""
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Run data role PDCA MVP every morning." -Force
Write-Host "Registered scheduled task $TaskName at $Time"
