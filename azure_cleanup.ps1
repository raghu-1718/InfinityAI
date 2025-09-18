# Azure Cleanup Script for InfinityAI
# This script deletes duplicate and unused resources. Review before running.

# Log Analytics Workspaces (keep only one)
az monitor log-analytics workspace delete --resource-group InfinityAI-Prod-RG-West --workspace-name workspace-nfinityrodestky5h --yes

# Container Apps Environments (keep only one)
az containerapp env delete --name InfinityAI-Prod-Env --resource-group InfinityAI-Prod-RG-West --yes

# Azure Database for MySQL flexible server (keep only one in West US 2)
az mysql flexible-server delete --name infinityai --resource-group InfinityAI-Prod-RG-West --yes
az mysql flexible-server delete --name infinityai-mysql-west-eur --resource-group InfinityAI-Prod-RG-West --yes

# Resource Groups (delete if not needed)
az group delete --name ai_infinityai-backend-app-insights_a9cd1190-3fa8-4197-a160-50f40ac9c01b_managed --yes --no-wait

# (Optional) Delete any other unused resources below
# az containerapp delete --name <unused-app> --resource-group <group> --yes
# az staticwebapp delete --name <unused-swa> --resource-group <group> --yes
# az keyvault delete --name <unused-kv> --resource-group <group> --yes

# End of cleanup script
Write-Host "Azure cleanup complete. Review Azure Portal to confirm."
