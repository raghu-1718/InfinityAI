# simple-container-app.tf
# Simplified Container App without Key Vault dependencies for immediate deployment

resource "azurerm_container_app" "infinityai_simple" {
  name                         = "infinityai-backend-simple"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  template {
    min_replicas = 0
    max_replicas = 10

    container {
      name   = "backend"
      image  = "nginx:latest"  # Using public image for testing
      cpu    = 0.5
      memory = "1.0Gi"

      env {
        name  = "DATABASE_URL"
        value = "mysql+pymysql://${var.mysql_admin_username}:${var.mysql_admin_password}@${azurerm_mysql_flexible_server.mysql.fqdn}:3306/${var.mysql_database_name}"
      }
      
      env {
        name  = "DB_HOST"
        value = azurerm_mysql_flexible_server.mysql.fqdn
      }
      
      env {
        name  = "DB_USER" 
        value = var.mysql_admin_username
      }
      
      env {
        name  = "DB_PASSWORD"
        value = var.mysql_admin_password
      }
      
      env {
        name  = "DB_NAME"
        value = var.mysql_database_name
      }
      
      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = azurerm_application_insights.appi.connection_string
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80  # nginx default port
    transport        = "auto"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = {
    Environment = "production"
    Project     = "infinityai"
    ManagedBy   = "terraform"
  }
}

output "simple_container_app_fqdn" {
  description = "FQDN of the simple Container App"
  value       = azurerm_container_app.infinityai_simple.latest_revision_fqdn
}