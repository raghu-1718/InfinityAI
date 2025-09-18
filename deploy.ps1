# InfinityAI.Pro Unified Deployment Script
# This script handles complete deployment of the InfinityAI.Pro application

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("azure", "docker", "podman", "vercel", "local")]
    [string]$Target = "azure",

    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,

    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,

    [Parameter(Mandatory=$false)]
    [string]$Environment = "production"
)

# Configuration
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$ProjectRoot\deployment_$Timestamp.log"

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..." $Cyan

    # Check Python
    if (!(Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Log "Python not found. Please install Python 3.10+" $Red
        exit 1
    }

    # Check Poetry
    if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
        Write-Log "Poetry not found. Please install Poetry" $Red
        exit 1
    }

    # Check Node.js
    if (!(Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Log "Node.js not found. Please install Node.js 18+" $Red
        exit 1
    }

    # Check npm
    if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Log "npm not found. Please install npm" $Red
        exit 1
    }

    # Target-specific checks
    switch ($Target) {
        "azure" {
            if (!(Get-Command az -ErrorAction SilentlyContinue)) {
                Write-Log "Azure CLI not found. Please install Azure CLI" $Red
                exit 1
            }
            if (!(Get-Command azd -ErrorAction SilentlyContinue)) {
                Write-Log "Azure Developer CLI not found. Please install Azure Developer CLI" $Red
                exit 1
            }
        }
        "docker" {
            if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
                Write-Log "Docker not found. Please install Docker" $Red
                exit 1
            }
        }
        "podman" {
            if (!(Get-Command podman -ErrorAction SilentlyContinue)) {
                Write-Log "Podman not found. Please install Podman" $Red
                exit 1
            }
        }
        "vercel" {
            if (!(Get-Command vercel -ErrorAction SilentlyContinue)) {
                Write-Log "Vercel CLI not found. Please install Vercel CLI" $Red
                exit 1
            }
        }
    }

    Write-Log "Prerequisites check completed successfully" $Green
}

