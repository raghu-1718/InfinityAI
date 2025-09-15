# deploy-step4.ps1
# Test endpoints
Write-Host "Step 4: Testing endpoints..." -ForegroundColor Green

try {
    # Get Container App URL
    Write-Host "Getting Container App URL..."
    $APP_URL = az containerapp show `
        --name infinityai-backend-app `
        --resource-group InfinityAI-Prod-RG-West `
        --query "properties.configuration.ingress.fqdn" -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Failed to get Container App URL" }
    
    Write-Host "Container App URL: https://$APP_URL"

    # Test health endpoint
    Write-Host "Testing health endpoint..."
    $HEALTH_RESPONSE = Invoke-RestMethod -Uri "https://$APP_URL/health" -Method Get -ErrorAction SilentlyContinue
    if ($HEALTH_RESPONSE.status -eq "healthy") {
        Write-Host "Health check passed: $($HEALTH_RESPONSE | ConvertTo-Json)" -ForegroundColor Green
    } else {
        Write-Warning "Health check returned unexpected response: $($HEALTH_RESPONSE | ConvertTo-Json)"
    }

    # Test API endpoints
    Write-Host "Testing API endpoints..."
    try {
        $FUNDS_RESPONSE = Invoke-RestMethod -Uri "https://$APP_URL/funds/1" -Method Get -ErrorAction SilentlyContinue
        Write-Host "Funds endpoint response: $($FUNDS_RESPONSE | ConvertTo-Json)" -ForegroundColor Green
    } catch {
        Write-Warning "Funds endpoint test failed: $_"
    }

    Write-Host "Endpoint testing completed." -ForegroundColor Green
    exit 0
} catch {
    Write-Error "Error in Step 4: $_"
    exit 1
}