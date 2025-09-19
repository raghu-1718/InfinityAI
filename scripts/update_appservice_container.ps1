# Update Azure App Service to use ACR container image and set health check

Param(
    [string]$ResourceGroup = "infinityai-prod-rg-west",
    [string]$AppName = "infinityai-backend-app",
    [string]$AcrName = "infinityaiprodacr",
    [string]$ImageName = "infinityai-backend",
    [string]$Tag = "latest",
  [string]$HealthPath = "/health",
  [string]$WebsitesPort = "8000",
  [string]$CorsAllowOrigins = "https://www.infinityai.pro"
)

Write-Host "Logging into Azure (expects az login already or federated credentials via pipeline)..."

$acr = az acr show --name $AcrName --resource-group $ResourceGroup --output json | ConvertFrom-Json
$acrLoginServer = $acr.loginServer
$image = "$acrLoginServer/$ImageName:$Tag"

Write-Host "Assigning system-managed identity to Web App (idempotent)" -ForegroundColor Cyan
az webapp identity assign --name $AppName --resource-group $ResourceGroup | Out-Null

# Grant AcrPull to the Web App managed identity
$principalId = az webapp show --name $AppName --resource-group $ResourceGroup --query identity.principalId -o tsv
$acrId = $acr.id
Write-Host "Granting AcrPull to principal $principalId on $acrId (safe to re-run)" -ForegroundColor Cyan
az role assignment create --assignee $principalId --role "AcrPull" --scope $acrId 2>$null | Out-Null

Write-Host "Configuring Web App to use container image $image" -ForegroundColor Cyan
az webapp config container set `
  --name $AppName `
  --resource-group $ResourceGroup `
  --docker-custom-image-name $image `
  --docker-registry-server-url https://$acrLoginServer | Out-Null

Write-Host "Setting health check path to $HealthPath" -ForegroundColor Cyan
az webapp update --name $AppName --resource-group $ResourceGroup --set siteConfig.healthCheckPath=$HealthPath | Out-Null

Write-Host "Setting WEBSITES_PORT=$WebsitesPort and CORS_ALLOW_ORIGINS=$CorsAllowOrigins" -ForegroundColor Cyan
az webapp config appsettings set --name $AppName --resource-group $ResourceGroup --settings WEBSITES_PORT=$WebsitesPort CORS_ALLOW_ORIGINS=$CorsAllowOrigins | Out-Null

Write-Host "Done. App Service configured to pull from ACR and health check updated." -ForegroundColor Green
