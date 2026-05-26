$ErrorActionPreference = "Stop"

$message = "Auto Sync $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

git status --short
git add .
git commit -m $message
git push

