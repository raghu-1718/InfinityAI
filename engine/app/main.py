from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.hash import bcrypt
import os
import threading

# Import shared utilities
from shared.utils.database import db
from shared.utils.logger import configure_logging

# Configure logging
logger = configure_logging(app_name="infinityai-backend", log_level="INFO")

# Create FastAPI application
app: FastAPI = FastAPI(
    title="InfinityAI Trading API",
    description="Trading API for InfinityAI.Pro",
    version="1.0.0"
)

# CORS configuration using env var CORS_ALLOW_ORIGINS (comma-separated)
# Default allows both the frontend (www) and backend (api) subdomains in production.
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "https://infinityai.pro,https://www.infinityai.pro,https://api.infinityai.pro")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple root route for smoke tests


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "infinityai-backend-app", "docs": "/docs", "health": "/health"}


#
# Health check endpoint for Container App probe
#

@app.get("/health", tags=["Monitoring"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for Azure Container App health probe.
    Returns status and basic diagnostics including database connectivity check.
    """
    try:
        # Perform DB check with a short timeout to avoid long probe waits
        timeout_seconds = float(os.getenv("HEALTH_DB_TIMEOUT", "3"))
        result = {"db": "unknown"}

        def _check_db() -> None:
            try:
                result["db"] = "connected" if db.test_connection() else "disconnected"
            except Exception:
                result["db"] = "error"

        t = threading.Thread(target=_check_db, daemon=True)
        t.start()
        t.join(timeout_seconds)
        db_status = result["db"] if not t.is_alive() else "timeout"

        # Overall status degrades if DB is not connected, but endpoint remains fast
        overall = "healthy" if db_status == "connected" else "degraded"

        logger.info("Health check performed", extra={"custom_fields": {"database": db_status}})
        return {
            "status": overall,
            "database": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "service": "infinityai-backend-app"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Import existing routes and functionality from engine/app implementation
# [Your existing routes and functionality here]

# Import any unique routes from api/routes

# Import and add trade and webhook routes
# Import and add AI/ML router
# from api.routes import webhook, trade, ai
# app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
# app.include_router(trade.router, prefix="/trade", tags=["Trade"])
# app.include_router(ai.router, prefix="/ai", tags=["AI/ML"])

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/ready", tags=["Monitoring"])
async def readiness() -> dict[str, str]:
    """Simple readiness endpoint that does not touch external deps."""
    return {"status": "ready", "service": "infinityai-backend-app"}


@app.post("/login", tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    from core.usermanager import get_user_by_username
    user = None
    try:
        user = get_user_by_username(form_data.username)
    except Exception as e:
        # DB may be unavailable; allow optional admin fallback below
        logger.warning(f"DB lookup failed in login: {e}")

    subject: Optional[str] = None
    if user:
        if not bcrypt.verify(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        subject = user["username"]
    else:
        allow_fallback = os.getenv("ALLOW_FALLBACK_LOGIN", "false").lower() == "true"
        admin_user = os.getenv("ADMIN_USERNAME")
        admin_hash = os.getenv("ADMIN_PASSWORD_HASH")
        admin_plain = os.getenv("ADMIN_PASSWORD")
        allow_plain = os.getenv("ADMIN_ALLOW_PLAINTEXT", "false").lower() == "true"

        if allow_fallback and admin_user and form_data.username == admin_user:
            verified = False
            if admin_hash:
                try:
                    verified = bcrypt.verify(form_data.password, admin_hash)
                except Exception:
                    verified = False
            elif allow_plain and admin_plain is not None:
                verified = (form_data.password == admin_plain)

            if not verified:
                raise HTTPException(status_code=400, detail="Incorrect username or password")
            subject = admin_user

    if not subject:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": subject}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/test", tags=["Test"])
async def test_endpoint() -> dict[str, str]:
    return {"message": "Test endpoint working"}

# Startup and shutdown events


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting InfinityAI Trading API")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down InfinityAI Trading API")
