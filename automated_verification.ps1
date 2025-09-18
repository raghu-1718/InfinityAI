# InfinityAI.Pro Automated Verification Script
# This script will:
# 1. Install Python dependencies
# 2. Install Node dependencies (if package.json exists)
# 3. Run backend services (Docker Compose if available, else Python)
# 4. Run all Python and Node tests
# 5. Summarize results

param(
    [string]$BaseUrl = $env:BASE_URL
)

$ErrorActionPreference = 'Stop'

# Ensure we run from the project directory regardless of how the script is invoked
Push-Location $PSScriptRoot
try {
    Write-Host "[1/7] Installing Python dependencies..."
    if (Test-Path "requirements.txt") {
        python -m pip install -r requirements.txt
    }
    if (Test-Path "api/requirements.txt") {
        python -m pip install -r api/requirements.txt
    }
    if (Test-Path "pyproject.toml") {
        if (Get-Command poetry -ErrorAction SilentlyContinue) {
            poetry install
        } else {
            Write-Host "Poetry not found, skipping poetry install."
        }
    }
    if (Test-Path "engine/pyproject.toml") {
        if (Get-Command poetry -ErrorAction SilentlyContinue) {
            Push-Location "engine"
            poetry install
            Pop-Location
        } else {
            Write-Host "Poetry not found for engine/, skipping poetry install."
        }
    }

    Write-Host "[2/7] Installing Node dependencies (if any)..."
    if (Test-Path "package.json") {
        if (Test-Path "yarn.lock") {
            yarn install
        } else {
            npm install
        }
    }

    Write-Host "[3/7] Starting backend services (Docker if available, else uvicorn)..."
    $dockerStarted = $false
    $uvicornProc = $null
    $hasDockerComposeYml = Test-Path "docker-compose.yml"
    $hasComposeYaml = Test-Path "compose.yaml"
    if ($hasDockerComposeYml -or $hasComposeYaml) {
        try {
            if ($hasDockerComposeYml) {
                docker-compose -f docker-compose.yml up -d
            } else {
                docker compose -f compose.yaml up -d
            }
            $dockerStarted = $true
            Write-Host "Docker services started (waiting for health)..."
            Start-Sleep -Seconds 10
        } catch {
            Write-Warning "Docker compose failed: $($_.Exception.Message). Falling back to uvicorn."
        }
    }
    if (-not $dockerStarted) {
        # Fallback: start FastAPI locally via uvicorn
        $moduleToRun = "engine.app.main:app"
        if (-not (Test-Path "engine/app/main.py")) { $moduleToRun = "api.app.main:app" }
        $args = @("-m", "uvicorn", $moduleToRun, "--host", "0.0.0.0", "--port", "8000")
        $uvicornProc = Start-Process -FilePath "python" -ArgumentList $args -PassThru
        Write-Host "Started uvicorn (PID=$($uvicornProc.Id))"
        Start-Sleep -Seconds 5
    }

    if (-not $BaseUrl -or [string]::IsNullOrWhiteSpace($BaseUrl)) { $BaseUrl = "http://localhost:8000" }
    Write-Host "[4/7] Health check: $BaseUrl/health"
    $healthy = $false
    for ($i = 0; $i -lt 15; $i++) {
        try {
            $resp = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 3
            if ($resp.StatusCode -eq 200) {
                Write-Host "Health OK: $($resp.StatusCode) - $($resp.Content)" -ForegroundColor Green
                $healthy = $true
                break
            }
        } catch {
            Start-Sleep -Milliseconds 700
        }
    }
    if (-not $healthy) {
        Write-Warning "Health check failed or endpoint not available."
    }

    Write-Host "[5/7] Running Python tests..."
    $hasPytestIni = Test-Path "pytest.ini"
    $hasTestsFolder = Test-Path "tests"
    $hasRootTests = (Get-ChildItem -Filter "test_*.py" -Path . -File -ErrorAction SilentlyContinue).Count -gt 0
    if ($hasPytestIni -or $hasTestsFolder -or $hasRootTests) {
        # Cover both configured tests/ and root test_*.py files
        python -m pytest -v --maxfail=1 --disable-warnings tests .
    } else {
        Write-Host "No pytest tests found."
    }

    Write-Host "[6/7] Running Node tests (if any)..."
    if (Test-Path "package.json") {
        try {
            $pkg = Get-Content package.json -Raw | ConvertFrom-Json
            if ($pkg.scripts -and $pkg.scripts.test) {
                npm test --silent
            } else {
                Write-Host "No npm test script found."
            }
        } catch {
            Write-Host "Unable to parse package.json; skipping npm tests."
        }
    }

} finally {
    Write-Host "[7/7] Cleanup (if any)..."
    if ($uvicornProc -ne $null) {
        try { Stop-Process -Id $uvicornProc.Id -Force } catch {}
        Write-Host "Stopped uvicorn (PID=$($uvicornProc.Id))"
    }
    if ($dockerStarted) {
        try {
            if (Test-Path "docker-compose.yml") { docker-compose -f docker-compose.yml down }
            elseif (Test-Path "compose.yaml") { docker compose -f compose.yaml down }
        } catch {}
        Write-Host "Docker services stopped."
    }
    Pop-Location
}

Write-Host "`nAutomation complete. Please review the output above for any errors or failures."
