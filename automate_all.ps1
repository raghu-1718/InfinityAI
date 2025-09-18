# Master automation script for InfinityAI Azure deployment and verification
# Usage: pwsh -File automate_all.ps1

Write-Host "[1/5] Enforcing backend App Service best practices..."
pwsh -File ./automate_backend_azure.ps1

Write-Host "[2/5] Enforcing backend DB and Key Vault config..."
pwsh -File ./automate_backend_db_kv.ps1

Write-Host "[3/5] Enforcing DNS/domain best practices..."
pwsh -File ./automate_dns.ps1

Write-Host "[4/5] Running backend CI/CD pipeline (GitHub Action must be enabled in repo)..."
Write-Host "  - Push to main branch to trigger .github/workflows/deploy-backend.yml"

Write-Host "[5/5] Running verification and smoke tests..."
pwsh -File ./automate_verify.ps1

Write-Host "Automation complete. Review output and Azure Portal for status."
