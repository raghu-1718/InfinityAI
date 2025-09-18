# Verification and smoke test automation
# This script runs the automated_verification.ps1 script against the deployed backend.
# Usage: pwsh -File automate_verify.ps1 -BaseUrl "https://www.infinityai.pro"

param(
    [string]$BaseUrl = "https://www.infinityai.pro"
)

Write-Host "Running automated verification against $BaseUrl..."
pwsh -File ./automated_verification.ps1 -BaseUrl $BaseUrl

Write-Host "Done. Review output above for errors."
