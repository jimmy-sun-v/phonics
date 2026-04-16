$ErrorActionPreference = "SilentlyContinue"
Write-Host "=== Tool Check ===" -ForegroundColor Cyan

# Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $python = python --version 2>&1
    Write-Host "[OK] $python" -ForegroundColor Green
    if ($python -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "[WARN] Python 3.11+ required, found $python" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[MISSING] Python 3.11+ required" -ForegroundColor Red
}

# pip
if (Get-Command pip -ErrorAction SilentlyContinue) {
    $pip = pip --version 2>&1
    Write-Host "[OK] $pip" -ForegroundColor Green
} else {
    Write-Host "[MISSING] pip required" -ForegroundColor Red
}

# PostgreSQL
if (Get-Command psql -ErrorAction SilentlyContinue) {
    $psql = psql --version 2>&1
    Write-Host "[OK] $psql" -ForegroundColor Green
} else {
    Write-Host "[INFO] PostgreSQL not found - SQLite will be used for development" -ForegroundColor Yellow
}

# Git
if (Get-Command git -ErrorAction SilentlyContinue) {
    $git = git --version 2>&1
    Write-Host "[OK] $git" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Git required" -ForegroundColor Red
}

# ffmpeg (required by pydub for audio transcoding)
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    $ffmpeg = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] $ffmpeg" -ForegroundColor Green
} else {
    Write-Host "[MISSING] ffmpeg required (used by pydub for audio format conversion)" -ForegroundColor Red
}

# venv module
$venvCheck = python -m venv --help 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] venv module available" -ForegroundColor Green
} else {
    Write-Host "[MISSING] venv module required" -ForegroundColor Red
}

Write-Host "=== Done ===" -ForegroundColor Cyan
