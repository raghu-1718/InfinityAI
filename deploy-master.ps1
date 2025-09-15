# deploy-master.ps1
# Master script to run all deployment steps
Write-Host "Azure Deployment Automation for InfinityAI.Pro" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Create scripts if they don't exist
$scripts = @{
    "deploy-step1.ps1" = "Build and push Docker image"
    "deploy-step2.ps1" = "Deploy to Container App"
    "deploy-step3.ps1" = "Configure logging and monitoring"
    "deploy-step4.ps1" = "Test endpoints"
    "deploy-step5.ps1" = "Verify deployment"
}

foreach ($script in $scripts.Keys) {
    if (!(Test-Path $script)) {
        Write-Warning "Script $script not found. Please ensure all deployment scripts are in the current directory."
        exit 1
    }
}

# Run steps in sequence
$steps = @(
    @{ Script = "deploy-step1.ps1"; Description = $scripts["deploy-step1.ps1"] },
    @{ Script = "deploy-step2.ps1"; Description = $scripts["deploy-step2.ps1"] },
    @{ Script = "deploy-step3.ps1"; Description = $scripts["deploy-step3.ps1"] },
    @{ Script = "deploy-step4.ps1"; Description = $scripts["deploy-step4.ps1"] },
    @{ Script = "deploy-step5.ps1"; Description = $scripts["deploy-step5.ps1"] }
)

$stepNumber = 1
foreach ($step in $steps) {
    Write-Host "`nRunning Step $stepNumber/5: $($step.Description)..." -ForegroundColor Cyan
    & ".\$($step.Script)"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Step $stepNumber ($($step.Description)) failed. Deployment stopped."
        exit 1
    }
    
    $stepNumber++
}

Write-Host "`nDeployment completed successfully!" -ForegroundColor Green