
from fastapi import FastAPI, Depends, HTTPException
from .auth import app as auth_app
from core.rbac import RBAC_MATRIX
from core.secrets import get_secret

app = auth_app

def require_role(role):
	def decorator(user=Depends(...)):
		if user.role not in RBAC_MATRIX or role not in RBAC_MATRIX[user.role]:
			raise HTTPException(status_code=403, detail="Forbidden")
		return user
	return decorator


import logging
from core.audit_logging import log_request


from .ws import app as ws_app
# WebSocket endpoint for market data
app.mount("/ws", ws_app)
