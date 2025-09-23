import os
from dotenv import load_dotenv
from shared.utils.logger import get_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import User, Base

# Load env from .env if present (no-op in production containers)
load_dotenv()

# Build a robust DATABASE_URL from DB_* envs when not explicitly provided
TESTING = os.getenv("TESTING") == "1"
if TESTING:
    DATABASE_URL = "sqlite:///./test.db"
else:
    # Prefer explicit DATABASE_URL if set
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        db_host = os.getenv("DB_HOST", "infinityai-prod-db.mysql.database.azure.com")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "infinityai")
        db_user = os.getenv("DB_USER", "user")
        db_pass = os.getenv("DB_PASSWORD", "")
        # Compose SQLAlchemy URL for PyMySQL driver
        DATABASE_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Connection arguments
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Keep connections fresh and fast-fail on dead connections
    connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
    connect_args["connect_timeout"] = connect_timeout

    # Azure MySQL typically requires SSL/TLS
    ssl_disabled = os.getenv("DB_SSL_DISABLED", "false").lower() == "true"
    ssl_ca = os.getenv("DB_SSL_CA", "").strip()
    if not ssl_disabled:
        # For PyMySQL, passing a non-empty 'ssl' dict enables TLS.
        # If a CA bundle is provided, enable certificate verification.
        if ssl_ca:
            connect_args["ssl"] = {"ca": ssl_ca}
        else:
            connect_args["ssl"] = {}  # Enable TLS without custom CA

# Create engine with sensible pool options
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Attempt to create tables; if DB is unavailable, this will be retried when called again
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # Don't crash import if DB is not reachable; login flow will handle errors
    logger = get_logger("usermanager")
    logger.warning(f"Skipping metadata.create_all due to DB error: {e}")

from typing import Optional, Dict, Any

def get_user_credentials(user_id: int) -> Optional[Dict[str, Any]]:
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    if user:
        return {
            "username": user.username,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "role": user.role,
            # Optional fields may not exist on dummy objects in tests
            "dhan_client_id": getattr(user, "dhan_client_id", None),
            "dhan_access_token": getattr(user, "dhan_access_token", None)
        }
    return None

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    if user:
        return {
            "username": user.username,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "role": user.role,
            "dhan_client_id": user.dhan_client_id,
            "dhan_access_token": user.dhan_access_token
        }
    return None
