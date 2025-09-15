# deploy-step5.ps1
# Verify deployment success
Write-Host "Step 5: Verifying deployment..." -ForegroundColor Green

try {
    # Check Container App status
    Write-Host "Checking Container App status..."
    $APP_STATUS = az containerapp show `
        --name infinityai-backend-app `
        --resource-group InfinityAI-Prod-RG-West `
        --query "properties.provisioningState" -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Failed to check Container App status" }
    
    Write-Host "Container App provisioning state: $APP_STATUS" -ForegroundColor $(if ($APP_STATUS -eq "Succeeded") { "Green" } else { "Red" })

    # Check for active replicas
    Write-Host "Checking for active replicas..."
    $REPLICAS = az containerapp revision list `
        --name infinityai-backend-app `
        --resource-group InfinityAI-Prod-RG-West `
        --query "[?active].{Name:name, Replicas:replicas}" -o json | ConvertFrom-Json
    
    if ($REPLICAS.Count -eq 0 -or $REPLICAS.Replicas -eq 0) {
        Write-Warning "No active replicas found!"
    } else {
        Write-Host "Active replicas: $($REPLICAS | ConvertTo-Json)" -ForegroundColor Green
    }

    # Check MySQL database status
    Write-Host "Checking MySQL database status..."
    $DB_STATUS = az mysql flexible-server show `
        --name infinityai-prod-db `
        --resource-group InfinityAI-Prod-RG-West `
        --query "state" -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Failed to check MySQL database status" }
    
    Write-Host "MySQL database state: $DB_STATUS" -ForegroundColor $(if ($DB_STATUS -eq "Ready") { "Green" } else { "Red" })

    # Overall verification result
    if ($APP_STATUS -eq "Succeeded" -and $REPLICAS.Count -gt 0 -and $REPLICAS.Replicas -gt 0 -and $DB_STATUS -eq "Ready") {
        Write-Host "Deployment verification PASSED. All components are running correctly." -ForegroundColor Green
    } else {
        Write-Warning "Deployment verification FAILED. Some components are not running correctly."
    }

    exit 0
} catch {
    Write-Error "Error in Step 5: $_"
    exit 1
}