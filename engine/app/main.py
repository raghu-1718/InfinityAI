from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.hash import bcrypt
import os

# Import shared utilities
from shared.utils.database import db
from shared.utils.logger import configure_logging

# Configure logging
logger = configure_logging(app_name="infinityai-backend", log_level="INFO")

# Create FastAPI application
app = FastAPI(
    title="InfinityAI Trading API",
    description="Trading API for InfinityAI.Pro",
    version="1.0.0"
)

# CORS configuration using env var CORS_ALLOW_ORIGINS (comma-separated)
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "https://www.infinityai.pro")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Container App probe
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint for Azure Container App health probe.
    Returns status and basic diagnostics including database connectivity check.
    """
    try:
        # Test database connectivity
        db_status = "connected" if db.test_connection() else "disconnected"

        # Log health check
        logger.info("Health check performed successfully")

        return {
            "status": "healthy",
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

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/login", tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    from core.usermanager import get_user_by_username
    user = get_user_by_username(form_data.username)

    if not user or not bcrypt.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/test", tags=["Test"])
async def test_endpoint():
    return {"message": "Test endpoint working"}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting InfinityAI Trading API")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down InfinityAI Trading API")
