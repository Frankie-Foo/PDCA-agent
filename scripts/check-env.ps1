Write-Host "Checking local sales agent environment..."

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
  Write-Host "[OK] git:" $git.Source
} else {
  Write-Host "[MISS] git not found"
}

$hermes = Get-Command hermes -ErrorAction SilentlyContinue
if ($hermes) {
  Write-Host "[OK] hermes:" $hermes.Source
  hermes --version
} else {
  Write-Host "[MISS] hermes not found in PATH"
}

$hermesHome = Join-Path $env:USERPROFILE ".hermes"
if (Test-Path $hermesHome) {
  Write-Host "[OK] Hermes home exists:" $hermesHome
} else {
  Write-Host "[MISS] Hermes home not found:" $hermesHome
}

Write-Host "Done."

