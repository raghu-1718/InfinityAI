# Example Terraform for Azure Container App
resource "azurerm_container_app" "infinityai_backend" {
  name                = "infinityai-backend-app"
  resource_group_name = var.resource_group_name
  location            = var.location
  container {
    image = "infinityai-backend"
    cpu   = 1.0
    memory = "2.0Gi"
    env {
      name  = "KEY_VAULT_URL"
      value = var.key_vault_url
    }
  }
}
