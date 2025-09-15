# deploy-step3.ps1
# Configure logging and monitoring
Write-Host "Step 3: Setting up structured logging and monitoring..." -ForegroundColor Green

try {
    # Get subscription ID
    $SUBSCRIPTION_ID = az account show --query id -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Failed to get subscription ID" }

    # Create Application Insights resource if not exists
    Write-Host "Checking if Application Insights exists..."
    $AI_EXISTS = az resource list --resource-group InfinityAI-Prod-RG-West --resource-type "microsoft.insights/components" --query "[?name=='infinityai-insights']" -o tsv
    
    if (!$AI_EXISTS) {
        Write-Host "Creating Application Insights resource..."
        az monitor app-insights component create `
            --app infinityai-insights `
            --location "West US 2" `
            --resource-group InfinityAI-Prod-RG-West `
            --application-type web
        if ($LASTEXITCODE -ne 0) { throw "Failed to create Application Insights" }
    }

    # Get Application Insights instrumentation key
    $INSTRUMENTATION_KEY = az monitor app-insights component show `
        --app infinityai-insights `
        --resource-group InfinityAI-Prod-RG-West `
        --query instrumentationKey -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Failed to get instrumentation key" }

    # Update Container App with instrumentation key
    Write-Host "Updating Container App with instrumentation key..."
    az containerapp update `
        --name infinityai-backend-app `
        --resource-group InfinityAI-Prod-RG-West `
        --env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=$INSTRUMENTATION_KEY"
    if ($LASTEXITCODE -ne 0) { throw "Failed to update Container App with instrumentation key" }

    # Configure diagnostic settings
    Write-Host "Configuring diagnostic settings..."
    az monitor diagnostic-settings create `
        --name "infinityai-diagnostics" `
        --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/InfinityAI-Prod-RG-West/providers/Microsoft.App/containerApps/infinityai-backend-app" `
        --workspace "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/InfinityAI-Prod-RG-West/providers/Microsoft.OperationalInsights/workspaces/workspace-nfinityrodestky5h" `
        --logs '[{"category": "ContainerAppConsoleLogs", "enabled": true}, {"category": "ContainerAppSystemLogs", "enabled": true}]' `
        --metrics '[{"category": "AllMetrics", "enabled": true}]'
    if ($LASTEXITCODE -ne 0) { throw "Failed to configure diagnostic settings" }

    Write-Host "Logging and monitoring successfully configured." -ForegroundColor Green
    exit 0
} catch {
    Write-Error "Error in Step 3: $_"
    exit 1
}