function Install-Dependencies {
    Write-Log "Installing dependencies..." $Cyan

    # Backend dependencies
    Write-Log "Installing Python dependencies with Poetry..."
    Push-Location $ProjectRoot
    try {
        poetry install --no-root
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to install Python dependencies" $Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    # Frontend dependencies
    Write-Log "Installing Node.js dependencies..."
    Push-Location "$ProjectRoot\dashboard"
    try {
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to install Node.js dependencies" $Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    Write-Log "Dependencies installed successfully" $Green
}

function Test-Tests {
    if ($SkipTests) {
        Write-Log "Skipping tests as requested" $Yellow
        return
    }

    Write-Log "Running tests..." $Cyan

    # Backend tests
    Write-Log "Running backend tests..."
    Push-Location $ProjectRoot
    try {
        poetry run pytest --tb=short
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Backend tests failed" $Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    # Frontend tests
    Write-Log "Running frontend tests..."
    Push-Location "$ProjectRoot\dashboard"
    try {
        npm test -- --watchAll=false --passWithNoTests
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Frontend tests failed" $Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    Write-Log "All tests passed" $Green
}

function Build-Application {
    if ($SkipBuild) {
        Write-Log "Skipping build as requested" $Yellow
        return
    }

    Write-Log "Building application..." $Cyan

    # Build frontend
    Write-Log "Building frontend..."
    Push-Location "$ProjectRoot\dashboard"
    try {
        npm run build
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Frontend build failed" $Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    Write-Log "Application built successfully" $Green
}

function Deploy-Azure {
    Write-Log "Deploying to Azure..." $Cyan

    Push-Location $ProjectRoot
    try {
        # Login to Azure (if not already logged in)
        Write-Log "Checking Azure authentication..."
        az account show 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Please login to Azure first:" $Yellow
            Write-Log "az login" $Yellow
            exit 1
        }

        # Use Azure Developer CLI for deployment
        Write-Log "Starting Azure deployment with azd..."
        azd up
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Azure deployment failed" $Red
            exit 1
        }

        Write-Log "Azure deployment completed successfully" $Green
        Write-Log "Your application should be available at: https://www.infinityai.pro" $Green

    } finally {
        Pop-Location
    }
}

function Deploy-Docker {
    Write-Log "Deploying with Docker..." $Cyan

    Push-Location $ProjectRoot
    try {
        Write-Log "Starting Docker deployment..."
        docker-compose up --build -d
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Docker deployment failed" $Red
            exit 1
        }

    Write-Log "Docker deployment completed successfully" $Green
    $backendUrl = if ($env:PUBLIC_URL) { $env:PUBLIC_URL } else { 'http://localhost:8000' }
    Write-Log "Application available at: $backendUrl" $Green

    } finally {
        Pop-Location
    }
}

function Deploy-Podman {
    Write-Log "Deploying with Podman..." $Cyan

    Push-Location $ProjectRoot
    try {
        Write-Log "Starting Podman deployment..."
        podman-compose up --build -d
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Podman deployment failed" $Red
            exit 1
        }

    Write-Log "Podman deployment completed successfully" $Green
    $backendUrl = if ($env:PUBLIC_URL) { $env:PUBLIC_URL } else { 'http://localhost:8000' }
    $frontendUrl = if ($env:FRONTEND_PUBLIC_URL) { $env:FRONTEND_PUBLIC_URL } else { 'http://localhost:3001' }
    Write-Log "Backend: $backendUrl" $Green
    Write-Log "Frontend: $frontendUrl" $Green

    } finally {
        Pop-Location
    }
}

function Deploy-Vercel {
    Write-Log "Deploying to Vercel..." $Cyan

    # Deploy frontend
    Write-Log "Deploying frontend to Vercel..."
    Push-Location "$ProjectRoot\dashboard"
    try {
        vercel --prod
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Vercel frontend deployment failed" $Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    # Deploy backend (if configured)
    Write-Log "Deploying backend to Vercel..."
    Push-Location $ProjectRoot
    try {
        vercel --prod
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Vercel backend deployment failed" $Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    Write-Log "Vercel deployment completed successfully" $Green
}

function Start-Local {
    Write-Log "Starting local development environment..." $Cyan

    # Start backend in background
    Write-Log "Starting backend server..."
    $backendJob = Start-Job -ScriptBlock {
        param($ProjectRoot)
        Push-Location $ProjectRoot
        poetry run uvicorn engine.app.main:app --host 0.0.0.0 --port 8000 --reload
    } -ArgumentList $ProjectRoot

    # Start frontend in background
    Write-Log "Starting frontend server..."
    $frontendJob = Start-Job -ScriptBlock {
        param($ProjectRoot)
        Push-Location "$ProjectRoot\dashboard"
        npm start
    } -ArgumentList $ProjectRoot

    Write-Log "Local development environment started" $Green
    $backendUrl = if ($env:PUBLIC_URL) { $env:PUBLIC_URL } else { 'http://localhost:8000' }
    $frontendUrl = if ($env:FRONTEND_PUBLIC_URL) { $env:FRONTEND_PUBLIC_URL } else { 'http://localhost:3001' }
    Write-Log "Backend: $backendUrl" $Green
    Write-Log "Frontend: $frontendUrl" $Green
    Write-Log "Press Ctrl+C to stop all services" $Yellow

    # Wait for user input to stop
    Read-Host "Press Enter to stop services"

    # Stop jobs
    Stop-Job $backendJob, $frontendJob -PassThru | Remove-Job
    Write-Log "Services stopped" $Green
}

function Show-Help {
    Write-Host @"
InfinityAI.Pro Deployment Script

USAGE:
    .\deploy.ps1 [-Target <target>] [-SkipBuild] [-SkipTests] [-Environment <env>]

PARAMETERS:
    -Target       Deployment target: azure, docker, podman, vercel, local (default: azure)
    -SkipBuild    Skip the build step
    -SkipTests    Skip running tests
    -Environment  Environment: production, staging, development (default: production)

EXAMPLES:
    .\deploy.ps1                                    # Deploy to Azure (default)
    .\deploy.ps1 -Target docker                     # Deploy with Docker
    .\deploy.ps1 -Target local -SkipTests          # Start local dev without tests
    .\deploy.ps1 -Target azure -Environment staging # Deploy to Azure staging

TARGETS:
    azure   - Deploy to Azure using Azure Developer CLI
    docker  - Deploy using Docker Compose
    podman  - Deploy using Podman Compose
    vercel  - Deploy to Vercel
    local   - Start local development environment

"@ -ForegroundColor Cyan
}

# Main execution
Write-Log "Starting InfinityAI.Pro deployment (Target: $Target, Environment: $Environment)" $Green
Write-Log "Log file: $LogFile" $Yellow

try {
    # Show help if requested
    if ($args -contains "-h" -or $args -contains "--help" -or $args -contains "-?") {
        Show-Help
        exit 0
    }

    # Execute deployment steps
    Test-Prerequisites
    Install-Dependencies
    Test-Tests
    Build-Application

    # Deploy based on target
    switch ($Target) {
        "azure" { Deploy-Azure }
        "docker" { Deploy-Docker }
        "podman" { Deploy-Podman }
        "vercel" { Deploy-Vercel }
        "local" { Start-Local }
        default {
            Write-Log "Invalid target: $Target" $Red
            Show-Help
            exit 1
        }
    }

    Write-Log "Deployment completed successfully!" $Green

} catch {
    Write-Log "Deployment failed: $($_.Exception.Message)" $Red
    Write-Log "Check the log file for details: $LogFile" $Yellow
    exit 1
}