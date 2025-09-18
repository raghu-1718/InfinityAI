# DNS/domain automation for InfinityAI
# This script provides Azure CLI commands to set up DNS records for apex and www, and SSL verification steps.
# Usage: pwsh -File automate_dns.ps1

param(
    [string]$DnsZone = "infinityai.pro",
    [string]$ResourceGroup = "InfinityAI-Prod-RG-West",
    [string]$SwaEndpoint = "<your-swa-endpoint>",
    [string]$AppServiceDomain = "www.infinityai.pro",
    [string]$AppServiceDefault = "infinityai-backend-app.azurewebsites.net"
)

Write-Host "Add apex (infinityai.pro) record to SWA endpoint (A/ALIAS or CNAME as per SWA instructions):"
Write-Host "az network dns record-set cname set-record --resource-group $ResourceGroup --zone-name $DnsZone --record-set-name @ --cname $SwaEndpoint"

Write-Host "Add www CNAME to App Service default domain:"
Write-Host "az network dns record-set cname set-record --resource-group $ResourceGroup --zone-name $DnsZone --record-set-name www --cname $AppServiceDefault"

Write-Host "Verify SSL bindings in Azure Portal for both domains."
