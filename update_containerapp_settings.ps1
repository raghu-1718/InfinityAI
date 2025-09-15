# PowerShell script to update Azure Container App settings for InfinityAI

$containerAppName = "infinityai-backend-app"
$resourceGroup = "InfinityAI-Prod-RG-West"
$acrImage = "infinityaiprodacr.azurecr.io/infinityai-backend:latest"

# Update container app with recommended values
az containerapp update `
  --name $containerAppName `
  --resource-group $resourceGroup `
  --min-replicas 2 `
  --max-replicas 25 `
  --cpu 4 `
  --memory 6Gi `
  --image $acrImage

# Update scale settings (cooldown period and polling interval)
az containerapp scale update `
  --name $containerAppName `
  --resource-group $resourceGroup `
  --cooldown-period 300 `
  --polling-interval 30

Write-Host "Container App settings updated successfully."
