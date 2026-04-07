# Design: Task 0.1 – Verify & Install Required Development Tools

## Overview

Before any project work begins, verify that all required development tools are installed and at the correct versions. Install any missing tools.

## Dependencies

None (this is the very first task)

## Required Tools

### 1. Python (≥ 3.11)

- **Check**: `python --version`
- **Install (if missing)**:
  - Windows: Download from https://www.python.org/downloads/ or `winget install Python.Python.3.11`
  - Ensure `python` and `pip` are on `PATH`
- **Post-install verification**: `python --version` → `Python 3.11.x` or higher

### 2. pip (bundled with Python)

- **Check**: `pip --version`
- **Expected**: pip 23.x+ with Python 3.11+

### 3. PostgreSQL (≥ 14)

- **Check**: `psql --version`
- **Install (if missing)**:
  - Windows: Download from https://www.postgresql.org/download/windows/ or `winget install PostgreSQL.PostgreSQL`
  - During install, note: port (default 5432), superuser password
- **Post-install**:
  - Verify service is running: `pg_isready`
  - Create dev database:
    ```sql
    CREATE DATABASE phonicsapp_dev;
    CREATE USER phonicsapp WITH PASSWORD '<dev-password>';
    GRANT ALL PRIVILEGES ON DATABASE phonicsapp_dev TO phonicsapp;
    ```

### 4. Git

- **Check**: `git --version`
- **Expected**: Git 2.x+
- **Install (if missing)**: `winget install Git.Git`

### 5. Node.js (optional, for frontend tooling if needed later)

- **Check**: `node --version`
- **Expected**: Node 18+ (only needed if a JS build step is added)

### 6. Virtual Environment Tool (venv)

- **Check**: `python -m venv --help`
- **Expected**: Built into Python 3.11+
- **Setup**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

## Implementation Steps

1. **Create a PowerShell verification script** at `scripts/check_tools.ps1`:
   ```powershell
   Write-Host "=== Tool Check ===" -ForegroundColor Cyan

   # Python
   $python = python --version 2>&1
   if ($LASTEXITCODE -eq 0) {
       Write-Host "[OK] $python" -ForegroundColor Green
   } else {
       Write-Host "[MISSING] Python 3.11+ required" -ForegroundColor Red
   }

   # pip
   $pip = pip --version 2>&1
   if ($LASTEXITCODE -eq 0) {
       Write-Host "[OK] $pip" -ForegroundColor Green
   } else {
       Write-Host "[MISSING] pip required" -ForegroundColor Red
   }

   # PostgreSQL
   $psql = psql --version 2>&1
   if ($LASTEXITCODE -eq 0) {
       Write-Host "[OK] $psql" -ForegroundColor Green
   } else {
       Write-Host "[MISSING] PostgreSQL 14+ required" -ForegroundColor Red
   }

   # Git
   $git = git --version 2>&1
   if ($LASTEXITCODE -eq 0) {
       Write-Host "[OK] $git" -ForegroundColor Green
   } else {
       Write-Host "[MISSING] Git required" -ForegroundColor Red
   }

   Write-Host "=== Done ===" -ForegroundColor Cyan
   ```

2. **Create the virtual environment** and activate it.

3. **Initialize `requirements.txt`** with core dependencies (to be expanded in Task 1.10):
   ```
   Django>=5.1,<5.2
   django-environ>=0.11
   psycopg2-binary>=2.9
   djangorestframework>=3.15
   ```

4. **Install base dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Acceptance Criteria

- [ ] Python ≥ 3.11 is available on PATH
- [ ] pip is available
- [ ] PostgreSQL ≥ 14 is installed and running, dev database created
- [ ] Git is available
- [ ] Virtual environment `.venv` created and activated
- [ ] `pip install -r requirements.txt` succeeds

## Test Strategy

- Run `scripts/check_tools.ps1` → all items show `[OK]`
- `python -c "import django; print(django.get_version())"` → prints Django version

## Target Folder(s)

```
PhonicsApp/
├── scripts/
│   └── check_tools.ps1
├── .venv/                (gitignored)
└── requirements.txt      (initial, expanded in Task 1.10)
```
