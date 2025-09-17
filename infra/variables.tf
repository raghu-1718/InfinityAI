variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "tenant_id" {
  description = "Azure AD tenant ID"
  type        = string
}

variable "containerapps_env_name" {
  description = "Name for the Container Apps environment"
  type        = string
  default     = "infinityai-env"
}

variable "container_app_name" {
  description = "Name of the Container App"
  type        = string
  default     = "infinityai-backend-app"
}

variable "container_image" {
  description = "Container image to deploy (e.g., ghcr.io/owner/repo:tag)"
  type        = string
  default     = "ghcr.io/raghu-1718/infinityai:latest"
}

variable "user_assigned_identity_name" {
  description = "Name of the user assigned managed identity"
  type        = string
  default     = "infinityai-uami"
}

variable "key_vault_name" {
  description = "Name of the Azure Key Vault"
  type        = string
}

variable "database_url_secret_name" {
  description = "Name of the Key Vault secret for DATABASE_URL"
  type        = string
  default     = "database-url"
}

variable "database_url_secret_value" {
  description = "Value of the DATABASE_URL secret (use only for dev/testing; manage via pipeline in prod)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "log_analytics_name" {
  description = "Name of the Log Analytics Workspace"
  type        = string
  default     = "infinityai-law"
}

variable "app_insights_name" {
  description = "Name of the Application Insights resource"
  type        = string
  default     = "infinityai-appi"
}

variable "mysql_server_name" {
  description = "Name of the Azure Database for MySQL Flexible Server"
  type        = string
  default     = "infinityai-mysql"
}

variable "mysql_admin_username" {
  description = "Administrator username for the MySQL server"
  type        = string
  default     = "infinityai_admin"
}

variable "mysql_admin_password" {
  description = "Administrator password for the MySQL server"
  type        = string
  sensitive   = true
}

variable "mysql_database_name" {
  description = "Name of the MySQL database to create"
  type        = string
  default     = "infinityai"
}
