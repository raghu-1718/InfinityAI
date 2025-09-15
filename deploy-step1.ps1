# deploy-step1.ps1
# Build and push Docker image to ACR
Write-Host "Step 1: Building and pushing Docker image to ACR..." -ForegroundColor Green

try {
    # Build Docker image from Dockerfile
    Write-Host "Building Docker image..."
    docker build -t infinityai-backend:latest .
    if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }

    # Login to Azure Container Registry
    Write-Host "Logging into ACR..."
    az acr login --name infinityaiprodacr
    if ($LASTEXITCODE -ne 0) { throw "ACR login failed" }

    # Tag and push image to ACR
    Write-Host "Tagging and pushing image..."
    docker tag infinityai-backend:latest infinityaiprodacr.azurecr.io/infinityai-backend:latest
    docker push infinityaiprodacr.azurecr.io/infinityai-backend:latest
    if ($LASTEXITCODE -ne 0) { throw "Push to ACR failed" }

    Write-Host "Image successfully built and pushed to ACR." -ForegroundColor Green
    exit 0
} catch {
    Write-Error "Error in Step 1: $_"
    exit 1
}