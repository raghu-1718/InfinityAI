# Azure App Service backend best practices automation
# This script sets recommended app settings and health check for your backend App Service.
# Usage: pwsh -File automate_backend_azure.ps1

param(
    [string]$AppName = "infinityai-backend-app",
    [string]$ResourceGroup = "infinityai-prod-rg-west",
    [string]$AllowedOrigins = "https://infinityai.pro,https://www.infinityai.pro",
    [string]$HealthCheckPath = "/health"
)

Write-Host "Setting WEBSITES_PORT=8000 and CORS_ALLOW_ORIGINS..."
az webapp config appsettings set --name $AppName --resource-group $ResourceGroup --settings WEBSITES_PORT=8000 CORS_ALLOW_ORIGINS="$AllowedOrigins"

Write-Host "Configuring health check path..."
az webapp config set --name $AppName --resource-group $ResourceGroup --health-check-path $HealthCheckPath

Write-Host "Restarting App Service..."
az webapp restart --name $AppName --resource-group $ResourceGroup

Write-Host "Done. Please verify health in Azure Portal."
