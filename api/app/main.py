# --- FastAPI & Flask-Limiter Integration ---
from fastapi import FastAPI, Depends, HTTPException
from .auth import app as auth_app
from core.rbac import RBAC_MATRIX
from core.secrets import get_secret

from starlette.middleware.wsgi import WSGIMiddleware
import sys
sys.path.append("./api/app")
from rate_limit_config import app as flask_limiter_app

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

# Mount Flask-Limiter for rate limiting (production)
app.mount("/flask-rate-limit", WSGIMiddleware(flask_limiter_app))

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://www.infinityai.pro"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
