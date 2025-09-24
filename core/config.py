import os
from functools import lru_cache

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    TESTING = os.getenv("TESTING", "0") == "1"
    DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", "4000"))
    BROKER = os.getenv("BROKER", "MOCK").upper()
    DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")
    DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "")
    ANGEL_API_KEY = os.getenv("ANGEL_API_KEY", "")
    ANGEL_API_SECRET = os.getenv("ANGEL_API_SECRET", "")
    FIVEPAISA_APP_NAME = os.getenv("FIVEPAISA_APP_NAME", "")
    FIVEPAISA_CLIENT_CODE = os.getenv("FIVEPAISA_CLIENT_CODE", "")
    FIVEPAISA_PASSWORD = os.getenv("FIVEPAISA_PASSWORD", "")
    FIVEPAISA_ENCRYPTION_KEY = os.getenv("FIVEPAISA_ENCRYPTION_KEY", "")
    CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")
    OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    SHADOW_MODE = os.getenv("SHADOW_MODE", "0") == "1"

@lru_cache
def get_settings():
    return Settings()
