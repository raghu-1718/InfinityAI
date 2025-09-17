
import os
from dotenv import load_dotenv
from shared.utils.logger import get_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import User, Base

if os.getenv("TESTING") == "1":
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@www.infinityai.pro/infinityai_prod_db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_user_credentials(user_id):
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

def get_user_by_username(username):
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
