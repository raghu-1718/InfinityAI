
// Terraform configuration for Azure Container Apps with Managed Identity, Key Vault, and Application Insights
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.100.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "62fc147a-2efc-4494-be1f-faa521439799"
}

// Container Apps Environment
resource "azurerm_container_app_environment" "env" {
  name                         = var.containerapps_env_name
  resource_group_name          = var.resource_group_name
  location                     = var.location
  log_analytics_workspace_id   = azurerm_log_analytics_workspace.law.id
}

// Log Analytics Workspace for Container Apps diagnostics
resource "azurerm_log_analytics_workspace" "law" {
  name                = var.log_analytics_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

// Application Insights (Workspace-based)
resource "azurerm_application_insights" "appi" {
  name                = var.app_insights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.law.id
}

// User Assigned Managed Identity for Container App
resource "azurerm_user_assigned_identity" "uami" {
  location            = var.location
  name                = var.user_assigned_identity_name
  resource_group_name = var.resource_group_name
}

// Key Vault for secrets
resource "azurerm_key_vault" "kv" {
  name                        = var.key_vault_name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = var.tenant_id
  sku_name                    = "standard"
  purge_protection_enabled    = true
  soft_delete_retention_days  = 7
  public_network_access_enabled = true

  // Allow RBAC-based access (preferred)
  rbac_authorization_enabled = true
}

// Grant "Key Vault Secrets User" role to the UAMI at the Key Vault scope
data "azurerm_role_definition" "kv_secrets_user" {
  name = "Key Vault Secrets User"
  scope = azurerm_key_vault.kv.id
}

resource "azurerm_role_assignment" "uami_kv_secrets_user" {
  scope              = azurerm_key_vault.kv.id
  role_definition_id = data.azurerm_role_definition.kv_secrets_user.id
  principal_id       = azurerm_user_assigned_identity.uami.principal_id
}

// Grant "Key Vault Administrator" role to the current user for deployment
data "azurerm_client_config" "current" {}

data "azurerm_role_definition" "kv_administrator" {
  name = "Key Vault Administrator"
  scope = azurerm_key_vault.kv.id
}

resource "azurerm_role_assignment" "current_user_kv_admin" {
  scope              = azurerm_key_vault.kv.id
  role_definition_id = data.azurerm_role_definition.kv_administrator.id
  principal_id       = data.azurerm_client_config.current.object_id
}

// (Optional) Create an initial secret for DATABASE_URL for illustration
// In production, prefer setting secrets via pipeline or portal
resource "azurerm_key_vault_secret" "database_url" {
  name         = var.database_url_secret_name
  value        = var.database_url_secret_value
  key_vault_id = azurerm_key_vault.kv.id
  
  depends_on = [azurerm_role_assignment.current_user_kv_admin]
  
  lifecycle {
    ignore_changes = [value]
  }
}

// Azure Database for MySQL Flexible Server
resource "azurerm_mysql_flexible_server" "mysql" {
  name                   = var.mysql_server_name
  resource_group_name    = var.resource_group_name
  location               = var.location
  administrator_login    = var.mysql_admin_username
  administrator_password = var.mysql_admin_password
  backup_retention_days  = 7
  geo_redundant_backup_enabled = false
  sku_name               = "B_Standard_B1ms"  # Burstable tier for cost optimization
  version                = "8.0.21"
  # Remove zone specification to let Azure choose automatically
  
  storage {
    size_gb = 20
    iops    = 360
  }

  tags = {
    "azd-env-name" = var.resource_group_name
  }
}

// MySQL Flexible Server Configuration
resource "azurerm_mysql_flexible_server_configuration" "mysql_config" {
  name                = "require_secure_transport"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.mysql.name
  value               = "OFF"  # Allow non-SSL connections for Container Apps
}

// MySQL Database
resource "azurerm_mysql_flexible_database" "mysql_db" {
  name                = var.mysql_database_name
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.mysql.name
  charset             = "utf8mb4"
  collation           = "utf8mb4_unicode_ci"
}

// Firewall rule to allow Container Apps to access MySQL
resource "azurerm_mysql_flexible_server_firewall_rule" "allow_container_apps" {
  name                = "AllowContainerApps"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.mysql.name
  start_ip_address    = "0.0.0.0"  # Allow all IPs (restrict in production)
  end_ip_address      = "255.255.255.255"
}

// Store MySQL connection string in Key Vault
resource "azurerm_key_vault_secret" "mysql_connection_string" {
  name         = "mysql-connection-string"
  value        = "mysql+pymysql://${var.mysql_admin_username}:${var.mysql_admin_password}@${azurerm_mysql_flexible_server.mysql.fqdn}:3306/${var.mysql_database_name}?charset=utf8mb4"
  key_vault_id = azurerm_key_vault.kv.id
  
  depends_on = [
    azurerm_mysql_flexible_server.mysql,
    azurerm_mysql_flexible_database.mysql_db,
    azurerm_role_assignment.current_user_kv_admin
  ]
}

// Container App
resource "azurerm_container_app" "infinityai" {
  name                         = var.container_app_name
  resource_group_name          = var.resource_group_name
  container_app_environment_id = azurerm_container_app_environment.env.id
  revision_mode                = "Single"

  // Assign the user-managed identity to enable Key Vault secret reference
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.uami.id]
  }

  // App configuration: ingress
  ingress {
    external_enabled = true
    // FastAPI app listens on 8000
    target_port      = 8000
    
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    container {
      name   = "backend"
      // Image is deployed by GitHub Actions from GHCR; this value is a placeholder
      image  = var.container_image
      cpu    = 0.5
      memory = "1.0Gi"

      // Map secrets to environment variables
      env {
        name        = "DATABASE_URL"
        secret_name = var.database_url_secret_name
      }

      env {
        name        = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        secret_name = "appinsights-connection-string"
      }
    }
  }

  // Secrets (Key Vault reference requires identity)
  secret {
    name            = var.database_url_secret_name
    key_vault_secret_id = azurerm_key_vault_secret.database_url.id
    identity        = azurerm_user_assigned_identity.uami.id
  }

  // MySQL connection string from Key Vault
  secret {
    name            = "mysql-connection-string"
    key_vault_secret_id = azurerm_key_vault_secret.mysql_connection_string.id
    identity        = azurerm_user_assigned_identity.uami.id
  }

  // Provide App Insights connection string via secret
  secret {
    name  = "appinsights-connection-string"
    value = azurerm_application_insights.appi.connection_string
  }
}

output "container_app_fqdn" {
  value       = azurerm_container_app.infinityai.latest_revision_fqdn
  description = "Public FQDN of the Container App"
}

output "mysql_server_fqdn" {
  value       = azurerm_mysql_flexible_server.mysql.fqdn
  description = "Fully Qualified Domain Name of the MySQL Flexible Server"
}

output "mysql_connection_string" {
  value       = "mysql+pymysql://${var.mysql_admin_username}:<password>@${azurerm_mysql_flexible_server.mysql.fqdn}:3306/${var.mysql_database_name}?charset=utf8mb4"
  description = "MySQL connection string template (replace <password> with actual password)"
  sensitive   = false
}
