<#!
.SYNOPSIS
  Fetch secrets from Azure Key Vault and apply them to the Azure Web App as app settings.

.DESCRIPTION
  Designed to keep DB credentials & sensitive config out of GitHub secrets. Use managed identity + Key Vault access policies / RBAC.

.EXAMPLE
  pwsh scripts/keyvault-sync-appsettings.ps1 -SubscriptionId <SUB> -ResourceGroup InfinityAI-Prod-RG-West -WebAppName infinityai-backend-app `
    -KeyVaultName kv-infinityai-prod -SecretMap @{ DB_HOST='db-host'; DB_USER='db-user'; DB_PASSWORD='db-password'; DB_NAME='db-name' }
#!>
param(
  [Parameter(Mandatory)] [string]$SubscriptionId,
  [Parameter(Mandatory)] [string]$ResourceGroup,
  [Parameter(Mandatory)] [string]$WebAppName,
  [Parameter(Mandatory)] [string]$KeyVaultName,
  # Hashtable: AppSettingName = SecretNameInKV
  [Parameter(Mandatory)] [hashtable]$SecretMap,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-AzContext -Subscription $SubscriptionId | Out-Null

Write-Host "== Key Vault → App Service Settings Sync ==" -ForegroundColor Cyan
Write-Host "Key Vault: $KeyVaultName" -ForegroundColor Gray

$settings = @{}
foreach ($k in $SecretMap.Keys) {
  $secretName = $SecretMap[$k]
  $secret = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name $secretName -ErrorAction Stop
  $settings[$k] = $secret.SecretValueText
}

Write-Host "Resolved settings (values masked):" -ForegroundColor Cyan
foreach ($pair in $settings.GetEnumerator()) { Write-Host "  $($pair.Key)=***" -ForegroundColor Gray }

if ($DryRun) { Write-Host "Dry run mode - not applying." -ForegroundColor Yellow; exit 0 }

az webapp config appsettings set -g $ResourceGroup -n $WebAppName --settings @settings | Out-Null
Write-Host "Applied Key Vault secrets to Web App." -ForegroundColor Green
