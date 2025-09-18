# Backend MySQL and Key Vault automation
# This script sets DB connection env vars and recommends Key Vault usage for App Service.
# Usage: pwsh -File automate_backend_db_kv.ps1

param(
    [string]$AppName = "infinityai-backend-app",
    [string]$ResourceGroup = "infinityai-prod-rg-west",
    [string]$DbHost = "infinityai-prod-db.mysql.database.azure.com",
    [string]$DbUser = "infinityai_admin",
    [string]$DbName = "<your_db>",
    [string]$KeyVaultName = "<your-kv-westus2>"
)

Write-Host "Setting DB connection env vars (use Key Vault for secrets in production)..."
az webapp config appsettings set --name $AppName --resource-group $ResourceGroup --settings DB_HOST=$DbHost DB_USER=$DbUser DB_NAME=$DbName

Write-Host "Enable managed identity for App Service..."
az webapp identity assign --name $AppName --resource-group $ResourceGroup

Write-Host "Grant Key Vault access policy for secrets (manual step if needed):"
Write-Host "az keyvault set-policy --name $KeyVaultName --object-id <app-service-identity-object-id> --secret-permissions get list"

Write-Host "Store DB_PASSWORD and other secrets in Key Vault, then reference in App Service config as:"
Write-Host "@Microsoft.KeyVault(SecretUri=https://$KeyVaultName.vault.azure.net/secrets/DB-PASSWORD/)"

Write-Host "Done."
