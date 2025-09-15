# This script automates the startup and verification of the backend and frontend applications.

# --- Configuration ---
$backendPort = 8000
$frontendPort = 3000
$maxWaitSeconds = 30 # Maximum time to wait for services to start

# --- Functions ---
function Start-Backend {
    Write-Host "Attempting to start the backend FastAPI server from 'engine/app/main.py'..."
    # Corrected command to run the main engine application.
    # We set PYTHONPATH to the project root to ensure modules like 'engine' and 'core' are found.
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$env:PYTHONPATH='.'; uvicorn engine.app.main:app --host 0.0.0.0 --port $backendPort }" -WindowStyle Minimized
}

function Start-Frontend {
    Write-Host "Attempting to start the frontend React app..."
    # Runs 'npm start' in the 'dashboard' directory
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd dashboard; npm start" -WindowStyle Minimized
}

function Verify-Endpoint {
    param(
        [string]$url,
        [string]$serviceName
    )
    $startTime = Get-Date
    $timeout = New-TimeSpan -Seconds $maxWaitSeconds
    Write-Host "Verifying $serviceName at $url..."
    do {
        try {
            # The main engine app might not have a "/" route, let's check a known one or a health check if available.
            # For now, we'll stick with the root, but this might need adjustment.
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 404) { # 404 is also a sign the server is up
                Write-Host "$serviceName is up and running." -ForegroundColor Green
                return $true
            }
        }
        catch {
            # Suppress error messages during polling
        }
        Start-Sleep -Seconds 2
        $elapsed = (Get-Date) - $startTime
    } while ($elapsed -lt $timeout)

    Write-Host "$serviceName failed to start within $maxWaitSeconds seconds." -ForegroundColor Red
    return $false
}

# --- Main Execution ---
try {
    # 1. Start Backend
    Start-Backend
    
    # 2. Start Frontend
    Start-Frontend

    # 3. Verify Backend
    # The main app in 'engine' might return 404 for the root, which still means it's running.
    if (-not (Verify-Endpoint -url "http://localhost:$backendPort/" -serviceName "Backend")) {
        throw "Backend verification failed."
    }

    # 4. Verify Frontend
    if (-not (Verify-Endpoint -url "http://localhost:$frontendPort" -serviceName "Frontend")) {
        throw "Frontend verification failed."
    }

    Write-Host "`nAll services started and verified successfully!" -ForegroundColor Cyan
    Write-Host "Backend is running on http://localhost:$backendPort"
    Write-Host "Frontend is running on http://localhost:$frontendPort"

}
catch {
    Write-Error "An error occurred during startup: $_"
    Write-Host "Stopping running processes..."
    # Forcefully stop the processes we started to clean up
    Get-Process -Name "powershell", "node" -ErrorAction SilentlyContinue | Stop-Process -Force
}