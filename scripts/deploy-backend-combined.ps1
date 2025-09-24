<#!
.SYNOPSIS
  Builds & pushes backend container (optional if image tag supplied), updates Azure Web App to new image, applies app settings,
  adds MySQL firewall rules for provided outbound IPs, and polls /health until database=connected.

.PREREQUISITES
  - Az PowerShell modules installed (Az.Accounts, Az.Websites, Az.ContainerRegistry, Az.MySql)
  - OIDC or interactive login: Connect-AzAccount; Set-AzContext -Subscription <SUB_ID>
  - ACR, Web App, MySQL Flexible Server already created.

.EXAMPLE
  pwsh scripts/deploy-backend-combined.ps1 -SubscriptionId 0000-... -ResourceGroup InfinityAI-Prod-RG-West -WebAppName infinityai-backend-app `
    -AcrName infinityaiprodacr -ImageName infinityai-backend -Dockerfile Dockerfile -ContextPath . `
    -MysqlServer infinityai-prod-db -DbName infinityai_prod_db -DbUser infinityai_admin@infinityai-prod-db -DbPasswordSecretEnv DB_PASSWORD `
    -AppServiceOutboundIps "20.51.10.100","20.51.10.101"

.NOTES
  Set the DB password in an environment variable (e.g., $Env:DB_PASSWORD) rather than passing plain text.
#!>
param(
  [Parameter(Mandatory)] [string]$SubscriptionId,
  [Parameter(Mandatory)] [string]$ResourceGroup,
  [Parameter(Mandatory)] [string]$WebAppName,
  [Parameter(Mandatory)] [string]$AcrName,
  [Parameter(Mandatory)] [string]$ImageName,
  [string]$ImageTag = $(Get-Date -Format 'yyyyMMddHHmmss'),
  [string]$Dockerfile = 'Dockerfile',
  [string]$ContextPath = '.',
  [int]$HealthTimeoutSeconds = 300,
  [int]$HealthPollIntervalSeconds = 5,
  # DB / MySQL
  [Parameter(Mandatory)] [string]$MysqlServer, # short server name without domain
  [Parameter(Mandatory)] [string]$DbName,
  [Parameter(Mandatory)] [string]$DbUser,
  [string]$DbPasswordSecretEnv = 'DB_PASSWORD',
  [string[]]$AppServiceOutboundIps = @(),
  [switch]$SkipBuild,
  [switch]$AllowFallbackLogin,
  [string]$AdminUsername = '',
  [string]$AdminPasswordHashEnv = 'ADMIN_PASSWORD_HASH'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "== InfinityAI Combined Backend Deploy ==" -ForegroundColor Cyan
Write-Host "Subscription: $SubscriptionId" -ForegroundColor Gray
Set-AzContext -Subscription $SubscriptionId | Out-Null

# Resolve ACR login server
$acr = Get-AzContainerRegistry -Name $AcrName -ResourceGroupName $ResourceGroup
if (-not $acr) { throw "ACR '$AcrName' not found" }
$loginServer = $acr.LoginServer

# DB password & optional admin hash from env
$dbPassword = [Environment]::GetEnvironmentVariable($DbPasswordSecretEnv)
if (-not $dbPassword) { throw "Environment variable '$DbPasswordSecretEnv' (DB password) not set" }
$adminHash = [Environment]::GetEnvironmentVariable($AdminPasswordHashEnv)

# Build & push image unless skipped
$fullTag = "$loginServer/$ImageName:$ImageTag"
if ($SkipBuild) {
  Write-Host "Skipping build (using provided tag $fullTag)" -ForegroundColor Yellow
} else {
  Write-Host "Building image $fullTag ..." -ForegroundColor Cyan
  docker build -f $Dockerfile -t $fullTag $ContextPath
  Write-Host "Pushing image $fullTag ..." -ForegroundColor Cyan
  docker push $fullTag
}

# Ensure Web App identity has AcrPull (idempotent)
Write-Host "Ensuring Web App identity & AcrPull role..." -ForegroundColor Cyan
$identity = az webapp identity assign -g $ResourceGroup -n $WebAppName --query principalId -o tsv 2>$null
if (-not $identity) { $identity = az webapp identity show -g $ResourceGroup -n $WebAppName --query principalId -o tsv }
$acrId = $acr.Id
az role assignment create --assignee $identity --role AcrPull --scope $acrId 2>$null | Out-Null

Write-Host "Configuring container image on Web App..." -ForegroundColor Cyan
az webapp config container set `
  --name $WebAppName `
  --resource-group $ResourceGroup `
  --docker-custom-image-name $fullTag `
  --docker-registry-server-url https://$loginServer | Out-Null

# Compose app settings
$mysqlFqdn = "$MysqlServer.mysql.database.azure.com"
$settings = @(
  "WEBSITES_PORT=8000"
  "DB_HOST=$mysqlFqdn"
  "DB_NAME=$DbName"
  "DB_USER=$DbUser"
  "DB_PASSWORD=$dbPassword"
  "CORS_ALLOW_ORIGINS=https://infinityai.pro,https://www.infinityai.pro,https://api.infinityai.pro"
  "DB_CONNECT_TIMEOUT=5"
)
if ($AllowFallbackLogin -and $AdminUsername -and $adminHash) {
  $settings += "ALLOW_FALLBACK_LOGIN=true"
  $settings += "ADMIN_USERNAME=$AdminUsername"
  $settings += "ADMIN_PASSWORD_HASH=$adminHash"
}

Write-Host "Applying app settings (password masked)..." -ForegroundColor Cyan
($settings | ForEach-Object { $_ -replace 'DB_PASSWORD=.*','DB_PASSWORD=***masked***' }) | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
az webapp config appsettings set -g $ResourceGroup -n $WebAppName --settings $settings | Out-Null

Write-Host "Setting health check path /health" -ForegroundColor Cyan
az webapp update -g $ResourceGroup -n $WebAppName --set siteConfig.healthCheckPath=/health | Out-Null

Write-Host "Restarting Web App..." -ForegroundColor Cyan
az webapp restart -g $ResourceGroup -n $WebAppName | Out-Null

# Firewall rules for MySQL (add outbound IPs if provided)
if ($AppServiceOutboundIps.Count -gt 0) {
  Write-Host "Adding MySQL firewall rules for outbound IPs..." -ForegroundColor Cyan
  foreach ($ip in $AppServiceOutboundIps) {
    $ruleName = "appsvc_$($ip.Replace('.','_'))"
    az mysql flexible-server firewall-rule create `
      --resource-group $ResourceGroup `
      --name $MysqlServer `
      --rule-name $ruleName `
      --start-ip-address $ip `
      --end-ip-address $ip 2>$null | Out-Null
  }
}

# Poll health until DB connected
$healthUrl = "https://$WebAppName.azurewebsites.net/health"
Write-Host "Polling $healthUrl for database=connected (timeout ${HealthTimeoutSeconds}s)" -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds($HealthTimeoutSeconds)
while ((Get-Date) -lt $deadline) {
  try {
    $resp = Invoke-RestMethod -Uri $healthUrl -Method GET -TimeoutSec 10
    $dbStatus = $resp.database
    Write-Host "Database status: $dbStatus" -ForegroundColor Gray
    if ($dbStatus -eq 'connected') {
      Write-Host "SUCCESS: Database connected." -ForegroundColor Green
      break
    }
  } catch {
    Write-Host "Health request failed: $($_.Exception.Message)" -ForegroundColor Yellow
  }
  Start-Sleep -Seconds $HealthPollIntervalSeconds
}
if (-not $dbStatus -or $dbStatus -ne 'connected') {
  Write-Warning "Database did not reach 'connected' before timeout. Check firewall / credentials."
  exit 2
}

Write-Host "Deployment complete." -ForegroundColor Green