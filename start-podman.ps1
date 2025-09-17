# Starts the InfinityAI stack using Podman Compose
param(
	[string]$EnvFile = "config/.env"
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

Write-Host "Backend: http://localhost:8000 | Frontend: http://localhost:3000"
