
# PowerShell script to automate backend/frontend startup and endpoint verification
# Save as automate_startup_and_verification.ps1 in workspace root

function Stop-ExistingProcesses {
    Write-Host "Stopping any running backend/frontend processes..."
    get-process -Name "uvicorn", "node", "npm" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}


function Start-Backend {
    $backendPath = "c:\Users\Raghu\Dropbox\InfinityAI.Pro\engine"
    if (Test-Path "$backendPath\pyproject.toml") {
        Write-Host "Starting backend (FastAPI via Poetry) in $backendPath..."
        Push-Location $backendPath
        Start-Process -NoNewWindow -FilePath "poetry" -ArgumentList "run uvicorn app.main:app --reload" -PassThru | Out-Null
        Pop-Location
        Start-Sleep -Seconds 10
    } else {
        Write-Host "ERROR: pyproject.toml not found in $backendPath. Backend not started."
    }
}

function Start-Frontend {
    $frontendPath = "c:\Users\Raghu\Dropbox\InfinityAI.Pro\dashboard"
    if (Test-Path "$frontendPath\package.json") {
        Write-Host "Starting frontend (React) in $frontendPath..."
        Push-Location $frontendPath
        Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "start" -PassThru | Out-Null
        Pop-Location
        Start-Sleep -Seconds 20
    } else {
        Write-Host "ERROR: package.json not found in $frontendPath. Frontend not started."
    }
}

function Test-EndpointVerification {
    $verificationScript = "c:\Users\Raghu\Dropbox\InfinityAI.Pro\check_fastapi_endpoints.ps1"
    Write-Host "Running endpoint verification script: $verificationScript"
    if (Test-Path $verificationScript) {
        try {
            & $verificationScript
        } catch {
            Write-Host "ERROR: Failed to run endpoint verification script. $_"
        }
    } else {
        Write-Host "ERROR: Endpoint verification script not found: $verificationScript"
    }
}

Write-Host "\n=== InfinityAI.Pro Automation Script ==="
Write-Host "This script will:"
Write-Host "1. Stop any running backend/frontend processes."
Write-Host "2. Start backend (FastAPI) and frontend (React) in correct folders."
Write-Host "3. Run endpoint verification script."
Write-Host "4. Display results and errors."
Write-Host "\nPlease ensure Poetry and npm are installed and available in PATH."

Stop-ExistingProcesses
Start-Backend
Start-Frontend
Test-EndpointVerification

Write-Host "\nAutomation complete. Check above for any errors or endpoint results."
