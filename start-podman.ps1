# Starts the InfinityAI stack using Podman Compose
param(
	[string]$EnvFile = "config/.env",
	[string]$PublicUrl = $env:PUBLIC_URL
)

Write-Host "Starting InfinityAI with Podman..."
if (Test-Path $EnvFile) {
	$env:COMPOSE_PROJECT_NAME = "infinityai"
	podman-compose --env-file $EnvFile -f podman-compose.yaml up --build -d
} else {
	Write-Warning "Env file '$EnvFile' not found. Proceeding without --env-file."
	$env:COMPOSE_PROJECT_NAME = "infinityai"
	podman-compose -f podman-compose.yaml up --build -d
}

$backendUrl = if ($PublicUrl) { "$PublicUrl" } else { "http://localhost:8000" }
$frontendUrl = if ($env:FRONTEND_PUBLIC_URL) { "$env:FRONTEND_PUBLIC_URL" } else { "http://localhost:3000" }
Write-Host "Backend: $backendUrl | Frontend: $frontendUrl"
