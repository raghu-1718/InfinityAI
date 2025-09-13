# PowerShell script to automate local test of FastAPI Docker container

# Build the Docker image (from api directory)
docker build -t infinityai-local-test .

# Run the container locally, mapping port 8000
# Remove any existing container with the same name first
docker rm -f infinityai-local-test-container 2>$null

docker run -d --name infinityai-local-test-container -p 8000:8000 infinityai-local-test

# Wait for container to start
Start-Sleep -Seconds 5

# Test the health endpoint
$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
Write-Host "Local /health endpoint response:"
Write-Host $response.Content
Write-Host "Status code: $($response.StatusCode)"

# Stop and remove the test container
docker rm -f infinityai-local-test-container
