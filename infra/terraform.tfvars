# Terraform variables for InfinityAI.Pro Azure infrastructure
# Copy this file to terraform.tfvars and update the values

# Resource Group and Location
resource_group_name = "InfinityAI-Prod-RG-West"
location           = "westeurope"
tenant_id          = "7bdda027-39ab-4374-9aae-3455645c9b60"

# Container App Configuration
containerapps_env_name = "infinityai-env"
container_app_name     = "infinityai-backend-eur"
container_image        = "ghcr.io/raghu-1718/infinityai:latest"

# Managed Identity and Key Vault
user_assigned_identity_name = "infinityai-uami"
key_vault_name             = "infinityai-kv-eur2024"  # Must be globally unique

# MySQL Database Configuration
mysql_server_name     = "infinityai-mysql-west-eur"
mysql_admin_username  = "infinityai_admin"
mysql_admin_password  = "InfinityAI@MySQL2024!SecurePass#123"  # Strong password for production
mysql_database_name   = "infinityai"

# Monitoring
log_analytics_name = "infinityai-law"
app_insights_name  = "infinityai-appi"

# Legacy DATABASE_URL (will be replaced by MySQL)
database_url_secret_name  = "database-url"
database_url_secret_value = ""  # Will be auto-generated from MySQL