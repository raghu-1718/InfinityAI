
# Terraform configuration for Azure Container App
provider "azurerm" {
  features {}
}
resource "azurerm_container_app_environment" "env" {
  name                = "infinityai-env"
  resource_group_name = var.resource_group_name
  location            = var.location
}
resource "azurerm_container_app" "infinityai" {
  name                = "infinityai-backend-app"
  resource_group_name = var.resource_group_name
  location            = var.location
  container_app_environment_id = azurerm_container_app_environment.env.id
  configuration {
    ingress {
      external_enabled = true
      target_port      = 80
    }
  }
  template {
    container {
      name   = "backend"
      image  = "infinityai-backend:latest"
      cpu    = 0.5
      memory = "1.0Gi"
      env {
        name  = "KEY_VAULT_URL"
        value = var.key_vault_url
      }
    }
  }
}
