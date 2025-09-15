# deploy-step2.ps1
# Deploy to Container App with health check and proper configuration
Write-Host "Step 2: Deploying to Container App with proper configuration..." -ForegroundColor Green

try {
    # Get database credentials (consider using Key Vault in production)
    $DB_HOST = "infinityai-prod-db.mysql.database.azure.com"
    $DB_USER = Read-Host "Enter database username"
    $DB_PASSWORD = Read-Host -AsSecureString "Enter database password"
    $DB_PASSWORD_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASSWORD))
    $DB_NAME = "infinityai"
    
    # Update container app with proper configuration
    Write-Host "Updating Container App with new image and configuration..."
    az containerapp update `
        --name infinityai-backend-app `
        --resource-group InfinityAI-Prod-RG-West `
        --image infinityaiprodacr.azurecr.io/infinityai-backend:latest `
        --min-replicas 1 `
        --max-replicas 10 `
        --set-env-vars "DB_HOST=$DB_HOST" "DB_USER=$DB_USER" "DB_PASSWORD=$DB_PASSWORD_PLAIN" "DB_NAME=$DB_NAME" "APP_ENV=production" "LOG_LEVEL=INFO" "APP_PORT=8000" "PYTHONUNBUFFERED=1"
    if ($LASTEXITCODE -ne 0) { throw "Container App update failed" }

    # Configure health probe
    Write-Host "Configuring health probe..."
    az containerapp ingress update `
        --name infinityai-backend-app `
        --resource-group InfinityAI-Prod-RG-West `
        --target-port 8000 `
        --transport http `
        --health-probe-path /health `
        --health-probe-protocol http `
        --health-probe-interval 30 `
        --health-probe-timeout 10 `
        --health-probe-retries 3
    if ($LASTEXITCODE -ne 0) { throw "Health probe configuration failed" }

    # Force a revision for the changes to take effect
    Write-Host "Creating new revision to apply changes..."
    az containerapp update `
        --name infinityai-backend-app `
        --resource-group InfinityAI-Prod-RG-West `
        --revision-suffix manual-update
    if ($LASTEXITCODE -ne 0) { throw "Revision update failed" }

    Write-Host "Container App successfully deployed with proper configuration." -ForegroundColor Green
    exit 0
} catch {
    Write-Error "Error in Step 2: $_"
    exit 1
}