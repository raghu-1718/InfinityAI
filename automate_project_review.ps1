# Automated project review and update script

Write-Host "=== Step 1: Installing coverage and pytest ==="
python -m pip install coverage pytest

Write-Host "=== Step 2: Running tests with coverage ==="
if (Test-Path "engine/core/tests") {
    coverage run -m pytest engine/core/tests/
    coverage report
    coverage html
    Write-Host "Coverage report generated: htmlcov/index.html"
} else {
    Write-Host "Test folder engine/core/tests not found."
}

Write-Host "=== Step 3: Installing flake8 and linting code ==="
python -m pip install flake8

$foldersToLint = @("api", "core", "engine/app", "engine/core")
foreach ($folder in $foldersToLint) {
    if (Test-Path $folder) {
        Write-Host "Linting $folder ..."
        flake8 $folder
    } else {
        Write-Host "$folder not found, skipping lint."
    }
}

Write-Host "=== Step 4: Checking environment variables ==="
$envFile = "config/.env.example"
if (Test-Path $envFile) {
    Write-Host "Required environment variables in $($envFile)"
    Get-Content $envFile | Where-Object { $_ -match "=" }
} else {
    Write-Host "Environment file config/.env.example not found!"
}

Write-Host "=== Step 5: Scanning for secrets in codebase ==="
Select-String -Path *.py,*.js,*.ps1 -Pattern "SECRET|TOKEN|PASSWORD|KEY" -CaseSensitive

Write-Host "=== Step 6: Finding duplicate files ==="
Get-ChildItem -Recurse | Group-Object Name | Where-Object { $_.Count -gt 1 } | Select-Object Name, Count

Write-Host "=== Step 7: Finding unused files (not modified in last 90 days) ==="
Get-ChildItem -Recurse | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) }

Write-Host "=== Step 8: Summary ==="
Write-Host "Review the above output for:"
Write-Host "- Test coverage and failures"
Write-Host "- Linting errors"
Write-Host "- Missing environment variables"
Write-Host "- Secrets in code"
Write-Host "- Duplicate and unused files"
Write-Host "Manual action may be required for code refactoring, documentation, and deployment configuration."