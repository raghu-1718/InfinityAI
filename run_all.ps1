# PowerShell script to automate backend and frontend runs for InfinityAI.Pro
# Save as run_all.ps1 in project root

$ErrorActionPreference = 'Stop'
Write-Host "`n=== InfinityAI.Pro Start ==="

function Resolve-NpmCmd {
    $cmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue)?.Source
    if (-not $cmd) { throw "npm.cmd not found in PATH. Install Node.js LTS from https://nodejs.org and restart PowerShell." }
    return $cmd
}

function Test-Url {
    param([string]$Url, [int]$Retries = 20, [int]$DelaySeconds = 1)
    for ($i=0; $i -lt $Retries; $i++) {
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { return $true }
        } catch {}
        Start-Sleep -Seconds $DelaySeconds
    }
    return $false
}

# 1) Start backend (FastAPI)
$backendDir = Join-Path $PSScriptRoot 'api'
if (-not (Test-Path (Join-Path $backendDir 'main.py'))) {
    throw "Backend entry api\main.py not found. Are you in the repo root?"
}
Write-Host "Starting backend (FastAPI) in $backendDir ..."
$python = (Get-Command python -ErrorAction SilentlyContinue)?.Source
if (-not $python) { throw "python not found in PATH/venv." }

# Kill any process on 8000 to avoid bind errors (optional)
try { Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } } catch {}

Start-Process -FilePath $python `
    -ArgumentList @('-m','uvicorn','api.main:app','--reload','--host','127.0.0.1','--port','8000') `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Minimized

if (Test-Url -Url 'http://127.0.0.1:8000/docs') {
    Write-Host "Backend OK at http://127.0.0.1:8000/docs"
} else {
    Write-Warning "Backend did not respond in time. Check terminal where it started."
}

# 2) Start frontend (React)
# Prefer dashboard/package.json; fallback to repo root package.json
$dashboardPkg = Join-Path $PSScriptRoot 'dashboard\package.json'
$rootPkg = Join-Path $PSScriptRoot 'package.json'
$frontendDir = $null
if (Test-Path $dashboardPkg) { $frontendDir = Split-Path $dashboardPkg -Parent }
elseif (Test-Path $rootPkg) { $frontendDir = $PSScriptRoot }

if ($frontendDir) {
    Write-Host "Starting frontend (React) in $frontendDir ..."
    $npm = Resolve-NpmCmd

    # Install dependencies if node_modules missing
    $nodeModules = Join-Path $frontendDir 'node_modules'
    $installArgs = 'ci'
    if (-not (Test-Path $nodeModules)) {
        Write-Host "Installing frontend dependencies (npm $installArgs) ..."
        Start-Process -FilePath $npm -ArgumentList $installArgs -WorkingDirectory $frontendDir -Wait
    } else {
        Write-Host "Dependencies already present. Skipping npm ci."
    }

    # Free port 3000 if needed
    try { Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } } catch {}

    # Launch dev server (non-blocking)
    Start-Process -FilePath $npm -ArgumentList 'start' -WorkingDirectory $frontendDir
} else {
    Write-Warning "No package.json found in dashboard/ or repo root. Skipping frontend start."
}

# 3) Optional endpoint verification
$verifyScript = Join-Path $PSScriptRoot 'check_fastapi_endpoints.ps1'
if (Test-Path $verifyScript) {
    Write-Host "Running endpoint verification: $verifyScript"
    & $verifyScript
} else {
    Write-Host "Endpoint verification script not found at $verifyScript (skipping)."
}

# 4) Open URLs
try { Start-Process 'http://127.0.0.1:8000/docs' } catch {}
try { Start-Process 'http://localhost:3000' } catch {}

Write-Host "`nStart complete. Backend on 8000; Frontend on 3000 (if present)."
