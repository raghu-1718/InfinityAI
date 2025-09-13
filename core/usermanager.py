
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import User, Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///infinityai.db")
engine = create_engine(DATABASE_URL)
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
            "role": user.role
        }
    return None
