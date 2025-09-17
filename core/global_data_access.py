# Global Data Access Example
# Multi-region deployment (Terraform)
# Save as infra/multi_region.tf
'''
resource "azurerm_container_app" "infinityai_backend_eu" {
  name                = "infinityai-backend-eu"
  resource_group_name = var.resource_group_eu
  location            = "westeurope"
  container {
    image = "infinityai-backend"
    cpu   = 1.0
    memory = "2.0Gi"
  }
}
resource "azurerm_container_app" "infinityai_backend_us" {
  name                = "infinityai-backend-us"
  resource_group_name = var.resource_group_us
  location            = "eastus"
  container {
    image = "infinityai-backend"
    cpu   = 1.0
    memory = "2.0Gi"
  }
}
'''

# API Gateway Example (FastAPI + Azure API Management)
# Configure Azure API Management to route requests to backend apps

# Caching Example (Redis)
import redis

redis_client = redis.Redis(host='www.infinityai.pro', port=6379, db=0)

def cache_set(key, value):
    redis_client.set(key, value)

def cache_get(key):
    return redis_client.get(key)

# Replication Example (Database)
# Use managed DB with geo-replication (Azure SQL, AWS Aurora, etc.)
