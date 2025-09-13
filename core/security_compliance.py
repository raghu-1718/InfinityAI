# Security & Compliance Example
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException
from core.rbac import RBAC_MATRIX
import logging

# Encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data: str) -> bytes:
    return cipher_suite.encrypt(data.encode())

def decrypt_data(token: bytes) -> str:
    return cipher_suite.decrypt(token).decode()

# RBAC Decorator

def require_role(role):
    def decorator(user=Depends(...)):
        if user.role not in RBAC_MATRIX or role not in RBAC_MATRIX[user.role]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return decorator

# Audit Logging
logger = logging.getLogger("audit")

def log_audit(user, action, details):
    logger.info(f"AUDIT: {user.username} performed {action}: {details}")

# GDPR/CCPA Compliance
GDPR_RETENTION_DAYS = 365
# Add logic to purge logs and data older than retention period
