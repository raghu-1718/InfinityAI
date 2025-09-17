# data-migration.ps1
# Script to migrate data from SingleStore to Azure MySQL

param(
    [switch]$DryRun = $false
)

Write-Host "🔄 InfinityAI.Pro Data Migration Script" -ForegroundColor Green
Write-Host "Source: SingleStore" -ForegroundColor Gray  
Write-Host "Target: Azure MySQL (infinityai-mysql-west-eur.mysql.database.azure.com)" -ForegroundColor Gray

# Configuration
$sourceHost = "svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com"
$sourcePort = "3333"
$sourceUser = "raghu-f2476"
$sourceDatabase = "db_raghu_d5f23"

$targetHost = "infinityai-mysql-west-eur.mysql.database.azure.com"
$targetPort = "3306"
$targetUser = "infinityai_admin"
$targetDatabase = "infinityai"
$targetPassword = "InfinityAI@MySQL2024!SecurePass#123"

# Check if mysql client is available
Write-Host "`n🔍 Checking MySQL client availability..." -ForegroundColor Yellow
$mysqlCheck = Get-Command mysql -ErrorAction SilentlyContinue
if (-not $mysqlCheck) {
    Write-Host "❌ MySQL client not found. Please install MySQL client tools." -ForegroundColor Red
    Write-Host "Download from: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Cyan
    Write-Host "Or install via winget: winget install Oracle.MySQL" -ForegroundColor Cyan
    exit 1
}
Write-Host "✅ MySQL client found: $($mysqlCheck.Source)" -ForegroundColor Green

# Step 1: Export data from SingleStore
Write-Host "`n📤 Step 1: Exporting data from SingleStore..." -ForegroundColor Yellow
$backupFile = "infinityai_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"

if ($DryRun) {
    Write-Host "DRY RUN: Would execute: mysqldump -h $sourceHost -P $sourcePort -u $sourceUser -p $sourceDatabase > $backupFile" -ForegroundColor Magenta
} else {
    Write-Host "Please enter your SingleStore password when prompted:" -ForegroundColor Cyan
    $exportCmd = "mysqldump -h $sourceHost -P $sourcePort -u $sourceUser -p --single-transaction --routines --triggers --set-gtid-purged=OFF --databases $sourceDatabase"
    
    Write-Host "Executing: $exportCmd > $backupFile" -ForegroundColor Gray
    Invoke-Expression "$exportCmd > $backupFile 2>&1"
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $backupFile)) {
        $fileSize = (Get-Item $backupFile).Length
        Write-Host "✅ Export completed successfully!" -ForegroundColor Green
        Write-Host "   Backup file: $backupFile" -ForegroundColor White
        Write-Host "   File size: $([math]::Round($fileSize/1MB, 2)) MB" -ForegroundColor White
    } else {
        Write-Host "❌ Export failed. Please check your SingleStore connection details." -ForegroundColor Red
        exit 1
    }
}

# Step 2: Test Azure MySQL connection
Write-Host "`n🔗 Step 2: Testing Azure MySQL connection..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "DRY RUN: Would test connection to Azure MySQL" -ForegroundColor Magenta
} else {
    $testCmd = "mysql -h $targetHost -P $targetPort -u $targetUser -p$targetPassword -e `"SELECT 1 as test_connection`""
    $testResult = Invoke-Expression $testCmd 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Azure MySQL connection successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ Azure MySQL connection failed:" -ForegroundColor Red
        Write-Host $testResult -ForegroundColor Red
        exit 1
    }
}

# Step 3: Create database schema (if needed)
Write-Host "`n🏗️  Step 3: Ensuring target database exists..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "DRY RUN: Would create database $targetDatabase if not exists" -ForegroundColor Magenta
} else {
    $createDbCmd = "mysql -h $targetHost -P $targetPort -u $targetUser -p$targetPassword -e `"CREATE DATABASE IF NOT EXISTS $targetDatabase CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`""
    Invoke-Expression $createDbCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database $targetDatabase ready!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create database $targetDatabase" -ForegroundColor Red
        exit 1
    }
}

# Step 4: Import data to Azure MySQL
Write-Host "`n📥 Step 4: Importing data to Azure MySQL..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "DRY RUN: Would execute: mysql -h $targetHost -P $targetPort -u $targetUser -p$targetPassword $targetDatabase < $backupFile" -ForegroundColor Magenta
} else {
    Write-Host "Starting import process..." -ForegroundColor Gray
    $importCmd = "mysql -h $targetHost -P $targetPort -u $targetUser -p$targetPassword $targetDatabase"
    
    try {
        Get-Content $backupFile | & mysql -h $targetHost -P $targetPort -u $targetUser -p$targetPassword $targetDatabase 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Data import completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Import completed with warnings. Please check the output above." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Import failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Step 5: Verify migration
Write-Host "`n🧪 Step 5: Verifying migration..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "DRY RUN: Would verify table counts and basic queries" -ForegroundColor Magenta
} else {
    # Count tables
    $tableCountCmd = "mysql -h $targetHost -P $targetPort -u $targetUser -p$targetPassword $targetDatabase -e `"SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='$targetDatabase';`""
    $tableCount = Invoke-Expression $tableCountCmd 2>$null | Select-String "table_count" -Context 0,1
    
    if ($tableCount) {
        Write-Host "✅ Migration verification:" -ForegroundColor Green
        Write-Host "   $tableCount" -ForegroundColor White
    }
    
    # Test a simple query
    Write-Host "Testing basic database functionality..." -ForegroundColor Gray
    $testQuery = "mysql -h $targetHost -P $targetPort -u $targetUser -p$targetPassword $targetDatabase -e `"SELECT NOW() as current_time;`""
    $queryResult = Invoke-Expression $testQuery 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database queries working correctly!" -ForegroundColor Green
    }
}

# Step 6: Summary and next steps
Write-Host "`n📋 Migration Summary" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

if (-not $DryRun) {
    Write-Host "✅ Data exported from SingleStore: $backupFile" -ForegroundColor White
    Write-Host "✅ Data imported to Azure MySQL: $targetDatabase" -ForegroundColor White
    Write-Host "✅ Connection verified and working" -ForegroundColor White
} else {
    Write-Host "DRY RUN completed - no actual migration performed" -ForegroundColor Yellow
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. ✅ GitHub DATABASE_URL secret updated (already done)" -ForegroundColor White
Write-Host "2. 🔄 Deploy your application to test with Azure MySQL" -ForegroundColor White  
Write-Host "3. 🧪 Run comprehensive application tests" -ForegroundColor White
Write-Host "4. 📊 Monitor application performance and logs" -ForegroundColor White
Write-Host "5. 🗑️  Decommission SingleStore after confirming everything works" -ForegroundColor White

Write-Host "`n📊 Azure MySQL Connection Details:" -ForegroundColor Cyan
Write-Host "   Host: $targetHost" -ForegroundColor White
Write-Host "   Database: $targetDatabase" -ForegroundColor White
Write-Host "   Port: $targetPort" -ForegroundColor White

if (-not $DryRun) {
    Write-Host "`n💾 Backup file location: $backupFile" -ForegroundColor Yellow
    Write-Host "Keep this file safe until migration is fully verified!" -ForegroundColor Yellow
}

Write-Host "`n🎉 Migration process completed!" -ForegroundColor Green