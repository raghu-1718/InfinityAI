"""FastAPI app composition and integrations (WSGI, CORS, RBAC)."""

# --- FastAPI & Flask-Limiter Integration ---
from typing import Any, Callable

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware

from core.rbac import RBAC_MATRIX

# Local package imports
try:
    from .auth import app as auth_app
except Exception:
    auth_app = FastAPI()

from .ws import app as ws_app
from .rate_limit_config import app as flask_limiter_app


app = auth_app


def get_current_user() -> Any:
    """Placeholder dependency that should extract the current user from auth context."""
    class _User:
        role: str = "user"

    return _User()


def require_role(role: str) -> Callable[[Any], Any]:
    def decorator(user: Any = Depends(get_current_user)):
        if user.role not in RBAC_MATRIX or role not in RBAC_MATRIX[user.role]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return decorator


# WebSocket endpoint for market data
app.mount("/ws", ws_app)

# Mount Flask-Limiter for rate limiting (production)
app.mount("/flask-rate-limit", WSGIMiddleware(flask_limiter_app))


origins = [
    "https://www.infinityai.pro",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
