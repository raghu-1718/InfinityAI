import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Usage: get_secret('MY_SECRET_NAME')
def get_secret(secret_name):
    key_vault_url = os.getenv('KEY_VAULT_URL')
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value
