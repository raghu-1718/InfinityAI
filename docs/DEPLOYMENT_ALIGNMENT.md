# Deployment Alignment (Azure + GitHub)

This document summarizes current deployment configuration and recommended actions to align CI/CD and Azure resources.

## Current State

- Backend CI (`.github/workflows/ci-cd.yml`):
  - Tests with TESTING=1
  - Builds/pushes image to GHCR (`ghcr.io/<owner>/<repo>:latest`)
  - Deploys to Azure Container Apps: resourceGroup=`InfinityAI`, app=`infinityai-backend-app` using GHCR image
  - Runs Alembic migrations via Poetry, `DATABASE_URL` secret required

- Scripts:
  - `update_containerapp_settings.ps1` uses RG `InfinityAI-Prod-RG-West` and ACR `infinityaiprodacr.azurecr.io`
  - `verify_infinityai_azure.ps1` checks a specific Container App FQDN in westus2

- Frontend:
  - Azure Static Web Apps workflow active (Node 18), deploys `dashboard/build` using `AZURE_STATIC_WEB_APPS_API_TOKEN_*`
  - `vercel.json` disabled

## Mismatches

1. Python version in CI: uses 3.9, but project requires >=3.10. Use 3.12.
2. Registry: CI uses GHCR; scripts reference ACR. Choose one and standardize.
3. Resource groups/names: Workflow vs scripts differ. Align RG, environment, and app name.
4. Custom domain: ensure DNS and TLS bindings for the chosen services, and CORS (`CORS_ALLOW_ORIGINS`) updated to include custom domain(s).

## Recommendations

1. Update CI Python to 3.12.
2. Decide registry:
   - Keep GHCR: configure Container App pull secret for GHCR and remove ACR image references from scripts.
   - Or move to ACR: push from CI to ACR; update deploy step and scripts accordingly.
3. Unify resource group/app names across `ci-cd.yml`, `update_containerapp_settings.ps1`, and `verify_infinityai_azure.ps1`.
4. Confirm Container App hostname in Azure Portal and update `verify_infinityai_azure.ps1` accordingly.
5. Frontend custom domain via Azure Static Web Apps: add domain in SWA, validate TXT, set CNAME, ensure backend CORS allows the domain.

## Secrets Checklist

- GitHub Secrets:
  - `AZURE_CREDENTIALS` (for azure/login)
  - `DATABASE_URL` (for migrations)
  - `AZURE_STATIC_WEB_APPS_API_TOKEN_...` (for SWA)
- Azure:
  - Container App ingress configured (external)
  - Custom domain bindings (SWA + Container App if needed)
  - Pull secret for registry (GHCR or ACR)
