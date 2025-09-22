Azure Backend Container Deployment
=================================

This guide wires the Azure Web App to the correct container image from ACR and ensures readiness/health settings.

Prerequisites
-------------
- Azure CLI logged in with access to the subscription
- Existing Azure Container Registry (ACR)
- Existing Azure Web App for Containers

Environment (example)
---------------------

```bash
RESOURCE_GROUP="InfinityAI-Prod-RG-West"
WEBAPP_NAME="infinityai-backend-app"
ACR_NAME="infinityaiprodacr"
ACR_LOGIN_SERVER="infinityaiprodacr.azurecr.io"
IMAGE_NAME="infinityai-backend"
IMAGE_TAG="latest"   # or a specific SHA
APP_PORT=8000
```

Wire Web App to ACR image
-------------------------

```bash
# Enable system-assigned managed identity (idempotent)
PRINCIPAL_ID=$(az webapp identity assign -g "$RESOURCE_GROUP" -n "$WEBAPP_NAME" --query principalId -o tsv)

# Grant AcrPull on ACR
ACR_ID=$(az acr show -n "$ACR_NAME" --query id -o tsv)
az role assignment create --assignee "$PRINCIPAL_ID" --role AcrPull --scope "$ACR_ID" || true

# Point Web App to the container image
IMAGE_REF="$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"
az webapp config container set \
  --name "$WEBAPP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --docker-custom-image-name "$IMAGE_REF" \
  --enable-app-service-storage false

# Set required app settings
az webapp config appsettings set \
  --name "$WEBAPP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings WEBSITES_PORT=$APP_PORT CORS_ALLOW_ORIGINS="https://www.infinityai.pro,https://api.infinityai.pro"

# Health check path
az webapp update \
  --name "$WEBAPP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --set siteConfig.healthCheckPath=/health

# Restart to apply
az webapp restart --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP"
```

Verification
------------

```bash
HOST=$(az webapp show -n "$WEBAPP_NAME" -g "$RESOURCE_GROUP" --query defaultHostName -o tsv)
curl -sf https://$HOST/health | jq .
```

If the response shows `status: healthy`, the backend container is running with dependencies installed (including MySQL driver).
