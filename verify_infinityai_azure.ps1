# Azure resource details
$backendUrl = "https://infinityai-backend-app.azurewebsites.net/health"
$resourceGroup = "InfinityAI-Prod-RG-West"
$acrName = "infinityaiprodacr"
$containerEnv = "InfinityAI-Prod-RG-West-env"
$subscriptionId = "62fc147a-2efc-4494-be1f-faa521439799"

Write-Host "`n=== InfinityAI Azure Resource Verification ===`n"

# 1. Test Backend API Health Endpoint
Write-Host "Testing backend API health endpoint..."
try {
    $response = Invoke-WebRequest -Uri $backendUrl -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend API is healthy. Response:" $response.Content
    } else {
        Write-Host "❌ Backend API returned status:" $response.StatusCode
    }
} catch {
    Write-Host "❌ Failed to reach backend API:" $_
}

# 2. List Container Registry Images
Write-Host "`nListing images in Azure Container Registry ($acrName)..."
az acr repository list --name $acrName --resource-group $resourceGroup --output table

# 3. List Container Apps in Environment
Write-Host "`nListing container apps in environment ($containerEnv)..."
az containerapp list --resource-group $resourceGroup --query "[].{name:name, env:environmentId, status:provisioningState}" --output table

# 4. (Optional) List Databases in MySQL (requires mysql client and password)
# $mysqlServer = "infinityai-prod-db.mysql.database.azure.com"
# $mysqlUser = "infinityai_admin@infinityai-prod-db"
# $mysqlPassword = "<YOUR_PASSWORD>"
# mysql -h $mysqlServer -u $mysqlUser -p$mysqlPassword -e "SHOW DATABASES;"

# 5. (Optional) Query Log Analytics Workspace (requires workspace name)
# $workspaceName = "workspace-nfinityrodesky5h"
# az monitor log-analytics query --workspace $workspaceName --query "Heartbeat | take 5"

Write-Host "`n=== Verification Complete ===`n"