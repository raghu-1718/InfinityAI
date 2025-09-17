# migrate-to-azure-mysql.ps1
# Script to migrate from SingleStore to Azure Database for MySQL

Write-Host "🚀 Migrating InfinityAI.Pro to Azure Database for MySQL" -ForegroundColor Green

# Step 1: Copy the example terraform.tfvars
Write-Host "`n📋 Step 1: Setting up Terraform configuration..." -ForegroundColor Yellow
if (-not (Test-Path "infra/terraform.tfvars")) {
    Copy-Item "infra/terraform.tfvars.example" "infra/terraform.tfvars"
    Write-Host "✅ Created terraform.tfvars from example" -ForegroundColor Green
    Write-Host "⚠️  Please edit infra/terraform.tfvars and update the mysql_admin_password" -ForegroundColor Yellow
    Write-Host "   Recommended password format: 16+ chars with uppercase, lowercase, numbers, and symbols" -ForegroundColor Gray
    
    # Pause for user to edit the file
    Write-Host "`nPress Enter after you've updated the mysql_admin_password in terraform.tfvars..." -ForegroundColor Cyan
    Read-Host
}

# Step 2: Deploy Azure MySQL infrastructure
Write-Host "`n🏗️  Step 2: Deploying Azure MySQL infrastructure..." -ForegroundColor Yellow
Set-Location "infra"

Write-Host "Initializing Terraform..." -ForegroundColor Gray
terraform init

Write-Host "Planning Terraform deployment..." -ForegroundColor Gray
terraform plan

Write-Host "Applying Terraform configuration..." -ForegroundColor Gray
$terraformOutput = terraform apply -auto-approve

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Azure MySQL infrastructure deployed successfully!" -ForegroundColor Green
    
    # Extract connection string from Terraform output
    $mysqlFqdn = terraform output -raw mysql_server_fqdn
    $connectionTemplate = terraform output -raw mysql_connection_string
    
    Write-Host "`n📊 MySQL Server Details:" -ForegroundColor Cyan
    Write-Host "   Server FQDN: $mysqlFqdn" -ForegroundColor White
    Write-Host "   Connection Template: $connectionTemplate" -ForegroundColor White
} else {
    Write-Host "❌ Terraform deployment failed. Please check the errors above." -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Set-Location ".."

# Step 3: Data Migration
Write-Host "`n📦 Step 3: Data Migration Options..." -ForegroundColor Yellow
Write-Host "Choose your migration method:" -ForegroundColor White
Write-Host "1. Manual export/import (recommended for small datasets)" -ForegroundColor Gray
Write-Host "2. Use Azure Data Migration Service" -ForegroundColor Gray
Write-Host "3. Custom migration script" -ForegroundColor Gray

Write-Host "`n💡 Manual Migration Steps:" -ForegroundColor Cyan
Write-Host "1. Export data from SingleStore:" -ForegroundColor White
Write-Host "   mysqldump -h svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com -P 3333 -u raghu-f2476 -p db_raghu_d5f23 > backup.sql" -ForegroundColor Gray
Write-Host "2. Import to Azure MySQL:" -ForegroundColor White
Write-Host "   mysql -h $mysqlFqdn -u infinityai_admin -p infinityai < backup.sql" -ForegroundColor Gray

# Step 4: Update GitHub Secrets
Write-Host "`n🔑 Step 4: Update GitHub Secrets..." -ForegroundColor Yellow
Write-Host "Update the DATABASE_URL secret in GitHub with the new Azure MySQL connection string:" -ForegroundColor White

# Get the password from terraform.tfvars
$tfvarsContent = Get-Content "infra/terraform.tfvars"
$passwordLine = $tfvarsContent | Where-Object { $_ -match 'mysql_admin_password\s*=\s*"([^"]+)"' }
if ($passwordLine) {
    $password = [regex]::Match($passwordLine, 'mysql_admin_password\s*=\s*"([^"]+)"').Groups[1].Value
    $encodedPassword = [System.Web.HttpUtility]::UrlEncode($password)
    $newDatabaseUrl = "mysql+pymysql://infinityai_admin:$encodedPassword@$mysqlFqdn:3306/infinityai?charset=utf8mb4"
    
    Write-Host "`n📋 New DATABASE_URL for GitHub Secrets:" -ForegroundColor Cyan
    Write-Host $newDatabaseUrl -ForegroundColor Yellow
    
    Write-Host "`n🔗 Go to: https://github.com/raghu-1718/InfinityAI/settings/secrets/actions" -ForegroundColor Cyan
    Write-Host "Update the DATABASE_URL secret with the value above" -ForegroundColor White
} else {
    Write-Host "⚠️  Could not extract password from terraform.tfvars. Please manually construct the DATABASE_URL." -ForegroundColor Red
}

# Step 5: Update application configuration
Write-Host "`n⚙️  Step 5: Update Application Configuration..." -ForegroundColor Yellow
Write-Host "The application will automatically use the new DATABASE_URL once GitHub secrets are updated." -ForegroundColor White
Write-Host "Your Container App is configured to read from Key Vault, so no code changes needed!" -ForegroundColor Green

# Step 6: Test the migration
Write-Host "`n🧪 Step 6: Testing..." -ForegroundColor Yellow
Write-Host "1. Deploy your application with the new DATABASE_URL" -ForegroundColor White
Write-Host "2. Test database connectivity and application functionality" -ForegroundColor White
Write-Host "3. Once confirmed working, you can decommission SingleStore" -ForegroundColor White

Write-Host "`n✅ Migration preparation complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Perform data migration" -ForegroundColor Gray
Write-Host "2. Update GitHub DATABASE_URL secret" -ForegroundColor Gray
Write-Host "3. Deploy and test your application" -ForegroundColor Gray
Write-Host "4. Decommission SingleStore after confirming everything works" -ForegroundColor Gray